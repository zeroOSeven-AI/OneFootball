import json
import requests
from datetime import datetime

# ==================================================
# MATCHDAY GENERATOR (CLEAN GITHUB VERSION)
# ==================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

LEAGUES_URL = "https://raw.githubusercontent.com/zeroOSeven-AI/OneFootball/main/leagues.json"
OUTPUT_FILE = "matchdays.json"


def load_leagues():
    r = requests.get(LEAGUES_URL, timeout=15)
    r.raise_for_status()
    return r.json()


def load_existing():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def get_matchdays(comp_id, season_id):

    url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"

    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    data = r.json()
    matchdays = data.get("matchdays", [])

    if not matchdays:
        return None

    current_index = next(
        (i for i, m in enumerate(matchdays) if m.get("isCurrentMatchday")),
        -1
    )

    if current_index == -1:
        return None

    prev_id = matchdays[current_index - 1]["id"] if current_index > 0 else None
    curr_id = matchdays[current_index]["id"]
    next_id = matchdays[current_index + 1]["id"] if current_index < len(matchdays) - 1 else None

    return {
        "previous": prev_id,
        "current": curr_id,
        "next": next_id
    }


def build():

    leagues = load_leagues()
    db = load_existing()

    now = datetime.now()
    weekday = now.weekday()

    print(f"⏰ Weekday: {weekday}")
    print("🚀 Starting generation...\n")

    updated = 0

    for league in leagues:

        if weekday not in league.get("days_active", [0,1,2,3,4,5,6]):
            print(f"💤 Skipping {league['name']} (inactive day)")
            continue

        comp_id = league["id"]
        season_id = league["s"]

        print(f"⚽ {league['name']}")

        try:
            md = get_matchdays(comp_id, season_id)

            if not md:
                print("   ❌ No matchday data")
                continue

            key = league["name"].lower().replace(" ", "_")

            db[key] = {
                "name": league["name"],
                "competition_id": comp_id,
                "season_id": season_id,

                "previous_matchday_id": md["previous"],
                "current_matchday_id": md["current"],
                "next_matchday_id": md["next"],

                "previous_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{md['previous']}"
                    if md["previous"] else None,

                "current_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{md['current']}",

                "next_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{md['next']}"
                    if md["next"] else None
            }

            print(f"   ✅ PREV {md['previous']} | CUR {md['current']} | NEXT {md['next']}")
            updated += 1

        except Exception as e:
            print(f"   ❌ ERROR: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    print("\n====================")
    print(f"DONE: {updated} leagues updated")
    print("====================")


if __name__ == "__main__":
    build()
