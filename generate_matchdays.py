import json  # Provjeri imaš li ovo na samom vrhu skripte

def build_matchday_database():
    # Umjesto requests.get, samo učitamo lokalni leagues.json
    try:
        with open('leagues.json', 'r', encoding='utf-8') as f:
            leagues = json.load(f)
    except FileNotFoundError:
        print("Greška: leagues.json ne postoji u ovom direktoriju!")
        return
    except json.JSONDecodeError:
        print("Greška: leagues.json nije ispravan JSON format!")
        return

    # Ovdje se tvoj kod nastavlja dalje, varijabla 'leagues' je spremna...
