from typing import List

import datahub.emitter.mce_builder as builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.com.linkedin.pegasus2avro.datajob import DataJobInputOutputClass
from datahub.metadata.schema_classes import ChangeTypeClass

# Construct the DataJobInputOutput aspect.
input_datasets: List[str] = [
    builder.make_dataset_urn(platform="postgres", name="feature_db.if_polaris.customer_feature", env="PROD"),
    builder.make_dataset_urn(platform="postgres", name="rawdata_db.mlaas_rawdata.cm_customer", env="PROD"),
]

output_datasets: List[str] = [
    builder.make_dataset_urn(
        platform="kafka", name="debezium.topics.wm_robo_advisor.job_done", env="PROD"
    ),
    builder.make_dataset_urn(
        platform="postgres", name="feature_db.wm_robo_advisor.feature_table", env="PROD"
    )
]

input_data_jobs: List[str] = [
    builder.make_data_job_urn(
        orchestrator="airflow", flow_id="wm_robo_advisor.feature_engineer", job_id="feature_etl", cluster="PROD"
    )
]

datajob_input_output = DataJobInputOutputClass(
    inputDatasets=input_datasets,
    outputDatasets=output_datasets,
    inputDatajobs=input_data_jobs,
)

# Construct a MetadataChangeProposalWrapper object.
# NOTE: This will overwrite all of the existing lineage information associated with this job.
datajob_input_output_mcp = MetadataChangeProposalWrapper(
    entityType="dataJob",
    changeType=ChangeTypeClass.UPSERT,
    entityUrn=builder.make_data_job_urn(
        orchestrator="airflow", flow_id="wm_robo_advisor.feature_engineer", job_id="feature_etl", cluster="PROD"
    ),
    aspectName="dataJobInputOutput",
    aspect=datajob_input_output,
)

# Create an emitter to the GMS REST API.
emitter = DatahubRestEmitter("http://localhost:8080")

# Emit metadata!
emitter.emit_mcp(datajob_input_output_mcp)