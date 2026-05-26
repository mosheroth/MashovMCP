"""
Configuration handling for Mashov MCP Server
"""

import os
from typing import Optional
from dotenv import load_dotenv
from mashov_client import MashovClient

# Load .env from this file's directory regardless of CWD
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def load_config() -> Optional[MashovClient]:
    """Load configuration from environment variables"""
    username = os.getenv("MASHOV_USERNAME")
    password = os.getenv("MASHOV_PASSWORD")
    semel = os.getenv("MASHOV_SEMEL")
    year = os.getenv("MASHOV_YEAR")
    
    if not all([username, password, semel, year]):
        return None
    
    client = MashovClient.get_instance()
    client.configure(username, password, semel, year)
    return client


