# config.py
from pathlib import Path

# Figshare API
FIGSHARE_API_URL = "https://api.figshare.com/v2"

# Default Figshare Project ID
DEFAULT_FIGSHARE_PROJECT_ID = "30926"

# Default project directory name
DEFAULT_PROJECT_DIRNAME = "earthpy-downloads"

# Default data home when not used with a Project
DEFAULT_DATA_HOME = Path.home() / "earth-analytics" / "data"

# Default exclusions -- hidden files and directories also excluded
DVCIGNORE = [
    "Thumbs.db", 
    ".DS_Store", 
    "__MACOSX", 
    "tmp"
]
DVCIGNORE_TEMPLATE = '\n'.join(
    DVCIGNORE 
    + 
    [
        '*.aux',
        '*.bck',
        '*.bak',
        '*.log',
        '*.out',
        '*.tmp',
        '.*',
    ])

# Data URLs, structured as {'week_name': [(URL, FILENAME, FILETYPE)]}
# If zipfile, tarfile, etc, unzip to a folder w/ the name

DATA_URLS = {
    "co-flood-extras": [
        (
            "https://ndownloader.figshare.com/files/7010681",
            "boulder-precip.csv",
            "file",
        ),
        (
            "https://ndownloader.figshare.com/files/7010681",
            "temperature_example.csv",
            "file",
        ),
    ],
    "colorado-flood": (
        "https://ndownloader.figshare.com/files/16371473",
        ".",
        "zip",
    ),
    "spatial-vector-lidar": (
        "https://ndownloader.figshare.com/files/12459464",
        ".",
        "zip",
    ),
    "cold-springs-modis-h4": (
        "https://ndownloader.figshare.com/files/10960112",
        ".",
        "zip",
    ),
    "cold-springs-fire": (
        "https://ndownloader.figshare.com/files/10960109",
        ".",
        "zip",
    ),
    "cs-test-naip": (
        (
            "https://ndownloader.figshare.com/files/10960211?"
            "private_link=18f892d9f3645344b2fe"
        ),
        ".",
        "zip",
    ),
    "cs-test-landsat": (
        (
            "https://ndownloader.figshare.com/files/10960214?private_link"
            "=fbba903d00e1848b423e"
        ),
        ".",
        "zip",
    ),
    "ndvi-automation": (
        "https://ndownloader.figshare.com/files/13431344",
        ".",
        "zip",
    ),
    "vignette-landsat": (
        "https://ndownloader.figshare.com/files/15197339",
        ".",
        "zip",
    ),
    "vignette-elevation": (
        "https://ndownloader.figshare.com/articles/8259098/versions/2",
        ".",
        "zip",
    ),
    "california-rim-fire": (
        "https://ndownloader.figshare.com/files/14419310",
        ".",
        "zip",
    ),
    "twitter-flood": [
        (
            "https://ndownloader.figshare.com/files/10960175",
            "boulder_flood_geolocated_tweets.json",
            "file",
        )
    ],
    "cold-springs-landsat-scenes": (
        "https://ndownloader.figshare.com/files/21941085 ",
        ".",
        "zip",
    ),
    "naip-fire-crop": (
        "https://ndownloader.figshare.com/files/23070791",
        ".",
        "zip",
    ),
}
