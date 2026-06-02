import requests
import time

# Target base configuration
COMPETITION_ID = "120"
SEASON_ID = "41642"
BASE_URL_FEED = f"https://feedmonster.onefootball.com/feeds/il/en/competitions/{COMPETITION_ID}/{SEASON_ID}/"
BASE_URL_API = "https://api.onefootball.com/scores-mixer/v1/en/cn/"

# Common headers to bypass basic bot protection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://onefootball.com",
    "Referer": "https://onefootball.com/"
}

# Advanced wordlist based on OneFootball legacy structure
FEED_ENDPOINTS = [
    "teams", "fixtures", "matches", "results", "players", 
    "top_scorers", "assists", "cards", "transfers", "news",
    "stages", "groups", "overview", "calendar", "season_overview",
    "fixtures-overview", "matchdays", "meta"
]

API_ENDPOINTS = [
    f"competitions/{COMPETITION_ID}",
    f"competitions/{COMPETITION_ID}/matchdays",
    "matchdays/today",
    "matchdays/current",
    "live-scores"
]

def scan_endpoints():
    print(f"=== Starting Scan for Competition: {COMPETITION_ID}, Season: {SEASON_ID} ===")
    print("Checking FeedMonster endpoints...")
    
    # 1. Scan Feedmonster (Static JSONs)
    for endpoint in FEED_ENDPOINTS:
        url = f"{BASE_URL_FEED}{endpoint}.json"
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                print(f"[SUCCESS] [200 OK] -> {url}")
            elif response.status_code == 403:
                print(f"[FORBIDDEN] [403] -> {url} (Endpoint exists but requires extra headers/auth)")
            # 404 is ignored to keep the output clean
            
            # Tiny sleep to be polite to the server
            time.sleep(0.2)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not connect to {url}: {e}")

    print("\nChecking API (Scores-Mixer) endpoints...")
    # 2. Scan Live API
    for endpoint in API_ENDPOINTS:
        url = f"{BASE_URL_API}{endpoint}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                print(f"[SUCCESS] [200 OK] -> {url}")
            elif response.status_code == 403:
                print(f"[FORBIDDEN] [403] -> {url}")
            
            time.sleep(0.2)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not connect to {url}: {e}")

    print("=== Scan completed ===")

if __name__ == "__main__":
    scan_endpoints()
