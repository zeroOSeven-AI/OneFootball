import json
import requests
from datetime import datetime

# --- DEFINICIJA KONSTANTI ---
LEAGUES_FILE = "leagues.json" 
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
}

def build_matchday_database():
    # Učitavamo staru (postojeću) bazu da ne izgubimo podatke
    try:
        with open("matchdays.json", "r", encoding="utf-8") as f:
            database = json.load(f)
    except Exception:
        database = {}

    # UČITAVANJE LOKALNOG JSON-A (Popravljeno ovdje)
    try:
        with open(LEAGUES_FILE, "r", encoding="utf-8") as f:
            leagues_data = json.load(f)
    except Exception as e:
        print(f"❌ Greška pri čitanju {LEAGUES_FILE}: {e}")
        return

    # Trenutno vrijeme
    sada = datetime.now()
    trenutni_dan = sada.weekday() 
    trenutni_sat = sada.hour

    print(f"⏰ Trenutno vrijeme na serveru: Dan {trenutni_dan}, Sat {trenutni_sat}:00")
    print("🔄 Pokrećem pametno filtriranje liga...")

    for league in leagues_data:
        league_name = league["name"].lower().replace(" ", "_")
        
        aktivni_dani = league.get("days_active", [0, 1, 2, 3, 4, 5, 6])
        
        if trenutni_dan not in aktivni_dani:
            print(f"💤 {league['name']} -> Preskačem (nije dan za utakmice/izmjenu).")
            continue
            
        print(f"🚀 {league['name']} je AKTIVNA. Provjeravam kolo na OneFootballu...")
        
        comp_id = league["id"]
        season_id = league["s"]
        url = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{comp_id}/{season_id}/matchdaysOverview.json"
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                data = res.json()
                for matchday in data.get("matchdays", []):
                    if matchday.get("isCurrentMatchday") == True:
                        current_id = matchday.get("id")
                        
                        database[league_name] = {
                            "name": league["name"],
                            "competition_id": comp_id,
                            "season_id": season_id,
                            "current_matchday_id": current_id,
                            "mixer_url": f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{current_id}"
                        }
                        print(f"   ✅ Uspješno ažurirano! Kolo ID: {current_id}")
                        break
            else:
                print(f"   ❌ Greška s OneFootball serverom ({res.status_code})")
        except Exception as e:
            print(f"   💥 Greška: {e}")

    # Spremanje osvježene kombinacije
    with open("matchdays.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
        
    print("\n🏁 Pametno ažuriranje baze završeno!")

if __name__ == "__main__":
    build_matchday_database()
