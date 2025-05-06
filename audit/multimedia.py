#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO

from config import DEFAULT_USER_AGENT, TIMEOUT

class MultimediaAudit:
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
        """Run all multimedia audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            
            self.check_image_compression()
            self.check_image_dimensions()
            self.check_responsive_images()
            self.check_image_filenames()
            self.check_video_optimization()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform multimedia audit: {str(e)}'
            }
            return self.results
    
    def check_image_compression(self):
        """Check if images are properly compressed"""
        try:
            images = self.soup.find_all('img', {'src': True})
            
            # Filter out data URIs, SVGs, and external images
            valid_images = []
            for img in images:
                src = img.get('src', '')
                if not src.startswith('data:') and not src.startswith('http') and not src.endswith('.svg'):
                    valid_images.append(img)
            
            # Limit to 5 images to avoid too many requests
            valid_images = valid_images[:5]
            
            if not valid_images:
                self.results['image_compression'] = {
                    'value': None,
                    'status': 'info',
                    'message': 'No valid images found to analyze'
                }
                return
            
            # Check image sizes
            large_images = []
            total_size = 0
            
            for img in valid_images:
                try:
                    src = img.get('src')
                    img_url = urljoin(self.url, src)
                    
                    # Get image size in bytes
                    img_response = requests.get(img_url, headers=self.headers, timeout=TIMEOUT)
                    size_kb = len(img_response.content) / 1024
                    total_size += size_kb
                    
                    # Check if image is too large
                    if size_kb > 100:  # 100KB threshold
                        large_images.append({
                            'src': src,
                            'size_kb': round(size_kb, 2)
                        })
                except:
                    continue
            
            avg_size = total_size / len(valid_images) if valid_images else 0
            
            # Determine status
            if avg_size < 50:
                status = 'good'
                message = f'Images are well compressed (avg: {avg_size:.2f}KB)'
            elif avg_size < 100:
                status = 'good'
                message = f'Image compression is acceptable (avg: {avg_size:.2f}KB)'
            else:
                status = 'warning'
                message = f'Images could be better compressed (avg: {avg_size:.2f}KB)'
            
            if large_images:
                message += f"; {len(large_images)} images exceed 100KB"
            
            self.results['image_compression'] = {
                'value': {
                    'average_size_kb': round(avg_size, 2),
                    'large_images': large_images
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['image_compression'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check image compression: {str(e)}'
            }
    
    def check_image_dimensions(self):
        """Check if images have appropriate dimensions"""
        try:
            images = self.soup.find_all('img', {'src': True})
            
            # Filter out data URIs, SVGs, and external images
            valid_images = []
            for img in images:
                src = img.get('src', '')
                if not src.startswith('data:') and not src.startswith('http') and not src.endswith('.svg'):
                    valid_images.append(img)
            
            # Limit to 5 images
            valid_images = valid_images[:5]
            
            if not valid_images:
                self.results['image_dimensions'] = {
                    'value': None,
                    'status': 'info',
                    'message': 'No valid images found to analyze'
                }
                return
            
            # Check image dimensions
            oversized_images = []
            
            for img in valid_images:
                try:
                    src = img.get('src')
                    img_url = urljoin(self.url, src)
                    
                    # Get image dimensions
                    img_response = requests.get(img_url, headers=self.headers, timeout=TIMEOUT)
                    img_data = Image.open(BytesIO(img_response.content))
                    width, height = img_data.size
                    
                    # Get display dimensions from HTML
                    display_width = int(img.get('width', 0)) or None
                    display_height = int(img.get('height', 0)) or None
                    
                    # Check if image is significantly larger than display size
                    if display_width and width > display_width * 2:
                        oversized_images.append({
                            'src': src,
                            'actual_dimensions': f"{width}x{height}",
                            'display_dimensions': f"{display_width}x{display_height}"
                        })
                    elif display_height and height > display_height * 2:
                        oversized_images.append({
                            'src': src,
                            'actual_dimensions': f"{width}x{height}",
                            'display_dimensions': f"{display_width}x{display_height}"
                        })
                except:
                    continue
            
            # Determine status
            if not oversized_images:
                status = 'good'
                message = 'Image dimensions are appropriate for display size'
            else:
                status = 'warning'
                message = f'{len(oversized_images)} images are significantly larger than their display size'
            
            self.results['image_dimensions'] = {
                'value': {
                    'oversized_images': oversized_images
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['image_dimensions'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check image dimensions: {str(e)}'
            }
    
    def check_responsive_images(self):
        """Check for responsive image techniques"""
        try:
            images = self.soup.find_all('img')
            
            # Count responsive image features
            srcset_count = len(self.soup.find_all('img', {'srcset': True}))
            sizes_count = len(self.soup.find_all('img', {'sizes': True}))
            picture_count = len(self.soup.find_all('picture'))
            
            total_responsive = srcset_count + picture_count
            
            # Calculate responsive ratio
            responsive_ratio = total_responsive / len(images) if images else 0
            
            # Determine status
            if responsive_ratio >= 0.7:
                status = 'good'
                message = f'{round(responsive_ratio * 100)}% of images use responsive techniques'
            elif responsive_ratio > 0:
                status = 'warning'
                message = f'Only {round(responsive_ratio * 100)}% of images use responsive techniques'
            else:
                status = 'warning'
                message = 'No responsive image techniques detected'
            
            self.results['responsive_images'] = {
                'value': {
                    'srcset_count': srcset_count,
                    'sizes_count': sizes_count,
                    'picture_count': picture_count,
                    'responsive_ratio': round(responsive_ratio * 100, 2)
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['responsive_images'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check responsive images: {str(e)}'
            }
    
    def check_image_filenames(self):
        """Check if image filenames are SEO-friendly"""
        try:
            images = self.soup.find_all('img', {'src': True})
            
            # Filter out data URIs and SVGs
            valid_images = []
            for img in images:
                src = img.get('src', '')
                if not src.startswith('data:') and not src.endswith('.svg'):
                    valid_images.append(img)
            
            if not valid_images:
                self.results['image_filenames'] = {
                    'value': None,
                    'status': 'info',
                    'message': 'No valid images found to analyze'
                }
                return
            
            # Check filenames
            seo_friendly = 0
            non_seo_friendly = []
            
            for img in valid_images:
                src = img.get('src')
                filename = os.path.basename(urlparse(src).path)
                
                # Check if filename is SEO-friendly
                # SEO-friendly: contains hyphens/underscores, descriptive (>3 chars before extension)
                name_part = os.path.splitext(filename)[0]
                
                if len(name_part) > 3 and ('-' in name_part or '_' in name_part) and not re.match(r'^img|^image|^pic|^[0-9]+$', name_part.lower()):
                    seo_friendly += 1
                else:
                    non_seo_friendly.append({
                        'src': src,
                        'filename': filename
                    })
            
            # Calculate ratio
            seo_friendly_ratio = seo_friendly / len(valid_images) if valid_images else 0
            
            # Determine status
            if seo_friendly_ratio >= 0.7:
                status = 'good'
                message = f'{round(seo_friendly_ratio * 100)}% of image filenames are SEO-friendly'
            else:
                status = 'warning'
                message = f'Only {round(seo_friendly_ratio * 100)}% of image filenames are SEO-friendly'
            
            self.results['image_filenames'] = {
                'value': {
                    'seo_friendly_count': seo_friendly,
                    'non_seo_friendly': non_seo_friendly,
                    'seo_friendly_ratio': round(seo_friendly_ratio * 100, 2)
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['image_filenames'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check image filenames: {str(e)}'
            }
    
    def check_video_optimization(self):
        """Check for video optimization techniques"""
        try:
            # Find videos
            videos = self.soup.find_all('video')
            iframes = self.soup.find_all('iframe', {'src': re.compile(r'youtube|vimeo')})
            
            if not videos and not iframes:
                self.results['video_optimization'] = {
                    'value': None,
                    'status': 'info',
                    'message': 'No videos found on the page'
                }
                return
            
            # Check for video optimization features
            has_preload = any(video.get('preload') for video in videos)
            has_poster = any(video.get('poster') for video in videos)
            has_controls = any(video.get('controls') for video in videos)
            
            # Check for transcripts or captions
            has_transcript = False
            has_captions = any(video.find('track', {'kind': 'captions'}) for video in videos)
            
            # Look for transcript indicators near videos
            for video in videos + iframes:
                next_sibling = video.find_next_sibling()
                if next_sibling and re.search(r'transcript|caption|subtitle', str(next_sibling), re.IGNORECASE):
                    has_transcript = True
                    break
            
            # Check for lazy loading
            has_lazy_loading = any(video.get('loading') == 'lazy' for video in videos)
            has_lazy_iframe = any(iframe.get('loading') == 'lazy' for iframe in iframes)
            
            # Calculate optimization score
            score = 0
            if has_preload:
                score += 20
            if has_poster:
                score += 20
            if has_controls:
                score += 10
            if has_transcript or has_captions:
                score += 30
            if has_lazy_loading or has_lazy_iframe:
                score += 20
            
            # Determine status
            if score >= 70:
                status = 'good'
                message = 'Videos are well-optimized'
            elif score >= 40:
                status = 'warning'
                message = 'Videos could be better optimized'
            else:
                status = 'warning'
                message = 'Videos lack optimization'
            
            self.results['video_optimization'] = {
                'value': {
                    'video_count': len(videos),
                    'embedded_video_count': len(iframes),
                    'has_preload': has_preload,
                    'has_poster': has_poster,
                    'has_controls': has_controls,
                    'has_transcript': has_transcript,
                    'has_captions': has_captions,
                    'has_lazy_loading': has_lazy_loading or has_lazy_iframe,
                    'optimization_score': score
                },
                'status': status,
                'message': message
            }
        except Exception as e:
            self.results['video_optimization'] = {
                'value': None,
                'status': 'error',
                'message': f'Failed to check video optimization: {str(e)}'
            }
