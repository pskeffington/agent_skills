#!/usr/bin/env python3
"""Generate a skill skeleton from the repository master template."""
import argparse
import pathlib
import re
import sys
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = pathlib.Path(__file__).resolve().parents[1]
MARKER = re.compile(r"\{\{([a-z_]+)\}\}")

def scaffold(name, description, destination, overwrite=False):
    if not NAME.fullmatch(name):
        raise ValueError("Skill name must be lowercase and hyphenated")
    if len(description.strip()) < 40 or "\n" in description:
        raise ValueError("Description must be >=40 characters and single-line")
    destination = pathlib.Path(destination)
    if destination.name != name:
        raise ValueError("Destination directory must match the skill name")
    if destination.exists() and any(destination.iterdir()) and not overwrite:
        raise FileExistsError("Destination is not empty; refusing overwrite")
    display = name.replace("-", " ").title()
    fields = {
        "skill_name": name,
        "capability_and_positive_triggers_with_negative_boundary": description.strip(),
        "human_readable_skill_name": display,
        "one_sentence_success_definition": "Produce a validated result for the requested task.",
        "inputs": "Specify required input types before release.",
        "optional_inputs": "Any task-specific context.",
        "tools_or_none": "List the necessary tools before release.",
        "critical_operation_one": "Apply the task-specific procedure.",
        "critical_operation_two": "Check preconditions, error states, and output.",
        "precise_deliverables_and_format": "Specify the output contract before release.",
        "out_of_scope_cases": "Specify out-of-scope requests before release.",
        "fallback_or_stop": "Report the missing dependency and stop safely.",
        "reference_links_only_if_used": "Add relevant local references before release.",
        "display_name": display,
        "short_description": "Validate and execute " + display.lower() + " tasks",
        "example_invocation": "Use " + display + " on the supplied input.",
    }
    def render(template):
        text = pathlib.Path(template).read_text(encoding="utf-8")
        return MARKER.sub(lambda m: fields[m.group(1)], text)
    entry = destination / "SKILL.md"
    metadata = destination / "agents" / "openai.yaml"
    destination.mkdir(parents=True, exist_ok=True)
    metadata.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text(render(ROOT / "templates/ai-skill-master/SKILL.md.tmpl"), encoding="utf-8")
    metadata.write_text(render(ROOT / "templates/ai-skill-master/agents/openai.yaml.tmpl"), encoding="utf-8")
    return destination

def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("--description", required=True)
    p.add_argument("--path", default="skills", help="Parent output directory")
    args = p.parse_args()
    try:
        target = pathlib.Path(args.path) / args.name
        scaffold(args.name, args.description, target)
    except (ValueError, FileExistsError, KeyError) as exc:
        p.error(str(exc))
    print("Created draft skill:", target)
    print("Complete the task-specific instructions and behavioral evaluations before release.")
    return 0
if __name__ == "__main__":
    sys.exit(main())
