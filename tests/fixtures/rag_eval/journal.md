An append-only JSONL journal records ordered task events and hashes.
Replay checks sequence numbers and hash-chain integrity after restart.
A truncated final record is discarded before the next append.
