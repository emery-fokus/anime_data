


from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'emery',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="03_scraper_myanimelist_final",
    default_args=default_args,
    description="Scraping piloté par l'artefact GitHub",
    schedule_interval=None, 
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['anidata', 'github_api', 'scraper'],
) as dag:

    # Tâche 1 : Vérifie la présence du script
    check_script = BashOperator(
        task_id="check_github_artifact",
        bash_command='if [ -f "/opt/airflow/scripts/scrape_mock_site.py" ]; then echo "OK"; else echo "Fichier introuvable" && exit 1; fi',
    )

    # Tâche 2 : Exécution du scraper
    run_scraper = BashOperator(
        task_id="run_scraper_from_artifact",
        bash_command='python /opt/airflow/scripts/scrape_mock_site.py',
    )

    # Tâche 3 : Vérification de la sortie
    check_output = BashOperator(
        task_id="verify_data_output",
        bash_command='if [ -f "/opt/airflow/data/scraped/anime_scraped.json" ]; then echo "✅ Terminé"; else echo "❌ Fichier non trouvé" && exit 1; fi',
    )

    check_script >> run_scraper >> check_output