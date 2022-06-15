"""Lineage Backend

An example DAG demonstrating the usage of DataHub's Airflow lineage backend.
"""

from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago

from airflow.providers.postgres.operators.postgres import PostgresOperator

from datahub_provider.entities import Dataset

default_args = {
    "owner": "esb13131",
    "depends_on_past": False,
    "email": ["jdoe@example.com"],
    "email_on_failure": False,
    "execution_timeout": timedelta(minutes=5),
}


with DAG(
    "if_polaris.customer_feature",
    default_args=default_args,
    description="feature ETL for if_polaris.customer_feature",
    schedule_interval="@once",
    start_date=days_ago(2),
    tags=["if_polaris"],
    catchup=False,
) as dag:
    task1 = PostgresOperator(
        task_id="run_feature_etl",
        dag=dag,
        postgres_conn_id='if_polaris.feature_db',
        sql="sql/customer_feature.sql",
        inlets={
            "datasets": [
                Dataset("postgres", "rawdata_db.mlaas_limit.cdtx0001"),
                Dataset("postgres", "rawdata_db.mlaas_rawdata.cm_customer")
            ],
        },
        outlets={"datasets": [Dataset("postgres", "feature_db.if_polaris.customer_feature")]},
    )
