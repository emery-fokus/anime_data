import requests
import zipfile
import io

# 1. TES INFOS À REMPLIR
TOKEN = ""
REPO = "emery-fokus/anidata-scraper"           # Ton dépôt
ARTIFACT_NAME = "project-build"                # Le nom dans ton fichier .yml

headers = {"Authorization": f"token {TOKEN}"}

# 2. ON DEMANDE À GITHUB OÙ EST LE CODE
url = "https://api.github.com/repos/emery-fokus/anime_data/actions/artifacts"
response = requests.get(url, headers=headers)
artifacts = response.json().get("artifacts", [])

if artifacts:
    # On prend le dernier build "project-build"
    latest = next(a for a in artifacts if a["name"] == ARTIFACT_NAME)
    download_url = latest["archive_download_url"]
    
    # 3. ON TÉLÉCHARGE ET ON EXTRAIT
    print(f" Téléchargement de {ARTIFACT_NAME}...")
    r = requests.get(download_url, headers=headers)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("./mon_code_valide")
    print(" C'est fait ! Regarde dans le dossier 'mon_code_valide'.")
else:
    print("Aucun code trouvé. Ton GitHub Action est-il bien terminé ?")