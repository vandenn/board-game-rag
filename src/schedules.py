# If planning to deploy and turn this ingestion into a regularly running job,
# configuring this schedule will be important and will depend on
# how often you need the data refreshed. Cron schedule will determine this.

from dagster import schedule

from src import jobs


@schedule(
    cron_schedule="30 13 * * *",
    job=jobs.ingest_board_game_rules,
    execution_timezone="Asia/Singapore",
)
def ingest_board_game_rules_schedule(context):
    # If any configuration needs to happen, config changes can happen here.
    return {}
