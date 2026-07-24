"""
MuleTrace AI — Logger Utility.

Provides helper for getting named logger instances.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Get a pre-configured logger instance with the given module name.

    Args:
        name: Logger module identifier (e.g. __name__ or 'app.services.account').

    Returns:
        logging.Logger instance.
    """
    return logging.getLogger(name)
