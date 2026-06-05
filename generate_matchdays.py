import json
import requests
from datetime import datetime
from pathlib import Path

# ==================================================
# PATH SETUP (FIX ZA GITHUB ACTIONS)
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
LEAGUES_FILE = BASE_DIR / "leagues.json"
MATCHDAYS_FILE = BASE_DIR / "matchdays.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

# ==================================================
# LOAD LEAGUES
# ==================================================
def load_leagues():
    if not LEAGUES_FILE.exists():
        raise FileNotFoundError(f"leagues.json NOT FOUND in {BASE_DIR}")

    with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==================================================
# LOAD EXISTING DATABASE (SAFE)
# ==================================================
def load_database():
    if not MATCHDAYS_FILE.exists():
        return {}

    try:
        with open(MATCHDAYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ==================================================
# SAVE JSON SAFELY (ATOMIC WRITE)
# ==================================================
def save_database(data):
    temp_file = MATCHDAYS_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    temp_file.replace(MATCHDAYS_FILE)

# ==================================================
# MAIN BUILDER
# ==================================================
def build():
    database = load_database()
    leagues = load_leagues()

    now = datetime.now()
    today = now.weekday()
    hour = now.hour

    print(f"⏰ Server time: day={today}, hour={hour}")

    for league in leagues:
        name_key = league["name"].lower().replace(" ", "_")

        active_days = league.get("days_active", [0,1,2,3,4,5,6])

        # ==================================================
        # DAY FILTER (ANTI API SPAM)
        # ==================================================
        if today not in active_days:
            print(f"💤 {league['name']} skipped (inactive day)")
            continue

        comp_id = league["id"]
        season_id = league["s"]

        url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"

        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"❌ {league['name']} API error {res.status_code}")
                continue

            data = res.json()
            matchdays = data.get("matchdays", [])

            if not matchdays:
                print(f"⚠️ No matchdays for {league['name']}")
                continue

            current_idx = next(
                (i for i, m in enumerate(matchdays) if m.get("isCurrentMatchday")),
                None
            )

            if current_idx is None:
                print(f"⚠️ No current matchday found for {league['name']}")
                continue

            prev_md = matchdays[current_idx - 1] if current_idx - 1 >= 0 else None
            curr_md = matchdays[current_idx]
            next_md = matchdays[current_idx + 1] if current_idx + 1 < len(matchdays) else None

            database[name_key] = {
                "name": league["name"],
                "competition_id": comp_id,
                "season_id": season_id,

                # PREVIOUS
                "previous_matchday_id": prev_md.get("id") if prev_md else None,
                "previous_mixer_url": (
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{prev_md.get('id')}"
                    if prev_md else None
                ),

                # CURRENT
                "current_matchday_id": curr_md.get("id"),
                "current_mixer_url": (
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{curr_md.get('id')}"
                ),

                # NEXT
                "next_matchday_id": next_md.get("id") if next_md else None,
                "next_mixer_url": (
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{next_md.get('id')}"
                    if next_md else None
                )
            }

            print(f"✅ {league['name']} updated (prev/current/next)")

        except Exception as e:
            print(f"💥 ERROR {league['name']}: {e}")

    save_database(database)
    print("🏁 DONE - matchdays.json updated")

# ==================================================
if __name__ == "__main__":
    build()
