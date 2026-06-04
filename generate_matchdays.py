import json
import requests

# Tvoj GitHub link za leagues.json
GITHUB_LEAGUES_URL = "https://raw.githubusercontent.com/zeroOSeven-AI/OneFootball/refs/heads/main/leagues.json?token=GHSAT0AAAAAAD7CHUMJZ4UZQ7JJYN7NXHYE2RB5DVQ"

# Čišćenje URL-a od privremenih tokena ako repozitorij postane javan
if "leagues.json" in GITHUB_LEAGUES_URL and "token=GHSAT" not in GITHUB_LEAGUES_URL:
    GITHUB_LEAGUES_URL = GITHUB_LEAGUES_URL.split("?")[0]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://onefootball.com"
}

def build_matchday_database():
    database = {}
    
    print("🌐 Dohvaćam tvoju listu liga s GitHuba...")
    try:
        res_leagues = requests.get(GITHUB_LEAGUES_URL, headers=HEADERS, timeout=10)
        if res_leagues.status_code == 200:
            leagues_data = res_leagues.json()
            print(f"✅ Uspješno učitano {len(leagues_data)} liga s GitHuba.\n")
        else:
            print(f"❌ Ne mogu dohvatiti lige s GitHuba. Status kod: {res_leagues.status_code}")
            return
    except Exception as e:
        print(f"💥 Greška pri dohvaćanju liga s GitHuba: {e}")
        return

    print(f"🔄 Pokrećem bager za dohvaćanje aktivnih kola s OneFootballa...")
    
    for league in leagues_data:
        # Spremamo ključ u formatu "premier_league", "1._hnl" itd., ovisno o imenu s GitHuba
        league_name = league["name"].lower().replace(" ", "_")
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
                    print(f"⚠️ {league['name']} -> Nema aktivnog kola (isCurrentMatchday) u JSON-u.")
            else:
                print(f"❌ {league['name']} -> Server vratio status {res.status_code}")
        except Exception as e:
            print(f"💥 Greška na ligi {league['name']}: {e}")
            
    # Spremanje baze u matchdays.json
    try:
        with open("matchdays.json", "w", encoding="utf-8") as f:
            json.dump(database, f, indent=4, ensure_ascii=False)
        print("\n🏁 Baza 'matchdays.json' je uspješno stvorena i spremna!")
    except Exception as e:
        print(f"💥 Greška pri zapisivanju datoteke: {e}")

if __name__ == "__main__":
    build_matchday_database()
