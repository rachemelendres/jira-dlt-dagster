import dlt
from typing import Any, Optional
from dotenv import load_dotenv
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)
from dlt.sources.helpers.rest_client.auth import HttpBasicAuth
from dlt.sources.helpers.rest_client.paginators import JSONResponseCursorPaginator
from dagster import get_dagster_logger
from jira.utils.jira_utils import JiraUtils
from jira.dlt.sources.models.md_jira_issues_model import MdJiraIssuesModel
load_dotenv()

logger = get_dagster_logger()

PARTITION_DATE = '2024-02-23'
@dlt.source(name='md_jira_source', max_table_nesting=0, schema_contract={
  "tables": "evolve",
  "columns": "discard_value",
  "data_type": "freeze"
})
def md_jira_source(partition_date: str = PARTITION_DATE, jira_access_token: Optional[str] = dlt.secrets.value, jira_username: Optional[str] = dlt.secrets.value, cursor: str='nextPageToken') -> Any:
    """Defines the dlt source for MD Jira ingestion. It returns a REST API resource that fetches updated issues from the MD project JIRA board."""
    prev_date = JiraUtils.get_prev_date(partition_date)
    
    logger.info(f'Fetching issues updated on {prev_date} for reporting date: {partition_date}...')
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://domain-name.atlassian.net/rest/api/3/", ## Update the domain name here
            "headers": {"Accept": "application/json"},
            "auth": HttpBasicAuth(username=jira_username, password=jira_access_token) if jira_username and jira_access_token else None,
            "paginator": JSONResponseCursorPaginator(cursor_path=cursor, cursor_param=cursor),
            
        },
        # The default configuration for all resources and their endpoints
        "resource_defaults": {
            "primary_key": ["id", "partition_date"],
            "merge_key": "partition_date",
            "columns": {"updated": {"dedup_sort": "desc"}},
            "write_disposition": "merge",
        },
        "resources": [
            {
                "name": "issues",
                "endpoint": {
                    "path": "search/jql",
                    # Query parameters for the endpoint
                    "params": {
                        "jql": f"project ='MD' and updated >= '{prev_date} 00:00' and updated < '{partition_date} 00:00' order by updated desc",
                        "fields": "*all",
                        "expand": "changelog",
                        "maxResults": 100,
                    },
                },
                "processing_steps": [{"map": JiraUtils.add_fields_from_record(("fields.updated", "updated"), ("fields.created", "created"), ("fields.customfield_10095", "customer_id"))}, {"map": JiraUtils.remove_fields_from_record("expand")}, {"map": JiraUtils.add_partition_date(partition_date=partition_date)}],
                "columns": MdJiraIssuesModel,
            },
        ],
    }
    yield from rest_api_resources(config)

def load_jira():
    pipeline = dlt.pipeline(
        pipeline_name="md_jira",
        destination='duckdb',
        dataset_name="md_jira_issues",
        progress='log'
    )

    load_jira_info = pipeline.run(md_jira_source(partition_date=PARTITION_DATE))
    print(load_jira_info)
    
if __name__ == "__main__":
    load_jira()