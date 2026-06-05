import json
import requests
import os
from datetime import datetime

# -------------------------------------------------
# KONFIG
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEAGUES_FILE = os.path.join(BASE_DIR, "leagues.json")
MATCHDAYS_FILE = os.path.join(BASE_DIR, "matchdays.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

# -------------------------------------------------
# BUILD
# -------------------------------------------------

def build_matchday_database():

    print("====================================")
    print("CURRENT DIRECTORY:")
    print(os.getcwd())
    print("====================================")

    print("FILES FOUND:")
    for f in os.listdir(BASE_DIR):
        print(repr(f))

    print("====================================")
    print("LEAGUES PATH:")
    print(LEAGUES_FILE)
    print("EXISTS:", os.path.exists(LEAGUES_FILE))
    print("====================================")

    # Kreiraj bazu ako ne postoji
    if not os.path.exists(MATCHDAYS_FILE):
        with open(MATCHDAYS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    try:
        with open(MATCHDAYS_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
    except:
        database = {}

    try:
        with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
            leagues_data = json.load(f)
    except Exception as e:
        print(f"❌ GREŠKA LEAGUES.JSON: {e}")
        return

    sada = datetime.now()
    trenutni_dan = sada.weekday()
    trenutni_sat = sada.hour

    print(f"\n⏰ Dan={trenutni_dan} Sat={trenutni_sat}\n")

    for league in leagues_data:

        league_name = league["name"].lower().replace(" ", "_")

        aktivni_dani = league.get(
            "days_active",
            [0, 1, 2, 3, 4, 5, 6]
        )

        if trenutni_dan not in aktivni_dani:
            print(f"💤 {league['name']} preskačem")
            continue

        print(f"🚀 {league['name']}")

        comp_id = league["id"]
        season_id = league["s"]

        url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            if r.status_code != 200:
                print(f"❌ HTTP {r.status_code}")
                continue

            data = r.json()

            current_idx = None

            for i, md in enumerate(data.get("matchdays", [])):
                if md.get("isCurrentMatchday"):
                    current_idx = i
                    break

            if current_idx is None:
                print("❌ Nema current matchday")
                continue

            matchdays = data["matchdays"]

            previous_id = None
            current_id = None
            next_id = None

            if current_idx > 0:
                previous_id = matchdays[current_idx - 1]["id"]

            current_id = matchdays[current_idx]["id"]

            if current_idx + 1 < len(matchdays):
                next_id = matchdays[current_idx + 1]["id"]

            database[league_name] = {
                "name": league["name"],
                "competition_id": comp_id,
                "season_id": season_id,

                "previous_matchday_id": previous_id,
                "current_matchday_id": current_id,
                "next_matchday_id": next_id,

                "previous_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{previous_id}"
                    if previous_id else None,

                "current_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{current_id}",

                "next_mixer_url":
                    f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{next_id}"
                    if next_id else None
            }

            print(
                f"✅ PREV={previous_id} "
                f"CUR={current_id} "
                f"NEXT={next_id}"
            )

        except Exception as e:
            print(f"💥 {e}")

    with open(MATCHDAYS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            database,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n🏁 GOTOVO")


if __name__ == "__main__":
    build_matchday_database()
