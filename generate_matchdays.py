import json
import requests
import os
from datetime import datetime
from pathlib import Path

# ==================================================
# MATCHDAY GENERATOR V2 - FIKSIRANE PUTANJE
# ==================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

# Koristimo os.getcwd() da budemo sigurni da traži fajlove u mapi gdje se pokreće skripta
BASE_DIR = os.getcwd()
LEAGUES_FILE = os.path.join(BASE_DIR, "leagues.json")
MATCHDAYS_FILE = os.path.join(BASE_DIR, "matchdays.json")

def load_existing_database():
    try:
        if os.path.exists(MATCHDAYS_FILE):
            with open(MATCHDAYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Ne mogu učitati stari matchdays.json: {e}")
    return {}

def load_leagues():
    if not os.path.exists(LEAGUES_FILE):
        raise FileNotFoundError(f"Datoteka nije pronađena na putanji: {LEAGUES_FILE}")
    with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_matchday_ids(comp_id, season_id):
    url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code}")
    data = r.json()
    matchdays = data.get("matchdays", [])
    if not matchdays:
        raise Exception("Nema matchday podataka")

    current_index = -1
    for i, md in enumerate(matchdays):
        if md.get("isCurrentMatchday"):
            current_index = i
            break

    if current_index == -1:
        raise Exception("Nije pronađeno trenutno kolo")

    return {
        "previous_matchday_id": matchdays[current_index - 1]["id"] if current_index > 0 else None,
        "current_matchday_id": matchdays[current_index]["id"],
        "next_matchday_id": matchdays[current_index + 1]["id"] if current_index < len(matchdays) - 1 else None
    }

def build():
    database = load_existing_database()
    leagues = load_leagues()
    now = datetime.now()
    current_day = now.weekday()
    
    print(f"⏰ Dan: {current_day}")
    updated_count = 0

    for league in leagues:
        league_name = league["name"]
        key = league_name.lower().replace(" ", "_")
        active_days = league.get("days_active", [0, 1, 2, 3, 4, 5, 6])

        if current_day not in active_days:
            print(f"💤 {league_name} preskačem")
            continue

        comp_id = league["id"]
        season_id = league["s"]
        print(f"🚀 {league_name}")

        try:
            ids = get_matchday_ids(comp_id, season_id)
            database[key] = {
                "name": league_name,
                "competition_id": comp_id,
                "season_id": season_id,
                "previous_matchday_id": ids["previous_matchday_id"],
                "current_matchday_id": ids["current_matchday_id"],
                "next_matchday_id": ids["next_matchday_id"],
                "previous_mixer_url": f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{ids['previous_matchday_id']}" if ids['previous_matchday_id'] else None,
                "current_mixer_url": f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{ids['current_matchday_id']}",
                "next_mixer_url": f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{ids['next_matchday_id']}" if ids['next_matchday_id'] else None
            }
            updated_count += 1
        except Exception as e:
            print(f"   ❌ Greška za {league_name}: {e}")

    with open(MATCHDAYS_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Ažurirano liga: {updated_count}")

if __name__ == "__main__":
    build()
