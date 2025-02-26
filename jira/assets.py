from dagster import AssetExecutionContext, AssetKey, SourceAsset
from dagster_dlt import DagsterDltResource, dlt_assets, DagsterDltTranslator
from dlt import pipeline
from dlt.extract.resource import DltResource
from .dlt.sources.md import md_jira_source
from .partitions import daily_partitions_def

class MdJiraDagsterDltTranslator(DagsterDltTranslator):
    
    def get_asset_key(self, resource: DltResource) -> AssetKey:
        """Overrides the default asset key for the dlt resource"""
        return AssetKey([f"md_jira_{resource.name}"])
    
    def get_description(self, resource: DltResource) -> str | None:
        """Overrides the default asset description for the dlt resource"""
        base_description = super().get_description(resource)
        if base_description:
            return base_description
        else:
            return f"A Dlt resource: `{resource.name}` for MD Jira Ingestion"

@dlt_assets(
    dlt_source=md_jira_source(),
    dlt_pipeline=pipeline(
        pipeline_name="md_jira",
        dataset_name="md_jira_issues",
        destination="duckdb",
        progress="log",
    ),
    name="md_jira",
    group_name="md_jira_ingestion",
    dagster_dlt_translator=MdJiraDagsterDltTranslator(),
    partitions_def=daily_partitions_def,
)
def md_jira_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context, dlt_source=md_jira_source(partition_date=context.partition_key))
    
md_jira_source_assets = [
    SourceAsset(key, group_name="md_jira_ingestion") for key in md_jira_assets.dependency_keys
]