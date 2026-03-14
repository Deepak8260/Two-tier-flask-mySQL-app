# config.py
# ─────────────────────────────────────────────────────────────────
# Database configuration.
#
# Values are read from environment variables first.
# If an env var is not set, the fallback default is used
# (useful for local development without a .env file).
#
# For production / deployment:
#   1. Copy .env.example  →  .env
#   2. Fill in your real credentials
#   3. The app will pick them up automatically via python-dotenv
# ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load variables from a .env file if one exists (ignored if absent)
load_dotenv()

DB_HOST     = os.environ.get("DB_HOST",     "localhost")
DB_USER     = os.environ.get("DB_USER",     "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_NAME     = os.environ.get("DB_NAME",     "messagesdb")
