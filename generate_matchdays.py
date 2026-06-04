import json
import requests
from datetime import datetime

https://raw.githubusercontent.com/zeroOSeven-AI/OneFootball/refs/heads/main/leagues.json%E2%81%A0

def build_matchday_database():
    # Učitavamo staru (postojeću) bazu da ne izgubimo podatke za lige koje danas preskačemo
    try:
        with open("matchdays.json", "r", encoding="utf-8") as f:
            database = json.load(f)
    except Exception:
        database = {}

    # Dohvaćamo tvoj nadograđeni leagues.json s GitHuba
    res_leagues = requests.get(GITHUB_LEAGUES_URL, headers=HEADERS, timeout=10)
    leagues_data = res_leagues.json()

    # Trenutno vrijeme na serveru (dan u tjednu i sat)
    sada = datetime.now()
    trenutni_dan = sada.weekday() # 0=Ponedjeljak, 1=Utorak... 6=Nedjelja (PAŽNJA: Python broji od 0=Pon, prilagodi JSON po želji)
    trenutni_sat = sada.hour

    print(f"⏰ Trenutno vrijeme na serveru: Dan {trenutni_dan}, Sat {trenutni_sat}:00")
    print("🔄 Pokrećem pametno filtriranje liga...")

    for league in leagues_data:
        league_name = league["name"].lower().replace(" ", "_")
        
        # Čitanje pametnih pravila iz JSON-a (ako ih nema, stavi default da uvijek radi)
        aktivni_dani = league.get("days_active", [0, 1, 2, 3, 4, 5, 6])
        sat_azuriranja = league.get("update_hour", 0)

        # Ključni uvjet: Provjeri je li liga aktivna danas
        # Ako nije njezin dan, potpuno je preskačemo i ostaje stari matchday ID u bazi
        if trenutni_dan not in aktivni_dani:
            print(f"💤 {league['name']} -> Preskačem (nije dan za utakmice/izmjenu).")
            continue
            
        # Možeš čak dodati i uvjet za sat ako želiš biti još precizniji
        # if trenutni_sat < sat_azuriranja: ...

        # Ako je prošla provjeru, idemo na OneFootball po svježi Matchday ID
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

    # Spremanje osvježene kombinacije starih i novih podataka
    with open("matchdays.json", "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
        
    print("\n🏁 Pametno ažuriranje baze završeno!")

if __name__ == "__main__":
    build_matchday_database()
