from dagster import AssetSelection, define_asset_job

md_jira_ingestion_job = define_asset_job(
    name="md_jira_ingestion",
    selection=AssetSelection.groups("md_jira_ingestion"),
    description="Daily job that ingests Jira API data",
)
