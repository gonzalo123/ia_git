import logging

from langchain_core.tools import tool

from .chain import Score

logger = logging.getLogger(__name__)


@tool
def git_alert(status: Score) -> Score:
    """
    This function generates an alert based on the audit score.

    The function takes as input a Score object representing the audit score.
    This score is used to determine the level of the alert that is generated.

    The function returns a Score object representing the audit score.

    Args:
        status (Score): The audit score. This score is used to determine the level of the alert.

    Returns:
        Score: The audit score. This score is used to determine the level of the alert.
    """

    logger.info(f"Audit score: {status.name}")

    return status
