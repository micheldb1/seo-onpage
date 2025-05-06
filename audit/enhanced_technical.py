#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import ssl
import socket
from urllib.parse import urlparse
import json
import time
import gzip
import io

from config import DEFAULT_USER_AGENT, TIMEOUT

class EnhancedTechnicalAudit:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
        self.html = ""
    
    def run_audit(self):
        """Run all enhanced technical SEO audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            
            self.check_enhanced_http_headers()
            self.check_lazy_loading()
            self.check_minified_resources()
            self.check_browser_caching()
            self.check_mobile_friendliness()
            self.check_resource_compression()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform enhanced technical audit: {str(e)}'
            }
            return self.results
    
    def check_enhanced_http_headers(self):
        """Enhanced HTTP headers check"""
        try:
            response = requests.head(self.url, headers=self.headers, timeout=TIMEOUT)
            headers = response.headers
            
            # Check for important headers
            security_headers = {
                'Strict-Transport-Security': False,
                'Content-Security-Policy': False,
                'X-Content-Type-Options': False,
                'X-Frame-Options': False,
                'X-XSS-Protection': False
            }
            
            for header in security_headers:
                if header in headers:
                    security_headers[header] = True
            
            # Check caching headers
            cache_headers = {
                'Cache-Control': False,
                'Expires': False,
                'ETag': False,
                'Last-Modified': False
            }
            
            for header in cache_headers:
                if header in headers:
                    cache_headers[header] = True
            
            # Check compression
            has_compression = 'Content-Encoding' in headers and headers['Content-Encoding'] in ['gzip', 'br', 'deflate']
            
            # Calculate scores
            security_score = sum(1 for v in security_headers.values() if v) / len(security_headers)
            cache_score = sum(1 for v in cache_headers.values() if v) / len(cache_headers)
            
            issues = []
            if security_score < 0.6:
                issues.append('Missing important security headers')
            if cache_score < 0.5:
                issues.append('Insufficient caching headers')
            if not has_compression:
                issues.append('No content compression detected')
            
            self.results['enhanced_http_headers'] = {
                'value': {
                    'security_headers': security_headers,
                    'cache_headers': cache_headers,
                    'has_compression': has_compression,
                    'security_score': round(security_score * 100, 2),
                    'cache_score': round(cache_score * 100, 2)
                },
                'status': 'good' if not issues else 'warning',
                'message': 'HTTP headers are properly configured' if not issues else '; '.join(issues)
            }
        except Exception as e:
            self.results['enhanced_http_headers'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check HTTP headers: {str(e)}'
            }
    
    def check_lazy_loading(self):
        """Check for lazy loading implementation on images"""
        try:
            # Check for lazy loading attributes
            lazy_load_images = self.soup.find_all('img', {'loading': 'lazy'})
            data_src_images = self.soup.find_all('img', {'data-src': True})
            
            # Check for lazy loading libraries in scripts
            lazy_load_scripts = re.search(r'lazysizes|lozad|lazyload', self.html, re.IGNORECASE)
            
            has_lazy_loading = bool(lazy_load_images or data_src_images or lazy_load_scripts)
            
            self.results['lazy_loading'] = {
                'value': has_lazy_loading,
                'status': 'good' if has_lazy_loading else 'warning',
                'message': 'Lazy loading implemented for images' if has_lazy_loading else 'No lazy loading detected for images'
            }
        except Exception as e:
            self.results['lazy_loading'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check lazy loading: {str(e)}'
            }
    
    def check_minified_resources(self):
        """Check if CSS and JS files are minified"""
        try:
            # Get all CSS and JS files
            css_files = [link.get('href') for link in self.soup.find_all('link', {'rel': 'stylesheet'})]
            js_files = [script.get('src') for script in self.soup.find_all('script', {'src': True})]
            
            # Filter out None values and external resources
            css_files = [f for f in css_files if f and (f.startswith('/') or f.startswith(self.url))]
            js_files = [f for f in js_files if f and (f.startswith('/') or f.startswith(self.url))]
            
            # Check if files are minified
            minified_css = 0
            minified_js = 0
            
            for css in css_files[:5]:  # Limit to first 5 files to avoid too many requests
                try:
                    file_url = css if css.startswith('http') else f"{self.parsed_url.scheme}://{self.domain}{css if css.startswith('/') else '/' + css}"
                    css_response = requests.get(file_url, headers=self.headers, timeout=TIMEOUT)
                    # Check if minified (no line breaks or few line breaks)
                    if css_response.text.count('\n') < 5 or '.min.css' in css.lower():
                        minified_css += 1
                except:
                    continue
                    
            for js in js_files[:5]:  # Limit to first 5 files
                try:
                    file_url = js if js.startswith('http') else f"{self.parsed_url.scheme}://{self.domain}{js if js.startswith('/') else '/' + js}"
                    js_response = requests.get(file_url, headers=self.headers, timeout=TIMEOUT)
                    # Check if minified (no line breaks or few line breaks)
                    if js_response.text.count('\n') < 5 or '.min.js' in js.lower():
                        minified_js += 1
                except:
                    continue
            
            css_ratio = minified_css / len(css_files) if css_files else 0
            js_ratio = minified_js / len(js_files) if js_files else 0
            
            self.results['minified_resources'] = {
                'value': {
                    'css_ratio': round(css_ratio * 100, 2),
                    'js_ratio': round(js_ratio * 100, 2)
                },
                'status': 'good' if (css_ratio >= 0.7 and js_ratio >= 0.7) else 'warning',
                'message': f'{round(css_ratio * 100)}% CSS and {round(js_ratio * 100)}% JS files are minified'
            }
        except Exception as e:
            self.results['minified_resources'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check minified resources: {str(e)}'
            }
    
    def check_browser_caching(self):
        """Check browser caching configuration"""
        try:
            # Get all static resources
            resources = []
            
            # CSS files
            resources.extend([link.get('href') for link in self.soup.find_all('link', {'rel': 'stylesheet'}) if link.get('href')])
            
            # JS files
            resources.extend([script.get('src') for script in self.soup.find_all('script', {'src': True}) if script.get('src')])
            
            # Images
            resources.extend([img.get('src') for img in self.soup.find_all('img', {'src': True}) if img.get('src')])
            
            # Filter local resources
            local_resources = [r for r in resources if r and not r.startswith('http') and not r.startswith('//')][:5]  # Limit to 5
            
            # Check cache headers for each resource
            cache_times = []
            
            for resource in local_resources:
                try:
                    resource_url = f"{self.parsed_url.scheme}://{self.domain}{resource if resource.startswith('/') else '/' + resource}"
                    response = requests.head(resource_url, headers=self.headers, timeout=TIMEOUT)
                    
                    # Check for cache-control header
                    if 'Cache-Control' in response.headers:
                        cache_control = response.headers['Cache-Control']
                        max_age_match = re.search(r'max-age=([0-9]+)', cache_control)
                        if max_age_match:
                            cache_times.append(int(max_age_match.group(1)))
                    # Check for expires header
                    elif 'Expires' in response.headers:
                        # This is simplified - in a real implementation, parse the date and calculate seconds
                        cache_times.append(86400)  # Assume 1 day if Expires is present but can't parse
                except:
                    continue
            
            # Calculate average cache time
            avg_cache_time = sum(cache_times) / len(cache_times) if cache_times else 0
            
            # Determine status based on cache time
            if avg_cache_time >= 2592000:  # 30 days
                status = 'good'
                message = f'Excellent browser caching (avg: {avg_cache_time/86400:.1f} days)'
            elif avg_cache_time >= 604800:  # 7 days
                status = 'good'
                message = f'Good browser caching (avg: {avg_cache_time/86400:.1f} days)'
            elif avg_cache_time > 0:
                status = 'warning'
                message = f'Browser caching could be improved (avg: {avg_cache_time/86400:.1f} days)'
            else:
                status = 'warning'
                message = 'No browser caching detected'
            
            self.results['browser_caching'] = {
                'value': {
                    'average_cache_time': avg_cache_time,
                    'cache_times': cache_times
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['browser_caching'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check browser caching: {str(e)}'
            }
    
    def check_mobile_friendliness(self):
        """Check mobile-friendliness of the page"""
        try:
            # Check viewport meta tag
            viewport = self.soup.find('meta', {'name': 'viewport'})
            has_viewport = viewport is not None and 'width=device-width' in viewport.get('content', '')
            
            # Check for responsive design indicators
            has_media_queries = False
            has_responsive_images = False
            
            # Check for media queries in style tags
            style_tags = self.soup.find_all('style')
            for style in style_tags:
                if style.string and '@media' in style.string:
                    has_media_queries = True
                    break
            
            # Check for responsive images
            responsive_imgs = self.soup.find_all('img', {'srcset': True}) or self.soup.find_all('img', {'sizes': True})
            has_responsive_images = len(responsive_imgs) > 0
            
            # Check for touch-friendly elements
            buttons = self.soup.find_all('button')
            links = self.soup.find_all('a')
            
            # In a real implementation, we would check button/link sizes
            # Here we'll just check if they have reasonable text content
            small_touch_targets = 0
            for element in buttons + links:
                if element.get_text().strip() and len(element.get_text().strip()) < 3:
                    small_touch_targets += 1
            
            # Calculate mobile-friendliness score
            score = 0
            if has_viewport:
                score += 40
            if has_media_queries:
                score += 30
            if has_responsive_images:
                score += 20
            if small_touch_targets < 5:
                score += 10
            
            # Determine status
            if score >= 70:
                status = 'good'
                message = 'Page appears to be mobile-friendly'
            elif score >= 40:
                status = 'warning'
                message = 'Page has some mobile-friendly elements but needs improvement'
            else:
                status = 'error'
                message = 'Page does not appear to be mobile-friendly'
            
            self.results['mobile_friendliness'] = {
                'value': {
                    'has_viewport': has_viewport,
                    'has_media_queries': has_media_queries,
                    'has_responsive_images': has_responsive_images,
                    'small_touch_targets': small_touch_targets,
                    'score': score
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['mobile_friendliness'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check mobile-friendliness: {str(e)}'
            }
    
    def check_resource_compression(self):
        """Check if resources are properly compressed"""
        try:
            # Get main page compression
            response = requests.get(self.url, headers={
                **self.headers,
                'Accept-Encoding': 'gzip, deflate, br'
            }, timeout=TIMEOUT)
            
            main_page_compressed = 'Content-Encoding' in response.headers
            compression_type = response.headers.get('Content-Encoding', 'none')
            
            # Get a sample of resources
            resources = []
            
            # CSS files
            resources.extend([link.get('href') for link in self.soup.find_all('link', {'rel': 'stylesheet'}) if link.get('href')])
            
            # JS files
            resources.extend([script.get('src') for script in self.soup.find_all('script', {'src': True}) if script.get('src')])
            
            # Filter local resources
            local_resources = [r for r in resources if r and not r.startswith('http') and not r.startswith('//')][:3]  # Limit to 3
            
            # Check compression for each resource
            compressed_resources = 0
            
            for resource in local_resources:
                try:
                    resource_url = f"{self.parsed_url.scheme}://{self.domain}{resource if resource.startswith('/') else '/' + resource}"
                    resource_response = requests.get(resource_url, headers={
                        **self.headers,
                        'Accept-Encoding': 'gzip, deflate, br'
                    }, timeout=TIMEOUT)
                    
                    if 'Content-Encoding' in resource_response.headers:
                        compressed_resources += 1
                except:
                    continue
            
            # Calculate compression ratio
            compression_ratio = compressed_resources / len(local_resources) if local_resources else 0
            
            # Determine status
            if main_page_compressed and compression_ratio >= 0.7:
                status = 'good'
                message = f'Resources are properly compressed ({compression_type})'
            elif main_page_compressed:
                status = 'warning'
                message = f'Main page is compressed, but some resources are not'
            else:
                status = 'warning'
                message = 'No compression detected'
            
            self.results['resource_compression'] = {
                'value': {
                    'main_page_compressed': main_page_compressed,
                    'compression_type': compression_type,
                    'resource_compression_ratio': round(compression_ratio * 100, 2)
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['resource_compression'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check resource compression: {str(e)}'
            }
