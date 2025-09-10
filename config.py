import os

RATE_LIMIT = int(os.getenv("RATE_LIMIT", 1))  # req/s
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", 100))
UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://score.hsborges.dev/score")
