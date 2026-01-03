import logging

# Initializing the logger with basic configuration
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define the log format
)

logger = logging.getLogger("movie_rating")  # Create a logger named 'movie_rating'

# Testing log with a basic info message
logger.info("Logging system initialized.")
