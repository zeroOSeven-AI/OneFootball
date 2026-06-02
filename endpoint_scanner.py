import json
import requests

OUTPUT_FILE = "working_links.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://onefootball.com",
    "Referer": "https://onefootball.com/"
}

def auto_scan_and_mix():
    print("=== Pokrećem pametno skeniranje tvojih linkova ===")
    working_links = []

    # 1. Tvoja tri provjerena statična linka
    static_links = [
        "https://feedmonster.onefootball.com/feeds/il/en/competitions/120/41642/matchdaysOverview.json",
        "https://feedmonster.onefootball.com/feeds/il/en/competitions/120/41642/standings.json",
        "https://feedmonster.onefootball.com/feeds/il/en/competitions/120/41642/league_statistics.json"
    ]

    current_matchday_id = None

    # Provjeravamo prva tri linka i usput tražimo ID trenutnog kola
    for url in static_links:
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                print(f"[WORKING] [200 OK] -> {url}")
                working_links.append(url)
                
                # Ako je ovo matchdaysOverview, čupamo ID kola
                if "matchdaysOverview.json" in url:
                    data = res.json()
                    # Prolazimo kroz sva kola u JSON-u i tražimo ono koje je aktivno
                    for matchday in data.get("matchdays", []):
                        if matchday.get("isCurrentMatchday") == True:
                            current_matchday_id = matchday.get("id")
                            break
            else:
                print(f"[FAILED] [{res.status_code}] -> {url}")
        except Exception as e:
            print(f"[ERROR] Greška na linku {url}: {e}")

    # 2. Ako smo uspješno pronašli ID kola, slažemo i testiramo četvrti link (Scores Mixer)
    if current_matchday_id:
        mixer_url = f"https://api.onefootball.com/scores-mixer/v1/en/cn/matchdays/{current_matchday_id}"
        print(f"\n[INFO] Automatski pronađen ID trenutnog kola: {current_matchday_id}")
        print(f"[INFO] Testiram Scores-Mixer na linku: {mixer_url}")
        
        try:
            res = requests.get(mixer_url, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                print(f"[WORKING] [200 OK] -> {mixer_url}")
                working_links.append(mixer_url)
            else:
                print(f"[FAILED] [{res.status_code}] -> {mixer_url}")
        except Exception as e:
            print(f"[ERROR] Greška na mixer linku: {e}")
    else:
        print("\n[WARNING] Nisam uspio automatski pročitati isCurrentMatchday iz JSON-a.")

    # 3. Spremanje svih aktivnih linkova u JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(working_links, f, indent=4, ensure_ascii=False)
    
    print(f"\n=== Skeniranje završeno. Spremljeno {len(working_links)} linkova u '{OUTPUT_FILE}' ===")

if __name__ == "__main__":
    auto_scan_and_mix()
