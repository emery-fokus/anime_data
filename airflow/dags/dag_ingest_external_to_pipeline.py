from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
import os

from airflow import DAG
from airflow.decorators import task
from airflow.utils import timezone


BASE_DIR = os.path.dirname(__file__)
SCRIPTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "scripts")


def load_callable(script_name, function_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    module_name = os.path.splitext(script_name)[0].replace(".", "_")
    spec = spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name, None)


list_pending_input_files = load_callable("00_format_to_csv.py", "list_pending_input_files")
convert_input_file_to_csv = load_callable("00_format_to_csv.py", "convert_input_file_to_csv")
archive_input_file = load_callable("00_format_to_csv.py", "archive_input_file")
merge_converted_csvs = load_callable("00_format_to_csv.py", "merge_converted_csvs")


with DAG(
    dag_id="anidata_ingest_external_to_pipeline",
    start_date=datetime(2026, 3, 26),
    schedule_interval="*/5 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["anidata", "ingest", "xml", "json", "auto"],
    params={
        "input_file": "",
    },
    description="Scanne input/, convertit tous les fichiers XML/JSON en CSV puis déclenche le pipeline principal",
) as dag:
    @task
    def collect_input_files(**context):
        dag_run = context.get("dag_run")
        manual_input_file = None
        if dag_run and dag_run.conf:
            manual_input_file = dag_run.conf.get("input_file")

        files = list_pending_input_files(single_input_file=manual_input_file)
        print(f"Fichiers détectés : {files}")
        return files

    @task
    def process_input_file(input_file):
        processed = convert_input_file_to_csv(input_file)
        print(f"Fichier converti : {processed}")
        return processed

    @task
    def merge_processed_files(processed_files):
        processed_files = [dict(item) for item in list(processed_files or [])]
        merged = merge_converted_csvs(processed_files)
        if not merged:
            print("Aucun fichier à fusionner, aucun déclenchement du pipeline principal.")
            return None

        result = {
            "csv_path": merged["csv_path"],
            "processed_files": [dict(item) for item in merged["processed_files"]],
        }
        print(f"CSV fusionné prêt : {result['csv_path']}")
        return result

    @task
    def trigger_main_pipeline(merged):
        from airflow.api.common.trigger_dag import trigger_dag

        if not merged:
            return None

        csv_path = merged["csv_path"]
        run_id = f"ingest__merged__{timezone.utcnow().strftime('%Y%m%dT%H%M%S')}"

        trigger_dag(
            dag_id="anidata_lab_etl_full",
            run_id=run_id,
            conf={
                "input_csv": csv_path,
                "source_files": [item["input_file"] for item in merged["processed_files"]],
                "file_formats": [item["file_format"] for item in merged["processed_files"]],
            },
            execution_date=None,
            replace_microseconds=False,
        )

        print(f"Pipeline principal déclenché pour : {csv_path}")
        return merged

    @task
    def archive_source_file(processed):
        archived_path = archive_input_file(processed["input_file"])
        processed["archived_input_file"] = archived_path
        return processed

    pending_files = collect_input_files()
    processed_files = process_input_file.expand(input_file=pending_files)
    merged_file = merge_processed_files(processed_files)
    triggered_pipeline = trigger_main_pipeline(merged_file)
    archived_files = archive_source_file.expand(processed=processed_files)

    triggered_pipeline >> archived_files
