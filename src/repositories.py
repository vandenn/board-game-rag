from dagster import repository

from src.jobs import ingest_board_game_rules
from src.schedules import ingest_board_game_rules_schedule


# Boilerplate code for registering the job and schedule.
@repository
def board_game_rules():
    return {
        "jobs": {
            "ingest_board_game_rules": ingest_board_game_rules,
        },
        "schedules": {
            "ingest_board_game_rules_schedule": ingest_board_game_rules_schedule
        },
    }
