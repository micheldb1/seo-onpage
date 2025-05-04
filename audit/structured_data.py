#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import re

from config import DEFAULT_USER_AGENT, TIMEOUT

class StructuredDataAudit:
    def __init__(self, url):
        self.url = url
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
        self.structured_data = []
    
    def run_audit(self):
        """Run all structured data audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.soup = BeautifulSoup(response.text, 'html.parser')
            
            self.extract_structured_data()
            self.check_schema_types()
            self.check_schema_completeness()
            self.check_open_graph()
            self.check_twitter_cards()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform structured data audit: {str(e)}'
            }
            return self.results
    
    def extract_structured_data(self):
        """Extract structured data from the page"""
        if not self.soup:
            return
        
        # Find all script tags with type="application/ld+json"
        ld_json_scripts = self.soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in ld_json_scripts:
            try:
                data = json.loads(script.string)
                self.structured_data.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Check if structured data was found
        if self.structured_data:
            self.results['structured_data_present'] = {
                'value': True,
                'status': 'good',
                'message': f'Found {len(self.structured_data)} structured data blocks'
            }
        else:
            self.results['structured_data_present'] = {
                'value': False,
                'status': 'warning',
                'message': 'No structured data found on the page'
            }
    
    def check_schema_types(self):
        """Check schema.org types used in structured data"""
        if not self.structured_data:
            self.results['schema_types'] = {
                'value': None,
                'status': 'warning',
                'message': 'No structured data to analyze'
            }
            return
        
        schema_types = []
        
        for data in self.structured_data:
            # Extract @type from the data
            if isinstance(data, dict):
                schema_type = self._extract_type(data)
                if schema_type:
                    schema_types.extend(schema_type if isinstance(schema_type, list) else [schema_type])
        
        # Remove duplicates
        schema_types = list(set(schema_types))
        
        # Check if common schema types are used
        common_types = ['WebPage', 'Article', 'Product', 'Organization', 'LocalBusiness', 'Person', 'BreadcrumbList']
        has_common_type = any(common_type in schema_types for common_type in common_types)
        
        self.results['schema_types'] = {
            'value': schema_types,
            'status': 'good' if has_common_type else 'warning',
            'message': 'Common schema types found' if has_common_type else 'No common schema types found'
        }
    
    def _extract_type(self, data, types=None):
        """Recursively extract @type from structured data"""
        if types is None:
            types = []
        
        if isinstance(data, dict):
            if '@type' in data:
                types.append(data['@type'])
            
            # Recursively check nested objects
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._extract_type(value, types)
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_type(item, types)
        
        return types
    
    def check_schema_completeness(self):
        """Check if structured data is complete"""
        if not self.structured_data:
            self.results['schema_completeness'] = {
                'value': None,
                'status': 'warning',
                'message': 'No structured data to analyze'
            }
            return
        
        completeness_issues = []
        
        for data in self.structured_data:
            if isinstance(data, dict):
                # Check for required properties based on schema type
                if '@type' in data:
                    schema_type = data['@type']
                    
                    if schema_type == 'Article' or schema_type == 'BlogPosting':
                        required_props = ['headline', 'author', 'datePublished', 'image']
                        missing_props = [prop for prop in required_props if prop not in data]
                        if missing_props:
                            completeness_issues.append(f'{schema_type} missing properties: {", ".join(missing_props)}')
                    
                    elif schema_type == 'Product':
                        required_props = ['name', 'image', 'description', 'offers']
                        missing_props = [prop for prop in required_props if prop not in data]
                        if missing_props:
                            completeness_issues.append(f'{schema_type} missing properties: {", ".join(missing_props)}')
                    
                    elif schema_type == 'LocalBusiness':
                        required_props = ['name', 'address', 'telephone']
                        missing_props = [prop for prop in required_props if prop not in data]
                        if missing_props:
                            completeness_issues.append(f'{schema_type} missing properties: {", ".join(missing_props)}')
        
        self.results['schema_completeness'] = {
            'value': completeness_issues,
            'status': 'good' if not completeness_issues else 'warning',
            'message': 'Structured data is complete' if not completeness_issues else '; '.join(completeness_issues)
        }
    
    def check_open_graph(self):
        """Check Open Graph meta tags"""
        if not self.soup:
            return
        
        og_tags = self.soup.find_all('meta', property=re.compile('^og:'))
        
        if not og_tags:
            self.results['open_graph'] = {
                'value': None,
                'status': 'warning',
                'message': 'No Open Graph meta tags found'
            }
            return
        
        og_data = {}
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            og_data[property_name] = content
        
        # Check for required Open Graph properties
        required_props = ['title', 'type', 'image', 'url']
        missing_props = [prop for prop in required_props if prop not in og_data]
        
        self.results['open_graph'] = {
            'value': og_data,
            'status': 'good' if not missing_props else 'warning',
            'message': 'Open Graph tags are complete' if not missing_props else f'Missing Open Graph properties: {", ".join(missing_props)}'
        }
    
    def check_twitter_cards(self):
        """Check Twitter Card meta tags"""
        if not self.soup:
            return
        
        twitter_tags = self.soup.find_all('meta', attrs={'name': re.compile('^twitter:')})  
        
        if not twitter_tags:
            self.results['twitter_cards'] = {
                'value': None,
                'status': 'info',  # Not critical but good to have
                'message': 'No Twitter Card meta tags found'
            }
            return
        
        twitter_data = {}
        for tag in twitter_tags:
            property_name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            twitter_data[property_name] = content
        
        # Check for card type
        has_card_type = 'card' in twitter_data
        
        # Check for required properties based on card type
        card_type = twitter_data.get('card')
        missing_props = []
        
        if card_type == 'summary':
            required_props = ['title', 'description']
            missing_props = [prop for prop in required_props if prop not in twitter_data]
        elif card_type == 'summary_large_image':
            required_props = ['title', 'description', 'image']
            missing_props = [prop for prop in required_props if prop not in twitter_data]
        
        self.results['twitter_cards'] = {
            'value': twitter_data,
            'status': 'good' if has_card_type and not missing_props else 'warning',
            'message': 'Twitter Card tags are complete' if has_card_type and not missing_props else 
                      'Missing Twitter Card type' if not has_card_type else 
                      f'Missing Twitter Card properties: {", ".join(missing_props)}'
        }
