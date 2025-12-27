import logging
from agent.config import config

def setup_tracing():
    """Configures logging and tracing for the agent."""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("agent")
    return logger

logger = setup_tracing()
