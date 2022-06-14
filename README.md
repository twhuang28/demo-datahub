# Introduction
## Why we need a metadata management platform?
### For data user
* Who own the data? Who manange the data?
* What is the logic and definition of the data?
* Where does the data come from?
* When was the data created? When was it last updated?
* How does the data be updated?
* Is the data of sensitive nature? is the data in good quality?
### For data custodian
* How do I know the lineage of data and application?
* How can I conduct impact analysis when the data changed?

### For data owner
* Who has the access right of data
* Where does my data go?

## Goal
* data quality
* data obserbility
* data governance

## [open source data catalog tools comparison](https://atlan.com/open-source-data-catalog-tools/)

## DataHub Architecture
![](https://datahubproject.io/assets/images/datahub-architecture-30b34a888241e0780c72b7f618137fe4.png)

## Ingestion
* push-based: Airflow, Spark, Great Expectations and Protobuf Schemas
* pull-based: BigQuery, Snowflake, Looker, Tableau
* ![Metadata Ingestion Architecture](https://datahubproject.io/assets/images/ingestion-architecture-cd631d7c4a648ceb82908ce25b9f93b9.png)

### Sources
* Postgres, Elastic Search, Kafka, S3, Metabase, superset, dbt, LDAP...

### Sinks
* DataHub Rest
* DataHub Kafka

## [Metadata model](https://datahubproject.io/docs/metadata-modeling/metadata-model)
* Pegasus schema language ([PDL](https://linkedin.github.io/rest.li/pdl_schema))
* **Entities**: primary node in the metadata graph
    * Data Platform
    * Dataset
    * Chart
    * Dashboard
    * Data Job, Data Flow
* **Aspects**: a collection of attributes that describes a particular facet of an entity
    * [Tags](https://datahubproject.io/docs/tags): Informal, loosely controlled labels that serve as a tool for search & discovery. Assets may have multiple tags. No formal, central management.
    * [Business Glossary](https://datahubproject.io/docs/rfc/active/1842-business_glossary/): A controlled vocabulary, with optional hierarchy. Terms are typically used to standardize types of leaf-level attributes (i.e. schema fields) for governance. E.g. (EMAIL_PLAINTEXT)
    * [Domains](https://datahubproject.io/docs/domains): A set of top-level categories. Usually aligned to business units / disciplines to which the assets are most relevant. Central or distributed management. Single Domain assignment per data asset.
    * ownership
    * status
* **Relationships**: a named edge between 2 entities
    * OwnedBy
    * Contains
* ![](https://datahubproject.io/assets/images/metadata-model-chart-a22bf2c3338dcc0a5d40405dd51e7f13.png)

---

# Demo
## [datahub quick start by doc](https://datahubproject.io/docs/quickstart)
```
python3 -m pip install --upgrade pip wheel setuptools
python3 -m pip uninstall datahub acryl-datahub || true  # sanity check - ok if it fails
python3 -m pip install --upgrade acryl-datahub
python3 -m pip install --upgrade acryl-datahub[postgres]
python3 -m pip install --upgrade acryl-datahub[airflow]
python3 -m pip install --upgrade acryl-datahub-airflow-plugin

python3 -m datahub version
python3 -m datahub docker quickstart
python3 -m datahub docker check
```

## [setup airflow](https://datahubproject.io/docs/docker/airflow/local_airflow)
```
mkdir -p airflow_install
cd airflow_install
# Download docker-compose file
curl -L 'https://raw.githubusercontent.com/datahub-project/datahub/master/docker/airflow/docker-compose.yaml' -o docker-compose.yaml
# Create dags directory
mkdir -p ./dags ./logs ./plugins
# Download a sample DAG
curl -L 'https://raw.githubusercontent.com/datahub-project/datahub/master/metadata-ingestion/src/datahub_provider/example_dags/lineage_backend_demo.py' -o dags/lineage_backend_demo.py

# echo -e "AIRFLOW_UID=$(id -u)" > .env

docker-compose up airflow-init
docker-compose up
```

## Execute SQL in Postgres
```
CREATE USER etlworker;
ALTER USER etlworker WITH PASSWORD 'etlworker';
CREATE DATABASE rawdata;
COMMENT ON DATABASE rawdata IS '原始資料資料庫';
CREATE DATABASE feature;
COMMENT ON DATABASE feature IS '特徵資料資料庫';
GRANT CONNECT ON DATABASE rawdata TO etlworker;
GRANT CONNECT ON DATABASE feature TO etlworker;

\c rawdata
CREATE SCHEMA mlaas_rawdata;
COMMENT ON SCHEMA mlaas_rawdata IS '基礎共用之分析資料';
CREATE TABLE mlaas_rawdata.cm_customer(cust_no character varying, age integer, etl_dt date);
COMMENT ON TABLE mlaas_rawdata.cm_customer IS '顧客層之資料';
COMMENT ON COLUMN mlaas_rawdata.cm_customer.cust_no IS '顧客ID';
COMMENT ON COLUMN mlaas_rawdata.cm_customer.age IS '顧客年齡';
COMMENT ON COLUMN mlaas_rawdata.cm_customer.etl_dt IS '處理日期';
INSERT INTO mlaas_rawdata.cm_customer VALUES('A123456789',50,now()),('A123111111',20,now()),('A122222222',10,now());

GRANT USAGE ON SCHEMA mlaas_rawdata TO etlworker;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mlaas_rawdata TO etlworker;

CREATE USER esb13131;
ALTER USER esb13131 WITH PASSWORD 'esb13131';
GRANT USAGE ON SCHEMA mlaas_rawdata TO esb13131;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mlaas_rawdata TO esb13131;
select * from mlaas_rawdata.cm_customer ;

\c feature
```

## [ingest postgres](./postgres_recipe.yaml)
```
python3 -m datahub ingest -c postgres_recipe.yaml
```

### outcome
```
[2022-04-26 11:11:55,980] INFO     {datahub.cli.ingest_cli:96} - DataHub CLI version: 0.8.33.1
[2022-04-26 11:12:00,561] INFO     {datahub.cli.ingest_cli:112} - Starting metadata ingestion
[2022-04-26 11:12:00,860] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-info-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2
[2022-04-26 11:12:00,972] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-platforminstance-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2
[2022-04-26 11:12:01,075] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-subtypes-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2
[2022-04-26 11:12:01,146] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-info-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff
[2022-04-26 11:12:01,186] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-platforminstance-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff
[2022-04-26 11:12:01,231] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-subtypes-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff
[2022-04-26 11:12:01,268] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-parent-container-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff-urn:li:container:5f5848763cea57c328ee47e3b4200db2
[2022-04-26 11:12:01,473] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-urn:li:container:ef6b56668ad78753c94757ff0516fdff-to-urn:li:dataset:(urn:li:dataPlatform:postgres,DatabaseNameToBeIngested.mlaas_rawdata.cm_customer,PROD)
[2022-04-26 11:12:01,911] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit DatabaseNameToBeIngested.mlaas_rawdata.cm_customer
[2022-04-26 11:12:02,249] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit DatabaseNameToBeIngested.mlaas_rawdata.cm_customer-subtypes
[2022-04-26 11:12:02,384] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-info-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a
[2022-04-26 11:12:02,553] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-platforminstance-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a
[2022-04-26 11:12:02,601] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-subtypes-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a
[2022-04-26 11:12:02,633] INFO     {datahub.ingestion.run.pipeline:84} - sink wrote workunit container-parent-container-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a-urn:li:container:5f5848763cea57c328ee47e3b4200db2
[2022-04-26 11:12:02,633] INFO     {datahub.cli.ingest_cli:130} - Finished metadata pipeline

Source (postgres) report:
{'workunits_produced': 14,
 'workunit_ids': ['container-info-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2',
                  'container-platforminstance-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2',
                  'container-subtypes-rawdata-urn:li:container:5f5848763cea57c328ee47e3b4200db2',
                  'container-info-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff',
                  'container-platforminstance-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff',
                  'container-subtypes-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff',
                  'container-parent-container-mlaas_rawdata-urn:li:container:ef6b56668ad78753c94757ff0516fdff-urn:li:container:5f5848763cea57c328ee47e3b4200db2',
                  'container-urn:li:container:ef6b56668ad78753c94757ff0516fdff-to-urn:li:dataset:(urn:li:dataPlatform:postgres,DatabaseNameToBeIngested.mlaas_rawdata.cm_customer,PROD)',
                  'DatabaseNameToBeIngested.mlaas_rawdata.cm_customer',
                  'DatabaseNameToBeIngested.mlaas_rawdata.cm_customer-subtypes',
                  'container-info-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a',
                  'container-platforminstance-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a',
                  'container-subtypes-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a',
                  'container-parent-container-public-urn:li:container:be3be7df8b9d1f9472118d7dafb2308a-urn:li:container:5f5848763cea57c328ee47e3b4200db2'],
 'warnings': {},
 'failures': {},
 'cli_version': '0.8.33.1',
 'cli_entry_location': '/Users/esb17957/Library/Python/3.8/lib/python/site-packages/datahub/__init__.py',
 'py_version': '3.8.2 (default, Dec 21 2020, 15:06:04) \n[Clang 12.0.0 (clang-1200.0.32.29)]',
 'py_exec_path': '/Library/Developer/CommandLineTools/usr/bin/python3',
 'os_details': 'macOS-11.2.3-x86_64-i386-64bit',
 'tables_scanned': 1,
 'views_scanned': 0,
 'entities_profiled': 0,
 'filtered': ['information_schema.*'],
 'soft_deleted_stale_entities': [],
 'query_combiner': None}
Sink (datahub-rest) report:
{'records_written': 14,
 'warnings': [],
 'failures': [],
 'downstream_start_time': datetime.datetime(2022, 4, 26, 11, 12, 0, 678692),
 'downstream_end_time': datetime.datetime(2022, 4, 26, 11, 12, 2, 633296),
 'downstream_total_latency_in_seconds': 1.954604,
 'gms_version': 'v0.8.33'}

Pipeline finished successfully
```