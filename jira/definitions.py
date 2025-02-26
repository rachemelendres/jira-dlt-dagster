import warnings
from dagster import Definitions, load_assets_from_modules, ExperimentalWarning
from dagster_dlt import DagsterDltResource
from . import assets, jobs, schedules

warnings.filterwarnings("ignore", category=ExperimentalWarning)

dlt_resource = DagsterDltResource()
all_assets = load_assets_from_modules([assets])
defs = Definitions(
    assets=all_assets,
    schedules=[schedules.md_jira_ingestion_schedule],
    jobs=[jobs.md_jira_ingestion_job],
    resources={
        "dlt": dlt_resource,
    },
)