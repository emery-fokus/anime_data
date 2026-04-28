"""
Scraper pour le mock-site AniData Lab (Version Docker/Airflow)
Scrape le site via HTTP au lieu de fichiers locaux
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION DOCKER ---
# L'URL est le nom du service défini dans ton docker-compose
BASE_URL = "http://anidata-mock-site" 
# Chemins internes au container Airflow
OUTPUT_DIR = Path("/opt/airflow/data/scraped")
OUTPUT_FILE = OUTPUT_DIR / "anime_scraped.json"

def scrape_mock_site():
    """Scrape la liste des animes depuis la page d'accueil HTTP"""
    animes = []
    try:
        print(f"🌐 Connexion à {BASE_URL}...")
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # On cherche tous les liens qui mènent vers une page d'anime
        links = []
        for a in soup.find_all('a', href=True):
            if 'anime/' in a['href']:
                links.append(a['href'])
        
        # Supprimer les doublons
        links = list(set(links))
        print(f"🔍 {len(links)} pages d'animes détectées.")

        for link in links:
            # Construction de l'URL complète
            full_url = f"{BASE_URL}/{link.lstrip('/')}"
            anime_data = parse_anime_page(full_url)
            if anime_data:
                animes.append(anime_data)
    
    except Exception as e:
        print(f"❌ Erreur lors du scraping global: {e}")
    
    return animes

def parse_anime_page(url: str) -> dict | None:
    """Parse une page HTML distante via son URL"""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extraction du titre
        title_tag = soup.find("h2")
        title = title_tag.text.strip() if title_tag else "Inconnu"
        
        jp_title_tag = soup.find("div", class_="jp-title-big")
        jp_title = jp_title_tag.text.strip() if jp_title_tag else None
        
        specs = {}
        table = soup.find("table", class_="specs")
        if table:
            for row in table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    key = th.text.strip()
                    value = td.text.strip()
                    # Correction Linter : on va à la ligne après le ':'
                    if td.get("data-year"): 
                        value = td["data-year"]
                    if td.get("data-score"): 
                        value = td["data-score"]
                    specs[key] = value
        
        synopsis_div = soup.find("div", class_="synopsis")
        synopsis = ""
        if synopsis_div and synopsis_div.find("p"):
            synopsis = synopsis_div.find("p").text.strip()
        
        return {
            "title": title,
            "jp_title": jp_title,
            "year": specs.get("Année", ""),
            "studio": specs.get("Studio", ""),
            "type": specs.get("Type", ""),
            "episodes": specs.get("Épisodes", ""),
            "status": specs.get("Statut", ""),
            "genres": specs.get("Genres", ""),
            "score": specs.get("Score", "N/A"),
            "synopsis": synopsis,
            "source_url": url,
            "scraped_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Erreur sur {url}: {e}")
        return None

def save_to_json(animes: list, output_file: Path):
    """Sauvegarde les données en JSON"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(animes, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON sauvegardé: {output_file}")

def save_to_csv(animes: list, output_file: Path):
    """Sauvegarde les données en CSV"""
    # Correction Linter : pas de 'return' sur la même ligne que le 'if'
    if not animes: 
        return
        
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "title", "jp_title", "year", "studio", "type", 
        "episodes", "status", "genres", "score", 
        "synopsis", "source_url", "scraped_at"
    ]
    
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for anime in animes:
            row = {k: anime.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"✅ CSV sauvegardé: {output_file}")

def main():
    print("=" * 60)
    print("Spider 🕷️  Scraping du mock-site AniData Lab via Docker")
    print("=" * 60)
    
    animes = scrape_mock_site()
    
    if animes:
        save_to_json(animes, OUTPUT_FILE)
        save_to_csv(OUTPUT_FILE.with_suffix(".csv"))
        print(f"\n📊 Total: {len(animes)} animes récupérés avec succès !")
    else:
        print("❌ Aucune donnée récupérée. Vérifie si le site est en ligne.")

if __name__ == "__main__":
    main()






# """
# Scraper pour le mock-site AniData Lab (Version Docker/Airflow)
# Scrape le site via HTTP au lieu de fichiers locaux
# """
# import requests
# from bs4 import BeautifulSoup
# import json
# import csv
# from datetime import datetime
# from pathlib import Path

