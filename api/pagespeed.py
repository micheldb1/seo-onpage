#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

from config import GOOGLE_PAGESPEED_API_KEY

class PageSpeedAPI:
    def __init__(self):
        self.api_key = GOOGLE_PAGESPEED_API_KEY
        self.base_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    
    def analyze(self, url, strategy='mobile'):
        """Analyze a URL using Google PageSpeed Insights API
        
        Args:
            url (str): The URL to analyze
            strategy (str): Either 'mobile' or 'desktop'
            
        Returns:
            dict: PageSpeed analysis results
        """
        if not self.api_key:
            return {
                'error': 'Google PageSpeed API key is not configured',
                'status': 'error'
            }
        
        params = {
            'url': url,
            'strategy': strategy,
            'key': self.api_key,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                return self._parse_results(response.json())
            else:
                return {
                    'error': f'API request failed with status code {response.status_code}',
                    'status': 'error'
                }
        except Exception as e:
            return {
                'error': f'API request failed: {str(e)}',
                'status': 'error'
            }
    
    def _parse_results(self, data):
        """Parse PageSpeed API results
        
        Args:
            data (dict): Raw API response
            
        Returns:
            dict: Parsed and simplified results
        """
        results = {
            'status': 'success',
            'lighthouse_scores': {},
            'core_web_vitals': {},
            'opportunities': []
        }
        
        # Extract Lighthouse scores
        if 'lighthouseResult' in data and 'categories' in data['lighthouseResult']:
            categories = data['lighthouseResult']['categories']
            for category_name, category_data in categories.items():
                results['lighthouse_scores'][category_name] = {
                    'score': category_data.get('score', 0) * 100,  # Convert to percentage
                    'title': category_data.get('title', '')
                }
        
        # Extract Core Web Vitals
        if 'loadingExperience' in data and 'metrics' in data['loadingExperience']:
            metrics = data['loadingExperience']['metrics']
            
            # LCP - Largest Contentful Paint
            if 'LARGEST_CONTENTFUL_PAINT_MS' in metrics:
                lcp_data = metrics['LARGEST_CONTENTFUL_PAINT_MS']
                results['core_web_vitals']['lcp'] = {
                    'value': lcp_data.get('percentile', 0) / 1000,  # Convert to seconds
                    'category': lcp_data.get('category', '')
                }
            
            # FID - First Input Delay
            if 'FIRST_INPUT_DELAY_MS' in metrics:
                fid_data = metrics['FIRST_INPUT_DELAY_MS']
                results['core_web_vitals']['fid'] = {
                    'value': fid_data.get('percentile', 0),  # In milliseconds
                    'category': fid_data.get('category', '')
                }
            
            # CLS - Cumulative Layout Shift
            if 'CUMULATIVE_LAYOUT_SHIFT_SCORE' in metrics:
                cls_data = metrics['CUMULATIVE_LAYOUT_SHIFT_SCORE']
                results['core_web_vitals']['cls'] = {
                    'value': cls_data.get('percentile', 0) / 100,  # Normalize
                    'category': cls_data.get('category', '')
                }
        
        # Extract improvement opportunities
        if 'lighthouseResult' in data and 'audits' in data['lighthouseResult']:
            audits = data['lighthouseResult']['audits']
            for audit_id, audit_data in audits.items():
                if audit_data.get('score', 1) < 1 and 'details' in audit_data:
                    opportunity = {
                        'id': audit_id,
                        'title': audit_data.get('title', ''),
                        'description': audit_data.get('description', ''),
                        'score': audit_data.get('score', 0) * 100,  # Convert to percentage
                        'impact': 'high' if audit_data.get('score', 1) < 0.5 else 'medium'
                    }
                    results['opportunities'].append(opportunity)
        
        return results
