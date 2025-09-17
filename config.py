import os
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# Lê variáveis do ambiente ou usa valores padrão
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 1))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", 100))
UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://score.hsborges.dev/score")
