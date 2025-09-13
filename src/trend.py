import json
from datetime import datetime
from collections import Counter
from pathlib import Path

TRENDS_FILE = Path("trends.json")

def save_trend(issues):
    # Count severities
    sev_counts = Counter([i.severity for i in issues])
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "High": sev_counts.get("High", 0),
        "Medium": sev_counts.get("Medium", 0),
        "Low": sev_counts.get("Low", 0)
    }
    # Append to trends file
    trends = []
    if TRENDS_FILE.exists():
        with open(TRENDS_FILE, "r", encoding="utf-8") as f:
            trends = json.load(f)
    trends.append(record)
    with open(TRENDS_FILE, "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2)

def load_last_two_trends():
    if not TRENDS_FILE.exists():
        return []
    with open(TRENDS_FILE, "r", encoding="utf-8") as f:
        trends = json.load(f)
    return trends[-2:] if len(trends) >= 2 else trends

def print_trend():
    trends = load_last_two_trends()
    if len(trends) < 2:
        print("Not enough trend data to compare.")
        return
    prev, latest = trends[-2], trends[-1]
    print("📊 Issue Trend Comparison")
    print(f"Previous: {prev['timestamp']} → High={prev['High']}, Medium={prev['Medium']}, Low={prev['Low']}")
    print(f"Latest:   {latest['timestamp']} → High={latest['High']}, Medium={latest['Medium']}, Low={latest['Low']}\n")
    print("🔎 Severity Changes:")
    for sev in ["High", "Medium", "Low"]:
        diff = latest[sev] - prev[sev]
        if diff == 0:
            status = "no change"
        elif diff < 0:
            status = "improved"
        else:
            status = "more issues"
        print(f"  {sev}: {diff:+d} ({status})")