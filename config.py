import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_SEARCH_CONSOLE_API_KEY = os.getenv('GOOGLE_SEARCH_CONSOLE_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
GOOGLE_PAGESPEED_API_KEY = 'AIzaSyCdxQK0rcafvp7Leu-1o_H8A6bas5hnEpQ'

# Configuration Settings
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
MAX_PAGES_TO_CRAWL = 100  # Default limit for number of pages to crawl
CRAWL_DELAY = 1  # Default delay between requests in seconds
TIMEOUT = 30  # Default timeout for requests in seconds

# Technical SEO Thresholds
MAX_TITLE_LENGTH = 60
MIN_TITLE_LENGTH = 30
MAX_META_DESCRIPTION_LENGTH = 155
MIN_META_DESCRIPTION_LENGTH = 70
MIN_CONTENT_LENGTH = 300
MAX_URL_LENGTH = 75

# Core Web Vitals Thresholds
LCP_THRESHOLD = 2.5  # seconds
FID_THRESHOLD = 100  # milliseconds
CLS_THRESHOLD = 0.1  # score

# Database Settings
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'seo_audit.db')

# Reporting Settings
REPORT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'reports', 'output')
REPORT_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'reports', 'templates')

# Create a .env.example file if it doesn't exist
env_example_path = os.path.join(os.path.dirname(__file__), '.env.example')
if not os.path.exists(env_example_path):
    with open(env_example_path, 'w') as f:
        f.write("""# API Keys
GOOGLE_SEARCH_CONSOLE_API_KEY=your_google_search_console_api_key
SERPAPI_KEY=your_serpapi_key
#GOOGLE_PAGESPEED_API_KEY=your_pagespeed_api_key
""")
