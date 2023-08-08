"""Utilities for Deta."""


def parse_data_key(data_key: str) -> tuple[str, str]:
    """Get project id and key from data key.

    Args:
        data_key (str): Data key.

    Returns:
        tuple[str, str]: Project id and project key.
    """
    project_id, project_key = data_key.split('_')
    return project_id, project_key
