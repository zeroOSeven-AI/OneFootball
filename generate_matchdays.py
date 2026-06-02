import json
import requests

# Tvoja masovna lista liga pretvorena u Python rječnik (skraćeni prikaz radi preglednosti)
LEAGUES_DATA = [
    {"name": "Premier League", "id": 9, "s": 39301},
    {"name": "Bundesliga", "id": 1, "s": 39285},
    {"name": "Serie A", "id": 13, "s": 39325},
    {"name": "LaLiga", "id": 10, "s": 39319},
    {"name": "Ligue 1 Uber Eats", "id": 23, "s": 39245},
    {"name": "1. HNL", "id": 120, "s": 39272}
    # Ovdje u skriptu na GitHubu slobodno ubaci apsolutno sve lige iz tvog popisa
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://onefootball.com"
}

def build_matchday_database():
    database = {}
    
    print(f"🔄 Pokrećem bager za {len(LEAGUES_DATA)} liga...")
    
    for league in LEAGUES_DATA:
        league_name = league["name"].lower().replace(" ", "_") # npr. "premier_league"
        comp_id = league["id"]
        season_id = league["s"]
        
        url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                data = res.json()
                current_id = None
                
                # Tražimo aktivno kolo u petlji
                for matchday in data.get("matchdays", []):
                    if matchday.get("isCurrentMatchday") == True:
                        current_id = matchday.get("id")
                        break
                
                if current_id:
                    database[league_name] = {
                        "name": league["name"],
                        "competition_id": comp_id,
                        "season_id": season_id,
                        "current_matchday_id": current_id,
                        "mixer_url": f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{current_id}"
                    }
                    print(f"✅ {league['name']} -> Kolo ID: {current_id}")
            else:
                print(f"❌ {league['name']} -> Server vratio status {res.status_code}")
        except Exception as e:
            print(f"💥 Greška na ligi {league['name']}: {e}")
            
    # Spremanje baze na GitHub Pages
    with open("matchdays.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
        
    print("🏁 Baza 'matchdays.json' je uspješno stvorena i spremna!")

if __name__ == "__main__":
    build_matchday_database()
