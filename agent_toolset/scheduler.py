"""Deterministic task DAG scheduling, file-scope leases, and bounded retries."""
from __future__ import annotations

import hashlib
import pathlib
import re
import time
from typing import Any, Callable, Iterable

from .contracts import validate_task
from .journal import Journal

TERMINAL={"done","failed","cancelled"}
TRANSITIONS={
    "queued":{"ready","blocked","cancelled"},
    "ready":{"running","blocked","cancelled"},
    "running":{"review","blocked","failed","cancelled"},
    "review":{"done","ready","blocked","failed"},
    "blocked":{"ready","cancelled"},
    "failed":set(),"done":set(),"cancelled":set(),
}

class ScheduleError(ValueError):
    """The task graph, lease, or requested transition is invalid."""


def _scope_conflicts(left: list[str], right: list[str]) -> bool:
    """Conservatively reject paths that may name overlapping writer resources."""
    for a in left:
        for b in right:
            if a==b or a.startswith(b.rstrip("/")+"/") or b.startswith(a.rstrip("/")+"/"):
                return True
            if any(ch in a+b for ch in "*?["):
                def fixed_prefix(value):
                    match=re.search(r"[*?\[]",value)
                    return value[:match.start()] if match else value
                ap,bp=fixed_prefix(a),fixed_prefix(b)
                if not ap or not bp or ap.startswith(bp) or bp.startswith(ap):
                    return True
    return False


