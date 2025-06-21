"""
Runtime settings populated at start-up by **main.py**
and imported by all other internal modules.
"""

# These get filled in main.py **before** the crawler starts.
BASE_URL: str = ""          # full scheme+host, e.g. https://sm-portugal.forumeiros.com
BASE_DOMAIN: str = ""       # just host, e.g. sm-portugal.forumeiros.com
BACKUP_ROOT = None          # Path object pointing to Desktop/<slug>