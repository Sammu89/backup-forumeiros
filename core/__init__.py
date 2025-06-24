# __init__.py

"""
Forum Backup Crawler
====================

A package to mirror an online forum (phpBB/Forumeiros) for offline browsing.
It provides:

• A CLI entrypoint (`cli.py`)  
• Configuration management (`config.py`)  
• Network layers (rate limiting, HTTP client, auth)  
• Storage (SQLite state, asset caching, path mapping)  
• Processing (HTML rewriting, link discovery)  
• Core orchestration (scheduler, worker)  
• Utilities (typing protocols, timing helpers)  

To run from the command line:
    python -m forum_backup_crawler.cli [options]
"""

__version__ = "0.1.0"

# Expose the main CLI app at the package level
from .cli import app  # Typer application