class Scheduler:
    def __init__(self,journal:Journal,*,lease_seconds:int=300,max_retries:int=3):
        if lease_seconds<=0 or max_retries<0:
            raise ValueError("lease_seconds must be positive and max_retries non-negative")
        self.journal=journal
        self.lease_seconds=lease_seconds
        self.max_retries=max_retries

    def _state(self)->tuple[dict[str,dict[str,Any]],dict[str,dict[str,Any]]]:
        tasks={}; leases={}
        for event in self.journal.replay():
            typ,payload,task_id=event["event_type"],event["payload"],event["task_id"]
            if typ=="TASK_CREATED": tasks[task_id]=payload["task"]
            elif typ=="TASK_STATE": tasks[task_id]={**tasks[task_id],"status":payload["status"],"blocker":payload.get("blocker")}
            elif typ in {"LEASE_ACQUIRED","LEASE_RECLAIMED"}: leases[task_id]=payload
            elif typ in {"LEASE_RELEASED","TASK_CANCELLED"}: leases.pop(task_id,None)
        return tasks,leases

    def add_tasks(self,contracts:Iterable[dict[str,Any]],*,roles:set[str]|None=None)->list[str]:
        with self.journal.transaction() as tx:
            tasks,_=self._state(); proposed=dict(tasks); added=[]
            for raw in contracts:
                task=validate_task(raw,roles=roles); task_id=task["task_id"]
                if task_id in proposed: raise ScheduleError(f"duplicate task_id: {task_id}")
                proposed[task_id]=task; added.append(task_id)
            self._validate_graph(proposed)
            for task_id in added: tx.append(task_id,"TASK_CREATED",{"task":proposed[task_id]})
            return added

    @staticmethod
    def _validate_graph(tasks:dict[str,dict[str,Any]])->None:
        for task_id,task in tasks.items():
            for dependency in task.get("depends_on",[]):
                if dependency not in tasks: raise ScheduleError(f"{task_id} depends on unknown task {dependency}")
        visiting=set(); visited=set()
        def visit(node):
            if node in visiting: raise ScheduleError(f"dependency cycle at {node}")
            if node in visited: return
            visiting.add(node)
            for dependency in tasks[node].get("depends_on",[]): visit(dependency)
            visiting.remove(node); visited.add(node)
        for node in tasks: visit(node)

    def plan(self)->list[str]:
        tasks,_=self._state()
        self._validate_graph(tasks)
        return sorted(task_id for task_id,task in tasks.items() if task["status"] in {"queued","ready"} and all(tasks[d]["status"]=="done" for d in task.get("depends_on",[])))

    def status(self)->dict[str,Any]:
        tasks,leases=self._state()
        return {"tasks":tasks,"leases":leases,"ready":self.plan()}

    def _check_transition(self,tasks,task_id,new_status,blocker):
        if task_id not in tasks: raise ScheduleError(f"unknown task: {task_id}")
        current=tasks[task_id]["status"]
        if new_status not in TRANSITIONS.get(current,set()): raise ScheduleError(f"invalid transition {current} -> {new_status}")
        if new_status=="ready" and any(tasks[d]["status"]!="done" for d in tasks[task_id].get("depends_on",[])):
            raise ScheduleError("task dependencies are not complete")
        if new_status=="blocked" and not blocker: raise ScheduleError("blocked transition requires a documented blocker")
        if new_status!="blocked" and blocker is not None: raise ScheduleError("blocker is only valid for blocked status")

    def transition(self,task_id:str,new_status:str,*,blocker:str|None=None,owner:str|None=None,lease_token:str|None=None,now:float|None=None)->None:
        now=time.time() if now is None else now
        with self.journal.transaction() as tx:
            tasks,leases=self._state(); self._check_transition(tasks,task_id,new_status,blocker)
            if tasks[task_id]["status"]=="running":
                lease=leases.get(task_id)
                if not lease or lease["owner"]!=owner or lease["token"]!=lease_token or lease["expires_at"]<=now:
                    raise ScheduleError("running task transition requires its current, unexpired lease")
            tx.append(task_id,"TASK_STATE",{"status":new_status,"blocker":blocker})

    def _new_lease(self,task_id,owner,worktree,now,journal_sequence):
        token=hashlib.sha256(f"{task_id}:{owner}:{now}:{journal_sequence}".encode()).hexdigest()
        return {"owner":owner,"worktree":worktree,"acquired_at":now,"expires_at":now+self.lease_seconds,"token":token}

    def _assert_scope_available(self,tasks,leases,task_id):
        requested=tasks[task_id]["scope"]["include"]
        for other_id in leases:
            if other_id==task_id: continue
            if _scope_conflicts(requested,tasks[other_id]["scope"]["include"]):
                raise ScheduleError(f"writer scope overlaps active lease for task {other_id}")

    def _acquire_locked(self,tx,tasks,leases,task_id,owner,worktree,now):
        if not isinstance(owner,str) or not owner.strip(): raise ScheduleError("lease owner must be non-empty")
        if task_id not in tasks or any(tasks[d]["status"]!="done" for d in tasks[task_id].get("depends_on",[])):
            raise ScheduleError("task is unknown or dependencies are not complete")
        if tasks[task_id]["status"] not in {"queued","ready","running"}:
            raise ScheduleError("task is not in a schedulable state")
        current=leases.get(task_id)
        if current:
            if current["expires_at"]>now: raise ScheduleError(f"task already leased by {current['owner']}")
            raise ScheduleError("expired lease requires verified worker inactivity before reclamation")
        self._assert_scope_available(tasks,leases,task_id)
        lease=self._new_lease(task_id,owner,worktree,now,len(self.journal.replay()))
        tx.append(task_id,"LEASE_ACQUIRED",lease)
        if tasks[task_id]["status"]=="queued":
            tx.append(task_id,"TASK_STATE",{"status":"ready","blocker":None})
            tasks[task_id]={**tasks[task_id],"status":"ready"}
        if tasks[task_id]["status"]=="ready":
            tx.append(task_id,"TASK_STATE",{"status":"running","blocker":None})
        return lease

    def acquire(self,task_id:str,owner:str,*,now:float|None=None,worktree:str="")->dict[str,Any]:
        now=time.time() if now is None else now
        with self.journal.transaction() as tx:
            tasks,leases=self._state()
            return self._acquire_locked(tx,tasks,leases,task_id,owner,worktree,now)

    def reclaim_expired(self,task_id:str,owner:str,reason:str,*,process_check:Callable[[dict[str,Any]],bool|None],now:float|None=None,worktree:str="")->dict[str,Any]:
        """Reclaim only after the execution adapter confirms the old writer is inactive."""
        now=time.time() if now is None else now
        if not reason.strip() or not callable(process_check): raise ScheduleError("recovery reason and process check are required")
        with self.journal.transaction() as tx:
            tasks,leases=self._state(); lease=leases.get(task_id)
            if not lease: raise ScheduleError("no lease exists to reclaim")
            if lease["expires_at"]>now: raise ScheduleError("lease has not expired")
            inactive=process_check(dict(lease))
            if inactive is not True: raise ScheduleError("worker inactivity was not verified")
            self._assert_scope_available(tasks,leases,task_id)
            tx.append(task_id,"LEASE_RELEASED",{"owner":lease["owner"],"token":lease["token"],"recovery_reason":reason,"verified_inactive":True})
            leases.pop(task_id,None)
            new_lease=self._new_lease(task_id,owner,worktree,now,len(self.journal.replay()))
            tx.append(task_id,"LEASE_ACQUIRED",new_lease)
            return new_lease

    def release(self,task_id:str,owner:str,token:str)->None:
        with self.journal.transaction() as tx:
            _,leases=self._state(); lease=leases.get(task_id)
            if not lease or lease["owner"]!=owner or lease["token"]!=token: raise ScheduleError("lease owner or token mismatch")
            tx.append(task_id,"LEASE_RELEASED",{"owner":owner,"token":token})

    def cancel(self,task_id:str,reason:str,*,process_check:Callable[[dict[str,Any]],bool|None]|None=None)->None:
        if not isinstance(reason,str) or not reason.strip(): raise ScheduleError("cancellation requires a reason")
        with self.journal.transaction() as tx:
            tasks,leases=self._state(); self._check_transition(tasks,task_id,"cancelled",None)
            lease=leases.get(task_id)
            if lease:
                if not callable(process_check) or process_check(dict(lease)) is not True:
                    raise ScheduleError("cancelling a leased task requires verified worker inactivity")
                tx.append(task_id,"LEASE_RELEASED",{"owner":lease["owner"],"token":lease["token"],"cancellation_reason":reason,"verified_inactive":True})
            tx.append(task_id,"TASK_STATE",{"status":"cancelled","blocker":None})
            tx.append(task_id,"TASK_CANCELLED",{"reason":reason})

    def retry(self,task_id:str,root_cause:str)->int:
        if not isinstance(root_cause,str) or not root_cause.strip(): raise ScheduleError("retry requires a root cause")
        with self.journal.transaction() as tx:
            events=self.journal.replay()
            if not any(event["task_id"]==task_id and event["event_type"]=="TASK_CREATED" for event in events): raise ScheduleError(f"unknown task: {task_id}")
            count=sum(1 for event in events if event["task_id"]==task_id and event["event_type"]=="RETRY" and event["payload"].get("root_cause")==root_cause)
            if count>=self.max_retries: raise ScheduleError(f"retry budget exhausted for root cause: {root_cause}")
            next_count=count+1; tx.append(task_id,"RETRY",{"root_cause":root_cause,"attempt":next_count})
            return next_count
