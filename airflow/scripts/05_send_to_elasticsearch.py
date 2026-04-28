"""
🎌 AniData Lab — Indexation dans Elasticsearch
================================================
Séance 3 — Mardi 24 mars 2026 — Après-midi

Ce script :
  1. Vérifie la connexion à Elasticsearch
  2. Crée l'index "anime" avec un mapping optimisé
  3. Indexe le dataset anime_gold.json en bulk
  4. Vérifie l'indexation avec des requêtes de test
  5. Affiche des statistiques

Usage : python 06_indexation_es.py
Prérequis : pip install elasticsearch pandas
Entrée : output/anime_gold.json (généré par 05_validation.py)
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path



def run_indexation(index_name="anime"):
    try:
        from elasticsearch import Elasticsearch, helpers
        from elasticsearch._sync.client import _base as es_base
    except ImportError:
        print("❌ Module 'elasticsearch' non installé.")
        print("   Installez-le avec : pip install elasticsearch")
        sys.exit(1)

    # ============================================
    # CONFIG
    # ============================================
    BASE_DIR = Path(__file__).resolve().parent.parent
    ES_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
    INDEX_NAME = index_name
    INPUT_FILE = BASE_DIR / "output" / "anime_gold.json"
    BULK_CHUNK_SIZE = int(os.getenv("ANIDATA_ES_BULK_CHUNK_SIZE", "100"))
    ES_HEADERS = {
        "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
    }

    # Le client Python installé est en 9.x alors que le cluster Docker est en 8.x.
    # On force donc la compatibilité 8 pour toutes les requêtes générées par le client.
    es_base._COMPAT_MIMETYPE_SUB = "application/vnd.elasticsearch+\\g<1>; compatible-with=8"

    class C:
        H = "\033[95m"
        B = "\033[94m"
        G = "\033[92m"
        W = "\033[93m"
        F = "\033[91m"
        BOLD = "\033[1m"
        CYAN = "\033[96m"
        END = "\033[0m"

    def titre(t):
        print(f"\n{C.BOLD}{C.H}{'='*60}\n  {t}\n{'='*60}{C.END}\n")

    def step(t):
        print(f"\n{C.BOLD}{C.B}--- {t} ---{C.END}")

    def log_ok(t):
        print(f"  {C.G}✅ {t}{C.END}")

    def log_warn(t):
        print(f"  {C.W}⚠️  {t}{C.END}")

    def log_fail(t):
        print(f"  {C.F}❌ {t}{C.END}")

    def log_info(t):
        print(f"  {C.B}ℹ️  {t}{C.END}")

    def audit_error(step_name, error):
        """Affiche un audit court et utile de l'erreur."""
        error_type = type(error).__name__
        print(f"  Étape       : {step_name}")
        print(f"  Type erreur : {error_type}")
        print(f"  Message     : {error}")
        last_trace = traceback.format_exc().strip().splitlines()
        if last_trace:
            print(f"  Trace       : {last_trace[-1]}")

    def ko(step_name, error, retry_delay=30, attempt=1, max_attempts=2):
        """Journalise l'échec, audite l'erreur et décide du retry."""
        log_fail(f"{step_name} a échoué (tentative {attempt}/{max_attempts})")
        audit_error(step_name, error)
        if attempt < max_attempts:
            print(f"  Nouvelle tentative dans {retry_delay}s...")
            time.sleep(retry_delay)
            return True
        return False

    def ok(step_name, action, retry_delay=30):
        """Exécute une étape, audite l'erreur si besoin et retente une fois."""
        for attempt in range(1, 3):
            try:
                result = action()
                log_ok(f"{step_name} terminé")
                return result
            except Exception as error:
                if not ko(step_name, error, retry_delay=retry_delay, attempt=attempt, max_attempts=2):
                    raise


    # ============================================
    # MAPPING ELASTICSEARCH
    # ============================================
    ANIME_MAPPING = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "anime_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                # --- Identifiants ---
                "mal_id":           { "type": "integer" },

                # --- Noms (recherche full-text) ---
                "name":             { "type": "text", "analyzer": "anime_analyzer",
                                    "fields": { "keyword": { "type": "keyword" } } },
                "english_name":     { "type": "text", "analyzer": "anime_analyzer" },
                "japanese_name":    { "type": "text" },

                # --- Scores ---
                "score":            { "type": "float" },
                "weighted_score":   { "type": "float" },
                "score_category":   { "type": "keyword" },

                # --- Catégories ---
                "type":             { "type": "keyword" },
                "source":           { "type": "keyword" },
                "rating":           { "type": "keyword" },

                # --- Genres ---
                "genres":           { "type": "keyword" },
                "main_genre":       { "type": "keyword" },
                "n_genres":         { "type": "integer" },
                "best_of_decade_label": { "type": "keyword" },

                # --- Studios ---
                "studios":          { "type": "keyword" },
                "main_studio":      { "type": "keyword" },
                "studio_tier":      { "type": "keyword" },

                # --- Statistiques numériques ---
                "episodes":         { "type": "integer" },
                "members":          { "type": "long" },
                "favorites":        { "type": "long" },
                "popularity":       { "type": "integer" },
                "ranked":           { "type": "float" },

                # --- Métriques calculées ---
                "drop_ratio":       { "type": "float" },
                "engagement_ratio": { "type": "float" },
                "duration_minutes": { "type": "integer" },

                # --- Compteurs de statut ---
                "watching":         { "type": "long" },
                "completed":        { "type": "long" },
                "on_hold":          { "type": "long" },
                "dropped":          { "type": "long" },
                "plan_to_watch":    { "type": "long" },

                # --- Temporel ---
                "indexed_at":       { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
                "aired":            { "type": "text" },
                "aired_start":      { "type": "date", "format": "yyyy-MM-dd||epoch_millis||strict_date_optional_time", "ignore_malformed": True },
                "aired_end":        { "type": "date", "format": "yyyy-MM-dd||epoch_millis||strict_date_optional_time", "ignore_malformed": True },
                "premiered":        { "type": "keyword" },
                "year":             { "type": "integer" },
                "decade":           { "type": "integer" },

                # --- Scores détaillés ---
                "score_10":         { "type": "long" },
                "score_9":          { "type": "long" },
                "score_8":          { "type": "long" },
                "score_7":          { "type": "long" },
                "score_6":          { "type": "long" },
                "score_5":          { "type": "long" },
                "score_4":          { "type": "long" },
                "score_3":          { "type": "long" },
                "score_2":          { "type": "long" },
                "score_1":          { "type": "long" },

                # --- Flags ---
                "is_best_of_decade": { "type": "boolean" },
                "is_outlier":       { "type": "boolean" },

                # --- Autres textes ---
                "duration":         { "type": "keyword" },
                "producers":        { "type": "keyword" },
                "licensors":        { "type": "keyword" },
            }
        }
    }


    # ============================================
    # 1. VÉRIFIER LA CONNEXION
    # ============================================
    titre("INDEXATION ELASTICSEARCH")

    step("Étape 1 : Connexion à Elasticsearch")

    print(f"  Tentative de connexion à {ES_HOST}...")

    es = Elasticsearch(ES_HOST, request_timeout=30, headers=ES_HEADERS)

    def connect_to_elasticsearch():
        max_retries = 10
        last_error = None
        for attempt in range(max_retries):
            try:
                health = es.cluster.health()
                cluster_name = health.get("cluster_name", "?")
                status = health.get("status", "?")
                log_ok(f"Connecté au cluster '{cluster_name}' (status: {status})")
                return health
            except Exception as error:
                last_error = error
                if attempt < max_retries - 1:
                    print(f"  ⏳ ES pas encore prêt (tentative {attempt + 1}/{max_retries})... attente 5s")
                    time.sleep(5)
        print("\n  Vérifiez que Docker tourne :")
        print("    docker compose ps")
        print("    docker compose logs elasticsearch")
        raise last_error

    ok("Connexion à Elasticsearch", connect_to_elasticsearch)


    # ============================================
    # 2. VÉRIFIER LE FICHIER D'ENTRÉE
    # ============================================
    step("Étape 2 : Vérification du fichier source")

    def load_source_docs():
        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"Fichier introuvable : {INPUT_FILE}")

        doc_count = 0
        first_doc = None
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                doc_count += 1
                if first_doc is None:
                    first_doc = json.loads(line)

        taille_mb = os.path.getsize(INPUT_FILE) / (1024 * 1024)
        log_ok(f"Fichier chargé : {doc_count:,} documents ({taille_mb:.1f} MB)")

        if first_doc:
            log_info(f"Premier document : {list(first_doc.keys())[:8]}...")
            name_key = "name" if "name" in first_doc else list(first_doc.keys())[0]
            log_info(f"Exemple : {first_doc.get(name_key, '?')} (score: {first_doc.get('score', '?')})")

        return doc_count

    try:
        doc_count = ok("Vérification du fichier source", load_source_docs)
    except Exception:
        print("  Lancez d'abord les scripts de nettoyage :")
        print("    python scripts/03_nettoyage.py")
        print("    python scripts/04_feature_engineering.py")
        print("    python scripts/05_validation.py")
        sys.exit(1)


    # ============================================
    # 3. CRÉER / RECRÉER L'INDEX
    # ============================================
    step("Étape 3 : Création de l'index")

    def create_index():
        if es.indices.exists(index=INDEX_NAME):
            log_warn(f"L'index '{INDEX_NAME}' existe déjà — suppression...")
            es.indices.delete(index=INDEX_NAME)
            log_ok("Ancien index supprimé")

        print(f"  Création de l'index '{INDEX_NAME}' avec mapping...")
        es.indices.create(index=INDEX_NAME, body=ANIME_MAPPING)
        log_ok(f"Index '{INDEX_NAME}' créé avec succès")

        mapping_fields = list(ANIME_MAPPING["mappings"]["properties"].keys())
        log_info(f"Mapping : {len(mapping_fields)} champs définis")
        print("  Types principaux :")
        type_counts = {}
        for field, config in ANIME_MAPPING["mappings"]["properties"].items():
            t = config.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    • {t:12s} : {count} champs")

    try:
        ok("Création de l'index", create_index)
    except Exception:
        sys.exit(1)


    # ============================================
    # 4. INDEXATION BULK
    # ============================================
    step(f"Étape 4 : Indexation bulk ({doc_count:,} documents)")

    print(f"  Taille des chunks : {BULK_CHUNK_SIZE} documents")
    print("  Début de l'indexation...\n")

    # Préparer les actions bulk
    def generate_actions():
        indexed_at = datetime.now(timezone.utc).isoformat()
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                doc = json.loads(line)
            # Déterminer l'ID du document
                doc_id = doc.get("mal_id", doc.get("anime_id", None))

            # Nettoyer les valeurs NaN/None pour ES
                clean_doc = {"indexed_at": indexed_at}
                for key, value in doc.items():
                    if value is None:
                        continue
                    if isinstance(value, float) and (value != value):  # NaN check
                        continue
                    clean_doc[key] = value

                action = {
                    "_index": INDEX_NAME,
                    "_source": clean_doc,
                }
                if doc_id is not None:
                    action["_id"] = str(doc_id)

                yield action

    # Indexation avec suivi de progression
    success_count = 0
    error_count = 0
    errors = []
    start_time = 0.0

    def bulk_index_documents():
        nonlocal success_count, error_count, errors, start_time
        start_time = time.time()
        for ok_flag, result in helpers.streaming_bulk(
            es,
            generate_actions(),
            chunk_size=BULK_CHUNK_SIZE,
            raise_on_error=False,
            raise_on_exception=False,
        ):
            if ok_flag:
                success_count += 1
            else:
                error_count += 1
                if len(errors) < 5:  # Garder les 5 premières erreurs
                    errors.append(result)

            # Progression
            total = success_count + error_count
            if total % 2000 == 0 or total == doc_count:
                elapsed = time.time() - start_time
                rate = total / elapsed if elapsed > 0 else 0
                pct = total / doc_count * 100
                bar = "█" * int(pct / 2.5) + "░" * (40 - int(pct / 2.5))
                print(f"\r  [{bar}] {pct:5.1f}% — {total:,}/{doc_count:,} — {rate:.0f} docs/s", end="", flush=True)

        print()
        if error_count > 0:
            raise RuntimeError(f"{error_count:,} document(s) en erreur pendant l'indexation")

    try:
        ok("Indexation bulk", bulk_index_documents)
    except Exception:
        if errors:
            print("  Exemples d'erreurs bulk :")
            for err in errors[:3]:
                print(f"    → {err}")
        sys.exit(1)

    elapsed = time.time() - start_time
    log_ok(f"Indexation terminée en {elapsed:.1f} secondes")
    log_ok(f"  Succès : {success_count:,}")
    if error_count > 0:
        log_warn(f"  Erreurs : {error_count:,}")
        for err in errors[:3]:
            print(f"    → {err}")

    ok("Rafraîchissement de l'index", lambda: es.indices.refresh(index=INDEX_NAME))


    # ============================================
    # 5. VÉRIFICATION
    # ============================================
    step("Étape 5 : Vérification de l'indexation")

    count = 0
    size_mb = 0.0

    def verify_indexation():
        nonlocal count, size_mb
        count = es.count(index=INDEX_NAME)["count"]
        log_ok(f"Documents dans l'index : {count:,}")

        if count != success_count:
            log_warn(f"Attention : {success_count:,} indexés mais {count:,} dans l'index")

        stats = es.indices.stats(index=INDEX_NAME)
        size_bytes = stats["indices"][INDEX_NAME]["total"]["store"]["size_in_bytes"]
        size_mb = size_bytes / (1024 * 1024)
        log_info(f"Taille de l'index : {size_mb:.1f} MB")

        print("\n  Tests de recherche rapides :")
        print(f"  {'─'*50}")

        result = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 1})
        total_hits = result["hits"]["total"]["value"]
        log_ok(f"match_all : {total_hits:,} résultats")

        test_queries = [
            ("Naruto", {"query": {"match": {"name": "naruto"}}}),
            ("Score > 9", {"query": {"range": {"score": {"gte": 9}}}}),
            ("Genre: Action", {"query": {"term": {"main_genre": "Action"}}}),
            ("Studio: Bones", {"query": {"match": {"main_studio": "Bones"}}}),
        ]

        for name, query in test_queries:
            result = es.search(index=INDEX_NAME, body={**query, "size": 3})
            hits = result["hits"]["total"]["value"]
            top_name = result["hits"]["hits"][0]["_source"].get("name", "?") if result["hits"]["hits"] else "aucun"
            log_ok(f"{name:20s} → {hits:,} résultats (top: {top_name})")

        print("\n  Agrégation : Top 5 genres")
        print(f"  {'─'*50}")
        agg_result = es.search(index=INDEX_NAME, body={
            "size": 0,
            "aggs": {
                "top_genres": {
                    "terms": {"field": "main_genre", "size": 5}
                }
            }
        })
        for bucket in agg_result["aggregations"]["top_genres"]["buckets"]:
            genre = bucket["key"]
            genre_count = bucket["doc_count"]
            bar = "█" * int(genre_count / 500)
            print(f"    {genre:20s} : {genre_count:>5,} {bar}")

        print("\n  Agrégation : Score moyen par type")
        print(f"  {'─'*50}")
        agg_result = es.search(index=INDEX_NAME, body={
            "size": 0,
            "aggs": {
                "by_type": {
                    "terms": {"field": "type", "size": 10},
                    "aggs": {
                        "avg_score": {"avg": {"field": "score"}}
                    }
                }
            }
        })
        for bucket in agg_result["aggregations"]["by_type"]["buckets"]:
            anime_type = bucket["key"]
            avg = bucket["avg_score"]["value"]
            bucket_count = bucket["doc_count"]
            if avg:
                print(f"    {anime_type:12s} : score moyen {avg:.2f} ({bucket_count:,} animes)")

    try:
        ok("Vérification de l'indexation", verify_indexation)
    except Exception:
        sys.exit(1)


    # ============================================
    # 6. RÉSUMÉ FINAL
    # ============================================
    titre("INDEXATION TERMINÉE")

    print(f"""
    {C.BOLD}{C.CYAN}  Index           : {INDEX_NAME}
    Documents       : {count:,}
    Taille          : {size_mb:.1f} MB
    Temps           : {elapsed:.1f}s
    Débit           : {count/elapsed:.0f} docs/s{C.END}

    {C.BOLD}  Accès :{C.END}
    {C.B}📊 Grafana        → http://localhost:3000  (admin / anidata){C.END}
    {C.B}🔍 Elasticsearch  → {ES_HOST}/{INDEX_NAME}/_search{C.END}

    {C.BOLD}  Requêtes utiles :{C.END}
    {C.CYAN}curl http://localhost:9200/{INDEX_NAME}/_count{C.END}
    {C.CYAN}curl "http://localhost:9200/{INDEX_NAME}/_search?q=name:naruto&pretty"{C.END}
    {C.CYAN}curl "http://localhost:9200/{INDEX_NAME}/_search?q=main_genre:Action&size=5&pretty"{C.END}

    {C.BOLD}{C.G}✅ Les données sont prêtes dans Elasticsearch !
    Ouvrez Grafana pour créer vos dashboards.{C.END}
    """)
    
    print(f"Indexation terminée dans {index_name}")

if __name__ == "__main__":
    # Ceci permet de continuer à lancer le script seul si besoin
    run_indexation()
