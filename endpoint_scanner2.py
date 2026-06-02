import json
import os
import requests
import time

INPUT_FILE = "links_to_test.json"
OUTPUT_FILE = "working_links.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://onefootball.com",
    "Referer": "https://onefootball.com/"
}

def load_links():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file '{INPUT_FILE}' not found!")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_working_links(working_links):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(working_links, f, indent=4, ensure_ascii=False)
    print(f"\n[SUCCESS] Saved {len(working_links)} working links to '{OUTPUT_FILE}'")

def scan_links():
    links = load_links()
    if not links:
        print("No links to scan. Exiting.")
        return

    print(f"=== Starting Scan of {len(links)} URLs from JSON ===")
    working_links = []

    for url in links:
        try:
            # Send request using our headers
            response = requests.get(url, headers=HEADERS, timeout=5)
            
            if response.status_code == 200:
                print(f"[WORKING] [200 OK] -> {url}")
                working_links.append(url)
            else:
                print(f"[FAILED] [{response.status_code}] -> {url}")
                
            # Sleep briefly to avoid hammering the server
            time.sleep(0.2)
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Connection failed for {url}: {e}")

    # Save results to a new JSON file
    save_working_links(working_links)
    print("=== Scan completed ===")

if __name__ == "__main__":
    scan_links()
