import json
import requests
import os
from datetime import datetime

LEAGUES_FILE = "leagues.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)'
}

OUTPUT_FILE = "matchdays.json"


def fetch_matchdays(comp_id, season_id):
    url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        data = r.json()
        matchdays = data.get("matchdays", [])

        current_index = None

        for i, md in enumerate(matchdays):
            if md.get("isCurrentMatchday"):
                current_index = i
                break

        if current_index is None:
            return None

        previous_md = matchdays[current_index - 1] if current_index - 1 >= 0 else None
        current_md = matchdays[current_index]
        next_md = matchdays[current_index + 1] if current_index + 1 < len(matchdays) else None

        return {
            "previous": str(previous_md["id"]) if previous_md else None,
            "current": str(current_md["id"]),
            "next": str(next_md["id"]) if next_md else None
        }

    except Exception as e:
        print("ERROR:", e)
        return None


def build():
    # =========================
    # LOAD LEAGUES
    # =========================
    with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
        leagues = json.load(f)

    database = {}

    print("\n🚀 BUILD START\n")

    for league in leagues:
        key = league["name"].lower().replace(" ", "_")

        print("⚽", league["name"])

        md = fetch_matchdays(league["id"], league["s"])

        if not md:
            print("   ❌ SKIP")
            continue

        database[key] = {
            "name": league["name"],
            "competition_id": league["id"],
            "season_id": league["s"],
            "matchdays": md
        }

        print("   ✔", md)

    # =========================
    # ALWAYS WRITE FILE (OVERWRITE SAFE)
    # =========================

    # 🔥 ključni FIX — file uvijek postoji
    if not os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, "w", encoding="utf-8").write("{}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)

    print("\n🏁 DONE → file written / overwritten safely")
    print("📦 Exists:", os.path.exists(OUTPUT_FILE))


if __name__ == "__main__":
    build()
