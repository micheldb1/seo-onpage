#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urlparse, urljoin
import re
import requests

from config import DEFAULT_USER_AGENT, TIMEOUT

class URLProcessor:
    def __init__(self, url):
        self.url = url
        self.processed_url = None
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
    
    def process(self):
        """Process and normalize the URL"""
        # Add scheme if missing
        if not self.url.startswith(('http://', 'https://')):
            self.url = 'https://' + self.url
        
        # Parse URL
        parsed_url = urlparse(self.url)
        
        # Ensure www is consistent
        netloc = parsed_url.netloc
        if not netloc.startswith('www.') and not re.match(r'^[\d\.]+$', netloc):  # Not an IP address
            # Check if www version exists and redirects properly
            try:
                www_url = f"{parsed_url.scheme}://www.{netloc}{parsed_url.path}"
                response = requests.head(www_url, headers=self.headers, timeout=TIMEOUT, allow_redirects=True)
                if response.status_code == 200:
                    netloc = 'www.' + netloc
            except:
                # If error, keep original netloc
                pass
        
        # Remove trailing slash from path if it's just a root path
        path = parsed_url.path
        if path == '/':
            path = ''
        
        # Remove default ports
        if (':80' in netloc and parsed_url.scheme == 'http') or (':443' in netloc and parsed_url.scheme == 'https'):
            netloc = netloc.split(':')[0]
        
        # Reconstruct URL
        self.processed_url = f"{parsed_url.scheme}://{netloc}{path}"
        
        # Add query parameters if they exist
        if parsed_url.query:
            self.processed_url += f"?{parsed_url.query}"
        
        # Follow redirects to get final URL
        try:
            response = requests.head(self.processed_url, headers=self.headers, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code in [200, 301, 302, 307, 308]:
                self.processed_url = response.url
        except:
            # If error, keep the processed URL
            pass
        
        return self.processed_url
    
    def get_domain(self):
        """Extract domain from processed URL"""
        if not self.processed_url:
            self.process()
        
        parsed_url = urlparse(self.processed_url)
        return parsed_url.netloc
    
    def get_path(self):
        """Extract path from processed URL"""
        if not self.processed_url:
            self.process()
        
        parsed_url = urlparse(self.processed_url)
        return parsed_url.path
    
    def get_base_url(self):
        """Get base URL (scheme + domain)"""
        if not self.processed_url:
            self.process()
        
        parsed_url = urlparse(self.processed_url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    def is_valid(self):
        """Check if URL is valid"""
        try:
            result = urlparse(self.url)
            return all([result.scheme, result.netloc])
        except:
            return False
