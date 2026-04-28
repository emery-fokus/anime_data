from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
import inspect
import time
import traceback
import sys
import os

# Ajout du chemin pour que Airflow trouve tes scripts 01, 02, etc.
BASE_DIR = os.path.dirname(__file__)
SCRIPTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "scripts")
sys.path.append(BASE_DIR)


def load_callable(script_name, function_name):
    """Charge une fonction depuis un fichier Python numéroté."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return None

    module_name = os.path.splitext(script_name)[0].replace(".", "_")
    spec = spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name, None)


run_exploration = load_callable("01_exploration.py", "run_exploration")
run_nettoyage = load_callable("02_nettoyage.py", "run_nettoyage")
run_normalisation = load_callable("03_normalisation.py", "run_normalisation")
run_validation = load_callable("04_validation.py", "run_validation")
run_indexation = load_callable("05_send_to_elasticsearch.py", "run_indexation")


def audit_error(task_name, error):
    """Affiche un audit court de l'erreur pour la tâche."""
    print(f"[AUDIT] task={task_name}")
    print(f"[AUDIT] error_type={type(error).__name__}")
    print(f"[AUDIT] error_message={error}")
    trace_lines = traceback.format_exc().strip().splitlines()
    if trace_lines:
        print(f"[AUDIT] trace={trace_lines[-1]}")


def prepare_task_kwargs(task_callable, kwargs):
    """Ne conserve que les kwargs acceptés par la fonction cible."""
    if task_callable is None:
        return kwargs

    signature = inspect.signature(task_callable)
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kwargs:
        return kwargs

    allowed_names = {
        name for name, parameter in signature.parameters.items()
        if parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    return {key: value for key, value in kwargs.items() if key in allowed_names}


def ok(task_name, task_callable, **kwargs):
    """Exécute la tâche une première fois."""
    print(f"[OK] Exécution de la tâche '{task_name}'")
    if task_callable is None:
        raise ValueError(f"Callable introuvable pour la tâche '{task_name}'")
    return task_callable(**prepare_task_kwargs(task_callable, kwargs))


def ko(task_name, task_callable, error, wait_seconds=30, **kwargs):
    """Audite l'erreur, attend, puis retente une seconde fois."""
    print(f"[KO] Échec de la tâche '{task_name}', nouvelle tentative dans {wait_seconds}s")
    audit_error(task_name, error)
    time.sleep(wait_seconds)
    if task_callable is None:
        raise ValueError(f"Callable introuvable pour la tâche '{task_name}'")
    print(f"[KO] Relance de la tâche '{task_name}'")
    return task_callable(**prepare_task_kwargs(task_callable, kwargs))


def run_task(task_name, task_callable, **kwargs):
    """Applique la logique ok/ko indépendante à chaque tâche."""
    try:
        return ok(task_name, task_callable, **kwargs)
    except Exception as error:
        return ko(task_name, task_callable, error, **kwargs)

# ============================================
# CONFIGURATION DU DAG
# ============================================

default_args = {
    'owner': 'oskano',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'anidata_lab_etl_full',
    default_args=default_args,
    description='Pipeline ETL Anime - De l exploration à Elasticsearch',
    schedule_interval='@daily',
    catchup=False,
    tags=['anidata', 'etl', 'elasticsearch'],
) as dag:

    # 1. Tâche Exploration (Ton fichier 01)
    task_exploration = PythonOperator(
        task_id='exploration_data',
        python_callable=run_task,
        op_kwargs={
            'task_name': 'exploration_data',
            'task_callable': run_exploration,
        },
        doc_md="Audit de la qualité des données initiales (anime.csv, synopsis.csv)",
    )

    # 2. Tâche Nettoyage (Ton fichier 02)
    task_nettoyage = PythonOperator(
        task_id='nettoyage_donnees',
        python_callable=run_task,
        op_kwargs={
            'task_name': 'nettoyage_donnees',
            'task_callable': run_nettoyage,
            'input_file': "{{ dag_run.conf.get('input_csv', '/opt/airflow/data/anime.csv') if dag_run else '/opt/airflow/data/anime.csv' }}",
        },
        doc_md="Suppression des doublons et traitement des 'Unknown'",
    )

    # 3. Tâche Normalisation (Ton fichier 03)
    task_normalisation = PythonOperator(
        task_id='normalisation_features',
        python_callable=run_task,
        op_kwargs={
            'task_name': 'normalisation_features',
            'task_callable': run_normalisation,
        },
        doc_md="Création de nouvelles features (durée, popularité...)",
    )

    # 4. Tâche Validation (Ton fichier 04)
    task_validation = PythonOperator(
        task_id='validation_finale',
        python_callable=run_task,
        op_kwargs={
            'task_name': 'validation_finale',
            'task_callable': run_validation,
        },
        doc_md="Vérification de l'intégrité avant l'envoi vers l'index",
    )

    # 5. Tâche Envoi Elasticsearch (Ton fichier 05)
    task_load_es = PythonOperator(
        task_id='load_to_elasticsearch',
        python_callable=run_task,
        op_kwargs={
            'task_name': 'load_to_elasticsearch',
            'task_callable': run_indexation,
            'index_name': 'anime_final',
        },
        doc_md="Envoi en bulk vers Elasticsearch pour visualisation Grafana",
    )

    # ============================================
    # ORCHESTRATION DES TÂCHES (Le Pipeline)
    # ============================================
    task_exploration >> task_nettoyage >> task_normalisation >> task_validation >> task_load_es
# bonjour