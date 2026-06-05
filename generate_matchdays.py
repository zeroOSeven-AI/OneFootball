import json
import requests

# =========================
# CONFIG
# =========================
LEAGUES_FILE = "leagues.json"
OUTPUT_FILE = "matchdays.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

# =========================
# FETCH MATCHDAYS FROM ONEFOOTBALL
# =========================
def fetch_matchdays(comp_id, season_id):

    url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"

    try:
        r = requests.get(url, headers=HEADERS, timeout=8)

        if r.status_code != 200:
            print(f"   ❌ HTTP ERROR {r.status_code}")
            return None

        data = r.json()
        matchdays = data.get("matchdays", [])

        if not matchdays:
            return None

        current_index = None

        for i, md in enumerate(matchdays):
            if md.get("isCurrentMatchday") is True:
                current_index = i
                break

        if current_index is None:
            print("   ❌ No current matchday found")
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
        print("   💥 Exception:", e)
        return None


# =========================
# MAIN BUILDER
# =========================
def build_matchday_database():

    try:
        with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
            leagues = json.load(f)
    except Exception as e:
        print("❌ Cannot load leagues.json:", e)
        return

    database = {}

    print("\n🚀 STARTING MATCHDAY BUILD\n")

    for league in leagues:

        name_key = league["name"].lower().replace(" ", "_")

        comp_id = league["id"]
        season_id = league["s"]

        print(f"⚽ {league['name']}")

        md = fetch_matchdays(comp_id, season_id)

        if not md:
            print("   ❌ SKIPPED\n")
            continue

        database[name_key] = {
            "name": league["name"],
            "competition_id": comp_id,
            "season_id": season_id,
            "matchdays": {
                "previous": md["previous"],
                "current": md["current"],
                "next": md["next"]
            }
        }

        print(f"   ✔ Previous: {md['previous']}")
        print(f"   ✔ Current : {md['current']}")
        print(f"   ✔ Next    : {md['next']}\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)

    print("🏁 DONE → matchdays.json updated successfully!\n")


if __name__ == "__main__":
    build_matchday_database()
