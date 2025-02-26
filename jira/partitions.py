from dagster import DailyPartitionsDefinition


daily_partitions_def = DailyPartitionsDefinition(
    start_date='2024-02-25',
    timezone="US/Pacific",
    end_offset=1,
)