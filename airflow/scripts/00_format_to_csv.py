import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


DEFAULT_CONTAINER_DATA_DIR = Path("/opt/airflow/data")


def resolve_input_path(input_file):
    """Résout un chemin absolu ou relatif vers le dossier data partagé."""
    file_path = Path(input_file)
    if file_path.is_absolute():
        return file_path

    repo_data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    container_candidate = DEFAULT_CONTAINER_DATA_DIR / file_path
    repo_candidate = repo_data_dir / file_path
    return container_candidate if container_candidate.exists() else repo_candidate


def ensure_output_dir():
    """Crée le dossier de sortie des fichiers convertis."""
    output_dir = DEFAULT_CONTAINER_DATA_DIR / "converted"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def ensure_processed_dir():
    """Crée le dossier d'archivage des fichiers source déjà traités."""
    processed_dir = DEFAULT_CONTAINER_DATA_DIR / "input" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir


def list_pending_input_files(input_dir="input", single_input_file=None):
    """Retourne tous les fichiers XML/JSON en attente, du plus récent au plus ancien."""
    if single_input_file:
        source_path = resolve_input_path(single_input_file)
        return [str(source_path)]

    source_dir = resolve_input_path(input_dir)
    if not source_dir.exists():
        return []

    files = [
        path for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".json", ".xml"}
    ]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return [str(path) for path in files]


def detect_input_format(input_file):
    """Identifie le format du fichier source à partir de son extension."""
    source_path = resolve_input_path(input_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {source_path}")

    extension = source_path.suffix.lower()
    if extension == ".json":
        return {"input_file": str(source_path), "file_format": "json"}
    if extension == ".xml":
        return {"input_file": str(source_path), "file_format": "xml"}

    raise ValueError(f"Format non supporté : {extension}. Utilise un fichier .json ou .xml")


def convert_input_file_to_csv(input_file):
    """Choisit automatiquement la bonne conversion selon le format détecté."""
    detected = detect_input_format(input_file)
    file_format = detected["file_format"]
    source_path = detected["input_file"]

    if file_format == "json":
        csv_path = transform_json_to_csv(source_path)
    elif file_format == "xml":
        csv_path = transform_xml_to_csv(source_path)
    else:
        raise ValueError(f"Format inattendu : {file_format}")

    return {
        "input_file": source_path,
        "file_format": file_format,
        "csv_path": csv_path,
    }


def archive_input_file(input_file):
    """Déplace un fichier source traité vers le dossier processed."""
    source_path = resolve_input_path(input_file)
    if not source_path.exists():
        return str(source_path)

    processed_dir = ensure_processed_dir()
    target_path = processed_dir / source_path.name
    if target_path.exists():
        target_path = processed_dir / f"{source_path.stem}_processed{source_path.suffix}"

    shutil.move(str(source_path), str(target_path))
    print(f"Fichier source archivé : {target_path}")
    return str(target_path)


def merge_converted_csvs(processed_files):
    """Fusionne tous les CSV convertis en un seul fichier global."""
    if not processed_files:
        return None

    output_dir = ensure_output_dir()
    merged_path = output_dir / "merged_input.csv"

    dataframes = []
    for processed in processed_files:
        csv_path = Path(processed["csv_path"])
        df = pd.read_csv(csv_path)
        df["source_file"] = Path(processed["input_file"]).name
        df["source_format"] = processed["file_format"]
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
    merged_df.to_csv(merged_path, index=False)
    print(f"CSV fusionné généré : {merged_path}")

    return {
        "csv_path": str(merged_path),
        "processed_files": processed_files,
    }


def _normalize_json_payload(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
        return [payload]

    raise ValueError("Le contenu JSON doit être une liste ou un objet JSON")


def _normalize_cell_value(value):
    """Aplatit les listes/dicts pour obtenir un CSV exploitable."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=True)
    return value


def transform_json_to_csv(input_file):
    """Convertit un fichier JSON en CSV et retourne le chemin de sortie."""
    source_path = resolve_input_path(input_file)
    output_dir = ensure_output_dir()
    output_path = output_dir / f"{source_path.stem}.csv"

    with open(source_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    records = _normalize_json_payload(payload)
    df = pd.json_normalize(records)
    df = df.apply(lambda column: column.map(_normalize_cell_value))
    df.to_csv(output_path, index=False)

    print(f"CSV généré depuis JSON : {output_path}")
    return str(output_path)


def transform_xml_to_csv(input_file):
    """Convertit un fichier XML simple en CSV et retourne le chemin de sortie."""
    source_path = resolve_input_path(input_file)
    output_dir = ensure_output_dir()
    output_path = output_dir / f"{source_path.stem}.csv"

    tree = ET.parse(source_path)
    root = tree.getroot()

    records = []
    for child in root:
        record = {}
        for field in child:
            if list(field):
                record[field.tag] = ", ".join(
                    subfield.text.strip()
                    for subfield in field
                    if subfield.text and subfield.text.strip()
                )
            else:
                record[field.tag] = field.text
        if record:
            records.append(record)

    if not records:
        raise ValueError("Aucun enregistrement tabulaire trouvé dans le XML")

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)

    print(f"CSV généré depuis XML : {output_path}")
    return str(output_path)
