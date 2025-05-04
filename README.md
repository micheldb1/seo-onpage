# Comprehensive On-Page SEO Audit Tool

This tool audits over 45 on-page SEO factors for any website, providing detailed analysis and actionable recommendations.

## Features

- **Technical SEO Analysis**: Status codes, canonical tags, robots.txt, SSL, Core Web Vitals, and more
- **Content SEO Analysis**: Title tags, meta descriptions, heading structure, content quality, and keyword usage
- **Structured Data Validation**: Schema markup implementation and validation
- **Link Analysis**: Internal/external link structure, anchor text relevance, broken links
- **UX Factors**: Image optimization, mobile UX, page layout, CTA effectiveness
- **Advanced SEO Metrics**: JavaScript rendering, SERP feature targeting, semantic analysis

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure your API keys in `config.py`
3. Run the main application: `python app.py`

## Requirements

- Python 3.8+
- API keys for Google Search Console, SERPAPI, and other services as specified in the config file

## Project Structure

- `app.py`: Main application entry point
- `config.py`: Configuration settings and API keys
- `audit/`: Core audit modules for different SEO categories
- `utils/`: Utility functions and helpers
- `data/`: Data storage and processing
- `api/`: API integrations
- `ui/`: User interface components
- `reports/`: Report generation modules
