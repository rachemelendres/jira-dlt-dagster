from dagster import build_schedule_from_partitioned_job, DefaultScheduleStatus
from .jobs import md_jira_ingestion_job

md_jira_ingestion_schedule = build_schedule_from_partitioned_job(
    job=md_jira_ingestion_job,
    hour_of_day=0,
    minute_of_hour=0,
    default_status=DefaultScheduleStatus.STOPPED,
    description="Daily schedule to run the MD Jira API ingestion job",
)
