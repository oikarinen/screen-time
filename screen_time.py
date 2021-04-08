import datetime
from collections import defaultdict

from systemd import journal


def collect_entries():
    """Collect screen time entries from journal"""
    j = journal.Reader()
    j.log_level(journal.LOG_INFO)
    j.add_match(UNIT="sleep.target")
    results = defaultdict(list)
    start = None
    for entry in j:
        ts = entry["_SOURCE_REALTIME_TIMESTAMP"]
        date = ts.date()
        if ts.time() < datetime.time(hour=5):
            date = date - datetime.timedelta(days=1)
        if entry["JOB_TYPE"] == "stop":
            start = ts
        elif entry["JOB_TYPE"] == "start":
            if not start or start.date() != date:
                print(f"ERROR: no start for stop: {ts}")
                continue
            duration = ts - start
            entry = {
                "start": start,
                "end": ts,
                "duration": duration.total_seconds() / (60 * 60),
            }
            results[date].append(entry)
            start = None
    return results


def report_screen_time(entries):
    """Report screen time per day and total"""
    for date in entries:
        entry = entries[date]
        for item in entry:
            print("  {}-{}: {}".format(
                item["start"].time().isoformat(timespec="minutes"),
                item["end"].time().isoformat(timespec="minutes"),
                round(item["duration"], 2))
            )
        total = sum([item["duration"] for item in entry])
        print(f"{date}: {round(total, 2)}")


def main():
    entries = collect_entries()
    report_screen_time(entries)


if __name__ == "__main__":
    main()
