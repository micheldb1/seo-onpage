#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

from config import SERPAPI_KEY

class SERPAPI:
    def __init__(self):
        self.api_key = SERPAPI_KEY
        self.base_url = 'https://serpapi.com/search'
    
    def search(self, query, location='United States', device='desktop', num=10):
        """Perform a search using SERPAPI
        
        Args:
            query (str): Search query
            location (str): Location for search results
            device (str): Device type ('desktop' or 'mobile')
            num (int): Number of results to return
            
        Returns:
            dict: Search results
        """
        if not self.api_key:
            return {
                'error': 'SERPAPI key is not configured',
                'status': 'error'
            }
        
        params = {
            'q': query,
            'location': location,
            'device': device,
            'num': num,
            'api_key': self.api_key
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
    
    def analyze_serp_features(self, query):
        """Analyze SERP features for a query
        
        Args:
            query (str): Search query
            
        Returns:
            dict: SERP features analysis
        """
        search_results = self.search(query)
        
        if 'error' in search_results:
            return search_results
        
        # Extract SERP features
        features = {
            'featured_snippet': False,
            'knowledge_graph': False,
            'local_pack': False,
            'top_stories': False,
            'images': False,
            'videos': False,
            'shopping': False,
            'twitter': False,
            'faq': False
        }
        
        if 'answer_box' in search_results:
            features['featured_snippet'] = True
        
        if 'knowledge_graph' in search_results:
            features['knowledge_graph'] = True
        
        if 'local_results' in search_results:
            features['local_pack'] = True
        
        if 'top_stories' in search_results:
            features['top_stories'] = True
        
        if 'images_results' in search_results:
            features['images'] = True
        
        if 'videos_results' in search_results:
            features['videos'] = True
        
        if 'shopping_results' in search_results:
            features['shopping'] = True
        
        if 'twitter_results' in search_results:
            features['twitter'] = True
        
        # Check for FAQ results in organic results
        if 'organic_results' in search_results:
            for result in search_results['organic_results']:
                if 'sitelinks' in result and 'expanded' in result['sitelinks']:
                    features['faq'] = True
                    break
        
        return {
            'status': 'success',
            'query': query,
            'features': features,
            'opportunities': self._get_feature_opportunities(features)
        }
    
    def _parse_results(self, data):
        """Parse SERPAPI results
        
        Args:
            data (dict): Raw API response
            
        Returns:
            dict: Parsed results
        """
        # Add status field
        data['status'] = 'success'
        return data
    
    def _get_feature_opportunities(self, features):
        """Generate opportunities based on SERP features
        
        Args:
            features (dict): SERP features
            
        Returns:
            list: Opportunities for optimization
        """
        opportunities = []
        
        if not features['featured_snippet']:
            opportunities.append({
                'feature': 'Featured Snippet',
                'recommendation': 'Structure content to answer questions directly. Use clear headings, lists, and tables.'
            })
        
        if not features['knowledge_graph']:
            opportunities.append({
                'feature': 'Knowledge Graph',
                'recommendation': 'Implement schema.org markup for your organization, person, or product.'
            })
        
        if not features['faq']:
            opportunities.append({
                'feature': 'FAQ Results',
                'recommendation': 'Add FAQ schema markup to your page with relevant questions and answers.'
            })
        
        if not features['images']:
            opportunities.append({
                'feature': 'Image Results',
                'recommendation': 'Add high-quality, relevant images with proper alt text and file names.'
            })
        
        if not features['videos']:
            opportunities.append({
                'feature': 'Video Results',
                'recommendation': 'Consider adding video content and implementing video schema markup.'
            })
        
        return opportunities
