from __future__ import annotations

import hashlib
import os
import random
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / "data" / "activity.log"


def stable_int(text: str) -> int:
    """Return a deterministic integer derived from text."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def selected_slots_for_day(day: str) -> set[int]:
    """
    Pick a daily target: 0 with probability 1/7, 1..8 with probability 4/7,
    or 9..12 with probability 2/7. Then choose that many of the 12 two-hour
    slots for the day.

    The selection is deterministic for a given day, so rerunning the same
    workflow slot will not unpredictably change the day's plan.
    """
    group = stable_int(f"target-group:{day}") % 7
    if group == 0:
        target = 0
    elif group < 5:
        target = 1 + stable_int(f"target-count:{day}") % 8
    else:
        target = 9 + stable_int(f"target-count:{day}") % 4

    rng = random.Random(stable_int(f"slots:{day}"))
    slots = list(range(12))
    rng.shuffle(slots)
    return set(slots[:target])


def current_slot(now: datetime) -> int:
    """Map the current UTC hour into one of 12 two-hour slots."""
    return now.hour // 2


def already_recorded(day: str, slot: int) -> bool:
    if not LOG_FILE.exists():
        return False

    needle = f"{day} slot={slot:02d} "
    return any(line.startswith(needle) for line in LOG_FILE.read_text().splitlines())


def append_activity(now: datetime, slot: int) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = now.isoformat(timespec="seconds")
    nonce = hashlib.sha256(
        f"{stamp}:{os.urandom(16).hex()}".encode("utf-8")
    ).hexdigest()[:16]

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(
            f"{now.date().isoformat()} slot={slot:02d} "
            f"timestamp={stamp} nonce={nonce}\n"
        )


def main() -> int:
    now = datetime.now(timezone.utc)
    day = now.date().isoformat()
    slot = current_slot(now)
    selected = selected_slots_for_day(day)

    print(f"UTC date: {day}")
    print(f"Current two-hour slot: {slot}")
    print(f"Selected slots today: {sorted(selected)}")
    print(f"Daily target: {len(selected)}")

    if slot not in selected:
        print("No contribution scheduled for this slot.")
        return 0

    if already_recorded(day, slot):
        print("This slot was already recorded. Nothing to do.")
        return 0

    append_activity(now, slot)
    print("Contribution file updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
