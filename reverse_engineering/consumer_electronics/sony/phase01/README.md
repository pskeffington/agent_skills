# SONY Phase 01: ADB read-only collector

No live hardware was contacted during implementation. Python standard library only. This tool uses explicit target identifiers, no port scans or ADB pairing automation. Device must be physically confirmed and authorize debugging on its own screen.

## Test
```sh
cd reverse_engineering/consumer_electronics/sony/phase01
python3 -m unittest -v test_collector.py
```

## Collect (only after approving debugging on owned TV)
```sh
python3 collector.py --serial emulator-5554 --output inventory.private.json
```
Replace emulator-5554 with a **verified** authorized ADB serial obtained by `adb devices -l`. This example is illustrative, not the Sony TV's identifier. Treat output as private and keep it out of git. Review the model, OS, patch and packages before changing anything.

Never disable packages in Phase 01. Failures are recorded as typed errors without leaking stderr or device identifiers. The collector does not acquire serial numbers, MAC addresses, account identifiers, location data or network configuration. Mark identity as confirmed only through separate manual verification.

Next: Phase 02 launcher MVP on an emulator, retaining the stock launcher.
