#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

from config import DEFAULT_USER_AGENT, TIMEOUT

class LinkAnalysis:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
        self.internal_links = []
        self.external_links = []
        self.broken_links = []
    
    def run_audit(self):
        """Run all link analysis checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.soup = BeautifulSoup(response.text, 'html.parser')
            
            self.extract_links()
            self.check_internal_links()
            self.check_external_links()
            self.check_anchor_text()
            self.check_broken_links()
            self.check_link_attributes()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform link analysis: {str(e)}'
            }
            return self.results
    
    def extract_links(self):
        """Extract all links from the page"""
        if not self.soup:
            return
        
        links = self.soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            
            # Skip empty links, anchors, and javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Normalize URL
            if href.startswith('/'):
                href = f"{self.parsed_url.scheme}://{self.domain}{href}"
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(self.url, href)
            
            # Categorize as internal or external
            href_parsed = urlparse(href)
            href_domain = href_parsed.netloc
            
            # Check if the link is internal (same domain or subdomain)
            if href_domain == self.domain or href_domain.endswith('.' + self.domain) or self.domain.endswith('.' + href_domain):
                self.internal_links.append({
                    'url': href,
                    'text': link.get_text().strip(),
                    'rel': link.get('rel', ''),
                    'target': link.get('target', ''),
                    'title': link.get('title', '')
                })
            else:
                self.external_links.append({
                    'url': href,
                    'text': link.get_text().strip(),
                    'rel': link.get('rel', ''),
                    'target': link.get('target', ''),
                    'title': link.get('title', '')
                })
        
        # Store link counts
        self.results['link_counts'] = {
            'value': {
                'total_links': len(links),
                'internal_links': len(self.internal_links),
                'external_links': len(self.external_links)
            },
            'status': 'info',
            'message': f'Found {len(links)} links ({len(self.internal_links)} internal, {len(self.external_links)} external)'
        }
    
    def check_internal_links(self):
        """Analyze internal links"""
        if not self.internal_links:
            self.results['internal_links'] = {
                'value': None,
                'status': 'warning',
                'message': 'No internal links found'
            }
            return
        
        # Check for duplicate internal links
        internal_urls = [link['url'] for link in self.internal_links]
        duplicate_urls = [url for url in set(internal_urls) if internal_urls.count(url) > 1]
        
        # Check for empty anchor text
        empty_anchors = [link for link in self.internal_links if not link['text']]
        
        # Check for overly long anchor text
        long_anchors = [link for link in self.internal_links if len(link['text']) > 100]
        
        issues = []
        if duplicate_urls:
            issues.append(f'Found {len(duplicate_urls)} duplicate internal links')
        
        if empty_anchors:
            issues.append(f'Found {len(empty_anchors)} internal links with empty anchor text')
        
        if long_anchors:
            issues.append(f'Found {len(long_anchors)} internal links with overly long anchor text')
        
        if len(self.internal_links) < 3:
            issues.append('Few internal links found (less than 3)')
        
        self.results['internal_links'] = {
            'value': {
                'count': len(self.internal_links),
                'duplicate_count': len(duplicate_urls),
                'empty_anchor_count': len(empty_anchors),
                'long_anchor_count': len(long_anchors)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Internal linking structure is good' if not issues else '; '.join(issues)
        }
    
    def check_external_links(self):
        """Analyze external links"""
        if not self.external_links:
            self.results['external_links'] = {
                'value': None,
                'status': 'info',
                'message': 'No external links found'
            }
            return
        
        # Check for nofollow attributes
        nofollow_links = []
        for link in self.external_links:
            rel = link.get('rel', [])
            if isinstance(rel, list) and 'nofollow' in rel:
                nofollow_links.append(link)
            elif isinstance(rel, str) and 'nofollow' in rel:
                nofollow_links.append(link)
        
        nofollow_percentage = (len(nofollow_links) / len(self.external_links)) * 100 if self.external_links else 0
        
        # Check for target="_blank"
        new_window_links = [link for link in self.external_links if link.get('target') == '_blank']
        new_window_percentage = (len(new_window_links) / len(self.external_links)) * 100 if self.external_links else 0
        
        issues = []
        if nofollow_percentage < 50:
            issues.append(f'Only {round(nofollow_percentage, 2)}% of external links have nofollow attribute')
        
        if new_window_percentage < 80:
            issues.append(f'Only {round(new_window_percentage, 2)}% of external links open in new window')
        
        self.results['external_links'] = {
            'value': {
                'count': len(self.external_links),
                'nofollow_count': len(nofollow_links),
                'nofollow_percentage': round(nofollow_percentage, 2),
                'new_window_count': len(new_window_links),
                'new_window_percentage': round(new_window_percentage, 2)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'External linking structure is good' if not issues else '; '.join(issues)
        }
    
    def check_anchor_text(self):
        """Analyze anchor text quality"""
        all_links = self.internal_links + self.external_links
        
        if not all_links:
            self.results['anchor_text'] = {
                'value': None,
                'status': 'warning',
                'message': 'No links found to analyze anchor text'
            }
            return
        
        # Check for generic anchor text
        generic_terms = ['click here', 'read more', 'learn more', 'more info', 'details', 'link', 'here']
        generic_anchors = []
        for link in all_links:
            link_text = link['text'].lower()
            if any(term in link_text for term in generic_terms):
                generic_anchors.append(link)
        
        # Check for empty anchor text
        empty_anchors = [link for link in all_links if not link['text']]
        
        # Check for overly long anchor text
        long_anchors = [link for link in all_links if len(link['text']) > 100]
        
        # Check for image links without alt text
        image_links_without_alt = 0
        if self.soup:
            for link in self.soup.find_all('a', href=True):
                img = link.find('img')
                if img and not img.get('alt'):
                    image_links_without_alt += 1
        
        issues = []
        if generic_anchors:
            issues.append(f'Found {len(generic_anchors)} links with generic anchor text')
        
        if empty_anchors:
            issues.append(f'Found {len(empty_anchors)} links with empty anchor text')
        
        if long_anchors:
            issues.append(f'Found {len(long_anchors)} links with overly long anchor text')
        
        if image_links_without_alt:
            issues.append(f'Found {image_links_without_alt} image links without alt text')
        
        self.results['anchor_text'] = {
            'value': {
                'generic_anchor_count': len(generic_anchors),
                'empty_anchor_count': len(empty_anchors),
                'long_anchor_count': len(long_anchors),
                'image_links_without_alt': image_links_without_alt
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Anchor text quality is good' if not issues else '; '.join(issues)
        }
    
    def check_broken_links(self):
        """Check for broken links (limited to a sample to avoid too many requests)"""
        # In a real implementation, this would check all links but with rate limiting
        # For this example, we'll just check a small sample
        
        all_links = self.internal_links + self.external_links
        
        if not all_links:
            self.results['broken_links'] = {
                'value': None,
                'status': 'info',
                'message': 'No links to check for broken links'
            }
            return
        
        # For demonstration, we'll just set a placeholder
        # In a real implementation, you would check each link with a HEAD request
        self.results['broken_links'] = {
            'value': {
                'total_links_checked': len(all_links),
                'broken_links_count': 0,  # Placeholder
                'broken_links': []  # Would contain URLs of broken links
            },
            'status': 'info',
            'message': 'Broken link checking requires active requests to each URL (limited in this implementation)'
        }
    
    def check_link_attributes(self):
        """Check link attributes (rel, target, etc.)"""
        all_links = self.internal_links + self.external_links
        
        if not all_links:
            self.results['link_attributes'] = {
                'value': None,
                'status': 'warning',
                'message': 'No links found to analyze attributes'
            }
            return
        
        # Check for sponsored/ugc attributes on appropriate links
        sponsored_links = [link for link in self.external_links if 'sponsored' in link.get('rel', [])]
        ugc_links = [link for link in self.external_links if 'ugc' in link.get('rel', [])]
        
        # Check for links with title attributes
        links_with_title = [link for link in all_links if link.get('title')]
        
        # Check for download attributes
        download_links = []
        for link in self.soup.find_all('a', href=True):
            if link.get('download'):
                download_links.append(link['href'])
        
        self.results['link_attributes'] = {
            'value': {
                'sponsored_links_count': len(sponsored_links),
                'ugc_links_count': len(ugc_links),
                'links_with_title_count': len(links_with_title),
                'download_links_count': len(download_links)
            },
            'status': 'info',
            'message': f'Found {len(links_with_title)} links with title attributes, {len(sponsored_links)} sponsored links, {len(ugc_links)} UGC links, and {len(download_links)} download links'
        }