# # --- CONFIGURATION DOCKER ---
# # L'URL est le nom du service défini dans ton docker-compose
# BASE_URL = "http://anidata-mock-site" 
# # Chemins internes au container Airflow
# OUTPUT_DIR = Path("/opt/airflow/data/scraped")
# OUTPUT_FILE = OUTPUT_DIR / "anime_scraped.json"

# def scrape_mock_site():
#     """Scrape la liste des animes depuis la page d'accueil HTTP"""
#     animes = []
#     try:
#         print(f"🌐 Connexion à {BASE_URL}...")
#         response = requests.get(BASE_URL, timeout=10)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         # On cherche tous les liens qui mènent vers une page d'anime
#         # Dans le mock-site, ils sont souvent dans des balises <a> avec 'anime/' dans l'url
#         links = []
#         for a in soup.find_all('a', href=True):
#             if 'anime/' in a['href']:
#                 links.append(a['href'])
        
#         # Supprimer les doublons
#         links = list(set(links))
#         print(f"🔍 {len(links)} pages d'animes détectées.")

#         for link in links:
#             # Construction de l'URL complète
#             full_url = f"{BASE_URL}/{link.lstrip('/')}"
#             anime_data = parse_anime_page(full_url)
#             if anime_data:
#                 animes.append(anime_data)
    
#     except Exception as e:
#         print(f"❌ Erreur lors du scraping global: {e}")
    
#     return animes

# def parse_anime_page(url: str) -> dict | None:
#     """Parse une page HTML distante via son URL"""
#     try:
#         response = requests.get(url, timeout=5)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         # Extraction (ton code original très bien fait)
#         title = soup.find("h2")
#         title = title.text.strip() if title else "Inconnu"
        
#         jp_title = soup.find("div", class_="jp-title-big")
#         jp_title = jp_title.text.strip() if jp_title else None
        
#         specs = {}
#         table = soup.find("table", class_="specs")
#         if table:
#             for row in table.find_all("tr"):
#                 th = row.find("th")
#                 td = row.find("td")
#                 if th and td:
#                     key = th.text.strip()
#                     value = td.text.strip()
#                     if td.get("data-year"): value = td["data-year"]
#                     if td.get("data-score"): value = td["data-score"]
#                     specs[key] = value
        
#         synopsis_div = soup.find("div", class_="synopsis")
#         synopsis = synopsis_div.find("p").text.strip() if synopsis_div and synopsis_div.find("p") else ""
        
#         return {
#             "title": title,
#             "jp_title": jp_title,
#             "year": specs.get("Année", ""),
#             "studio": specs.get("Studio", ""),
#             "type": specs.get("Type", ""),
#             "episodes": specs.get("Épisodes", ""),
#             "status": specs.get("Statut", ""),
#             "genres": specs.get("Genres", ""),
#             "score": specs.get("Score", "N/A"),
#             "synopsis": synopsis,
#             "source_url": url,
#             "scraped_at": datetime.now().isoformat()
#         }
#     except Exception as e:
#         print(f"❌ Erreur sur {url}: {e}")
#         return None

# def save_to_json(animes: list, output_file: Path):
#     output_file.parent.mkdir(parents=True, exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(animes, f, ensure_ascii=False, indent=2)
#     print(f"✅ JSON sauvegardé: {output_file}")

# def save_to_csv(animes: list, output_file: Path):
#     if not animes: return
#     output_file.parent.mkdir(parents=True, exist_ok=True)
#     fieldnames = ["title", "jp_title", "year", "studio", "type", "episodes", "status", "genres", "score", "synopsis", "source_url", "scraped_at"]
#     with open(output_file, "w", encoding="utf-8", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for anime in animes:
#             row = {k: anime.get(k, "") for k in fieldnames}
#             writer.writerow(row)
#     print(f"✅ CSV sauvegardé: {output_file}")

# def main():
#     print("=" * 60)
#     print("🕷️  Scraping du mock-site AniData Lab via Docker Network")
#     print("=" * 60)
    
#     animes = scrape_mock_site()
    
#     if animes:
#         save_to_json(animes, OUTPUT_FILE)
#         save_to_csv(OUTPUT_FILE.with_suffix(".csv"))
#         print(f"\n📊 Total: {len(animes)} animes récupérés avec succès !")
#     else:
#         print("❌ Aucune donnée récupérée. Vérifie si le site est en ligne.")

# if __name__ == "__main__":
#     main()