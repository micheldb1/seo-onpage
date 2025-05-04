#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import ssl
import socket
import urllib.robotparser
from urllib.parse import urlparse, quote_plus

from config import (
    DEFAULT_USER_AGENT,
    TIMEOUT,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    MAX_META_DESCRIPTION_LENGTH,
    MIN_META_DESCRIPTION_LENGTH,
    MAX_URL_LENGTH,
    GOOGLE_PAGESPEED_API_KEY,
    LCP_THRESHOLD,
    FID_THRESHOLD,
    CLS_THRESHOLD
)

class TechnicalSEOAudit:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
    
    def run_audit(self):
        """Run all technical SEO audit checks"""
        self.check_status_code()
        self.check_ssl_certificate()
        self.check_robots_txt()
        self.check_sitemap()
        self.check_canonical_tags()
        self.check_meta_robots()
        self.check_url_structure()
        self.check_page_speed()
        self.check_http_headers()
        
        return self.results
    
    def check_status_code(self):
        """Check HTTP status code"""
        try:
            response = requests.head(self.url, headers=self.headers, timeout=TIMEOUT, allow_redirects=True)
            status_code = response.status_code
            self.results['status_code'] = {
                'value': status_code,
                'status': 'good' if status_code == 200 else 'warning' if status_code in [301, 302, 307, 308] else 'error',
                'message': f'Status code: {status_code}'
            }
        except Exception as e:
            self.results['status_code'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check status code: {str(e)}'
            }
    
    def check_ssl_certificate(self):
        """Check SSL certificate"""
        try:
            hostname = self.parsed_url.netloc
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            self.results['ssl_certificate'] = {
                'value': True,
                'status': 'good',
                'message': 'Valid SSL certificate found'
            }
        except Exception as e:
            self.results['ssl_certificate'] = {
                'value': False,
                'status': 'error',
                'message': f'SSL certificate issue: {str(e)}'
            }
    
    def check_robots_txt(self):
        """Check robots.txt file"""
        try:
            robots_url = f"{self.parsed_url.scheme}://{self.domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(DEFAULT_USER_AGENT, self.url)
            self.results['robots_txt'] = {
                'value': can_fetch,
                'status': 'good' if can_fetch else 'warning',
                'message': 'URL is allowed by robots.txt' if can_fetch else 'URL is blocked by robots.txt'
            }
        except Exception as e:
            self.results['robots_txt'] = {
                'value': None,
                'status': 'warning',
                'message': f'Failed to check robots.txt: {str(e)}'
            }
    
    def check_sitemap(self):
        """Check for sitemap.xml"""
        try:
            sitemap_url = f"{self.parsed_url.scheme}://{self.domain}/sitemap.xml"
            response = requests.get(sitemap_url, headers=self.headers, timeout=TIMEOUT)
            
            if response.status_code == 200 and ('xml' in response.headers.get('Content-Type', '')):
                self.results['sitemap'] = {
                    'value': True,
                    'status': 'good',
                    'message': 'Sitemap found'
                }
            else:
                self.results['sitemap'] = {
                    'value': False,
                    'status': 'warning',
                    'message': 'No sitemap found or invalid format'
                }
        except Exception as e:
            self.results['sitemap'] = {
                'value': False,
                'status': 'warning',
                'message': f'Failed to check sitemap: {str(e)}'
            }
    
    def check_canonical_tags(self):
        """Check canonical tags"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            canonical = soup.find('link', {'rel': 'canonical'})
            if canonical and canonical.get('href'):
                canonical_url = canonical.get('href')
                is_self_canonical = canonical_url == self.url or canonical_url == self.url.rstrip('/')
                
                self.results['canonical_tag'] = {
                    'value': canonical_url,
                    'status': 'good' if is_self_canonical else 'warning',
                    'message': 'Self-referencing canonical tag found' if is_self_canonical else f'Canonical tag points to different URL: {canonical_url}'
                }
            else:
                self.results['canonical_tag'] = {
                    'value': None,
                    'status': 'warning',
                    'message': 'No canonical tag found'
                }
        except Exception as e:
            self.results['canonical_tag'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check canonical tags: {str(e)}'
            }
    
    def check_meta_robots(self):
        """Check meta robots tags"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            meta_robots = soup.find('meta', {'name': 'robots'})
            if meta_robots and meta_robots.get('content'):
                content = meta_robots.get('content').lower()
                is_indexable = 'noindex' not in content
                
                self.results['meta_robots'] = {
                    'value': content,
                    'status': 'good' if is_indexable else 'warning',
                    'message': 'Page is indexable' if is_indexable else 'Page is set to noindex'
                }
            else:
                self.results['meta_robots'] = {
                    'value': 'index, follow',  # Default behavior
                    'status': 'good',
                    'message': 'No meta robots tag found (defaults to indexable)'
                }
        except Exception as e:
            self.results['meta_robots'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check meta robots: {str(e)}'
            }
    
    def check_url_structure(self):
        """Check URL structure"""
        url_length = len(self.url)
        has_uppercase = any(c.isupper() for c in self.url)
        has_special_chars = any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&\'()*+,;=' for c in self.url)
        
        issues = []
        if url_length > MAX_URL_LENGTH:
            issues.append(f'URL length ({url_length}) exceeds recommended maximum ({MAX_URL_LENGTH})')
        if has_uppercase:
            issues.append('URL contains uppercase characters')
        if has_special_chars:
            issues.append('URL contains special characters that may need encoding')
        
        self.results['url_structure'] = {
            'value': self.url,
            'status': 'good' if not issues else 'warning',
            'message': 'URL structure is good' if not issues else '; '.join(issues)
        }
    
    def check_page_speed(self):
        """Check page speed using Google PageSpeed Insights API"""
        try:
            if not GOOGLE_PAGESPEED_API_KEY or GOOGLE_PAGESPEED_API_KEY == 'placeholder_pagespeed_api_key':
                self.results['page_speed'] = {
                    'value': None,
                    'status': 'info',
                    'message': 'Page speed check requires valid Google PageSpeed API key'
                }
                return
                
            # Encode URL for API request
            encoded_url = quote_plus(self.url)
            api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&key={GOOGLE_PAGESPEED_API_KEY}&strategy=mobile"
            
            # Use a longer timeout for PageSpeed API (60 seconds instead of default)
            response = requests.get(api_url, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract Core Web Vitals metrics
                lighthouse_result = data.get('lighthouseResult', {})
                audits = lighthouse_result.get('audits', {})
                
                # Performance score
                performance_score = lighthouse_result.get('categories', {}).get('performance', {}).get('score', 0) * 100
                
                # Core Web Vitals
                lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000  # Convert to seconds
                fid = audits.get('max-potential-fid', {}).get('numericValue', 0)  # In milliseconds
                cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
                
                # Determine status based on Core Web Vitals thresholds
                lcp_status = 'good' if lcp < LCP_THRESHOLD else 'warning'
                fid_status = 'good' if fid < FID_THRESHOLD else 'warning'
                cls_status = 'good' if cls < CLS_THRESHOLD else 'warning'
                
                # Overall status
                if performance_score >= 90:
                    overall_status = 'good'
                    message = 'Page speed is excellent'
                elif performance_score >= 50:
                    overall_status = 'warning'
                    message = 'Page speed needs improvement'
                else:
                    overall_status = 'error'
                    message = 'Page speed is poor'
                
                # Add Core Web Vitals details to message
                message += f"; LCP: {lcp:.2f}s ({lcp_status}); FID: {fid:.0f}ms ({fid_status}); CLS: {cls:.2f} ({cls_status})"
                
                self.results['page_speed'] = {
                    'value': {
                        'performance_score': performance_score,
                        'lcp': lcp,
                        'fid': fid,
                        'cls': cls,
                        'lcp_status': lcp_status,
                        'fid_status': fid_status,
                        'cls_status': cls_status
                    },
                    'status': overall_status,
                    'message': message
                }
            else:
                self.results['page_speed'] = {
                    'value': None,
                    'status': 'error',
                    'message': f'Failed to get page speed data: API returned status code {response.status_code}'
                }
        except requests.exceptions.Timeout:
            self.results['page_speed'] = {
                'value': None,
                'status': 'warning',
                'message': 'Page speed check timed out. This often happens with larger websites or slow servers. Try again later or consider optimizing the website.'
            }
        except requests.exceptions.RequestException as e:
            self.results['page_speed'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check page speed: {str(e)}'
            }
    
    def check_mobile_friendliness(self):
        """This method is intentionally left empty as Google has retired the Mobile-Friendly Test API"""
        # This method is intentionally left empty
        pass
    
    def check_http_headers(self):
        """Check HTTP headers"""
        try:
            response = requests.head(self.url, headers=self.headers, timeout=TIMEOUT)
            headers = response.headers
            
            # Check for important headers
            has_x_robots = 'X-Robots-Tag' in headers
            has_content_type = 'Content-Type' in headers
            has_cache_control = 'Cache-Control' in headers
            
            issues = []
            if has_x_robots and 'noindex' in headers.get('X-Robots-Tag', '').lower():
                issues.append('X-Robots-Tag header is set to noindex')
            if not has_content_type:
                issues.append('Content-Type header is missing')
            if not has_cache_control:
                issues.append('Cache-Control header is missing')
            
            self.results['http_headers'] = {
                'value': dict(headers),
                'status': 'good' if not issues else 'warning',
                'message': 'HTTP headers are properly set' if not issues else '; '.join(issues)
            }
        except Exception as e:
            self.results['http_headers'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check HTTP headers: {str(e)}'
            }
