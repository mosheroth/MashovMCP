"""
Configuration handling for Mashov MCP Server
"""

import os
from typing import Optional
from dotenv import load_dotenv
from mashov_client import MashovClient

# Load environment variables
load_dotenv()


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


