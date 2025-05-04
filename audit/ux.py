#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

from config import DEFAULT_USER_AGENT, TIMEOUT

class UXFactorsAudit:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
    
    def run_audit(self):
        """Run all UX factors audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.soup = BeautifulSoup(response.text, 'html.parser')
            
            self.check_image_optimization()
            self.check_mobile_viewport()
            self.check_font_size()
            self.check_tap_targets()
            self.check_form_usability()
            self.check_content_readability()
            self.check_cta_effectiveness()
            self.check_navigation_usability()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform UX audit: {str(e)}'
            }
            return self.results
    
    def check_image_optimization(self):
        """Check image optimization"""
        if not self.soup:
            return
        
        images = self.soup.find_all('img')
        
        if not images:
            self.results['image_optimization'] = {
                'value': None,
                'status': 'info',
                'message': 'No images found on the page'
            }
            return
        
        # Check for width and height attributes
        images_with_dimensions = [img for img in images if img.get('width') and img.get('height')]
        
        # Check for lazy loading
        images_with_lazy_loading = [img for img in images if img.get('loading') == 'lazy' or img.get('data-src')]
        
        # Check for responsive images
        images_with_srcset = [img for img in images if img.get('srcset')]
        
        # Calculate percentages
        dimensions_percentage = (len(images_with_dimensions) / len(images)) * 100
        lazy_loading_percentage = (len(images_with_lazy_loading) / len(images)) * 100
        responsive_percentage = (len(images_with_srcset) / len(images)) * 100
        
        issues = []
        if dimensions_percentage < 80:
            issues.append(f'Only {round(dimensions_percentage, 2)}% of images have width and height attributes')
        
        if lazy_loading_percentage < 50:
            issues.append(f'Only {round(lazy_loading_percentage, 2)}% of images use lazy loading')
        
        if responsive_percentage < 50:
            issues.append(f'Only {round(responsive_percentage, 2)}% of images use responsive techniques (srcset)')
        
        self.results['image_optimization'] = {
            'value': {
                'total_images': len(images),
                'images_with_dimensions': len(images_with_dimensions),
                'images_with_lazy_loading': len(images_with_lazy_loading),
                'images_with_srcset': len(images_with_srcset),
                'dimensions_percentage': round(dimensions_percentage, 2),
                'lazy_loading_percentage': round(lazy_loading_percentage, 2),
                'responsive_percentage': round(responsive_percentage, 2)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Images are well optimized for UX' if not issues else '; '.join(issues)
        }
    
    def check_mobile_viewport(self):
        """Check mobile viewport meta tag"""
        if not self.soup:
            return
        
        viewport_meta = self.soup.find('meta', {'name': 'viewport'})
        
        if not viewport_meta or not viewport_meta.get('content'):
            self.results['mobile_viewport'] = {
                'value': None,
                'status': 'error',
                'message': 'No viewport meta tag found'
            }
            return
        
        viewport_content = viewport_meta.get('content')
        
        # Check for key viewport properties
        has_width = 'width=' in viewport_content
        has_initial_scale = 'initial-scale=' in viewport_content
        has_device_width = 'width=device-width' in viewport_content
        
        issues = []
        if not has_width:
            issues.append('Viewport meta tag missing width property')
        
        if not has_initial_scale:
            issues.append('Viewport meta tag missing initial-scale property')
        
        if not has_device_width:
            issues.append('Viewport width is not set to device-width')
        
        self.results['mobile_viewport'] = {
            'value': viewport_content,
            'status': 'good' if not issues else 'warning',
            'message': 'Viewport meta tag is properly configured' if not issues else '; '.join(issues)
        }
    
    def check_font_size(self):
        """Check font size for readability"""
        if not self.soup:
            return
        
        # Extract CSS styles
        styles = self.soup.find_all('style')
        inline_styles = [tag.get('style') for tag in self.soup.find_all(style=True)]
        
        # Look for small font sizes in styles
        small_font_patterns = [r'font-size:\s*([0-9]+)px', r'font-size:\s*([0-9\.]+)em', r'font-size:\s*([0-9\.]+)rem']
        
        small_fonts_found = False
        for pattern in small_font_patterns:
            # Check in style tags
            for style in styles:
                if style.string:
                    matches = re.findall(pattern, style.string)
                    for match in matches:
                        if (pattern.endswith('px') and float(match) < 16) or \
                           (pattern.endswith('em') and float(match) < 1) or \
                           (pattern.endswith('rem') and float(match) < 1):
                            small_fonts_found = True
                            break
            
            # Check in inline styles
            for style in inline_styles:
                if style:
                    matches = re.findall(pattern, style)
                    for match in matches:
                        if (pattern.endswith('px') and float(match) < 16) or \
                           (pattern.endswith('em') and float(match) < 1) or \
                           (pattern.endswith('rem') and float(match) < 1):
                            small_fonts_found = True
                            break
        
        self.results['font_size'] = {
            'value': small_fonts_found,
            'status': 'warning' if small_fonts_found else 'good',
            'message': 'Small font sizes detected (less than 16px or 1em/rem)' if small_fonts_found else 'Font sizes appear to be readable'
        }
    
    def check_tap_targets(self):
        """Check tap target sizes for mobile usability"""
        if not self.soup:
            return
        
        # This is a simplified check - a real implementation would analyze CSS
        # to determine actual tap target sizes
        
        # Look for closely spaced links
        links = self.soup.find_all('a', href=True)
        buttons = self.soup.find_all('button')
        inputs = self.soup.find_all('input', {'type': ['button', 'submit', 'reset']})
        
        # Check for small buttons or links with minimal content
        small_tap_targets = []
        
        for link in links:
            # Check if link contains only a very short text or a small image
            text = link.get_text().strip()
            img = link.find('img')
            
            if (len(text) <= 1 and not img) or \
               (img and (not img.get('width') or int(img.get('width', '0')) < 48) and \
                        (not img.get('height') or int(img.get('height', '0')) < 48)):
                small_tap_targets.append(link)
        
        for button in buttons:
            if len(button.get_text().strip()) <= 1 and not button.find('img'):
                small_tap_targets.append(button)
        
        self.results['tap_targets'] = {
            'value': len(small_tap_targets),
            'status': 'warning' if small_tap_targets else 'good',
            'message': f'Found {len(small_tap_targets)} potentially small tap targets' if small_tap_targets else 'Tap targets appear to be properly sized'
        }
    
    def check_form_usability(self):
        """Check form usability"""
        if not self.soup:
            return
        
        forms = self.soup.find_all('form')
        
        if not forms:
            self.results['form_usability'] = {
                'value': None,
                'status': 'info',
                'message': 'No forms found on the page'
            }
            return
        
        form_issues = []
        
        for form in forms:
            # Check for labels on inputs
            inputs = form.find_all('input', {'type': ['text', 'email', 'password', 'tel', 'number']})
            inputs_with_labels = 0
            
            for input_field in inputs:
                input_id = input_field.get('id')
                if input_id and form.find('label', {'for': input_id}):
                    inputs_with_labels += 1
                elif input_field.parent.name == 'label':
                    inputs_with_labels += 1
                elif input_field.get('placeholder'):
                    # Placeholder is not as good as a label but better than nothing
                    inputs_with_labels += 0.5
            
            if inputs and inputs_with_labels / len(inputs) < 0.8:
                form_issues.append(f'Form has {len(inputs) - inputs_with_labels} inputs without proper labels')
            
            # Check for submit button
            has_submit = form.find('input', {'type': 'submit'}) or form.find('button', {'type': 'submit'}) or form.find('button')
            if not has_submit:
                form_issues.append('Form missing submit button')
        
        self.results['form_usability'] = {
            'value': {
                'forms_count': len(forms),
                'forms_with_issues': len(form_issues)
            },
            'status': 'good' if not form_issues else 'warning',
            'message': 'Forms are user-friendly' if not form_issues else '; '.join(form_issues)
        }
    
    def check_content_readability(self):
        """Check content layout and readability"""
        if not self.soup:
            return
        
        # Check for text contrast (simplified - would need CSS analysis)
        has_contrast_issues = False
        
        # Check for line length (container width)
        main_content = self.soup.find('main') or self.soup.find('article') or self.soup.find('div', {'class': re.compile(r'content|main|article')})
        
        if main_content and main_content.get('style') and 'width' in main_content.get('style'):
            width_match = re.search(r'width:\s*([0-9]+)px', main_content.get('style'))
            if width_match and int(width_match.group(1)) > 900:
                has_contrast_issues = True
        
        # Check for paragraph length
        paragraphs = self.soup.find_all('p')
        long_paragraphs = [p for p in paragraphs if len(p.get_text()) > 500]  # Roughly 100 words
        
        issues = []
        if has_contrast_issues:
            issues.append('Content container may be too wide for comfortable reading')
        
        if long_paragraphs and len(long_paragraphs) / len(paragraphs) > 0.3:
            issues.append(f'Found {len(long_paragraphs)} excessively long paragraphs')
        
        self.results['content_readability'] = {
            'value': {
                'total_paragraphs': len(paragraphs),
                'long_paragraphs': len(long_paragraphs)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Content layout appears readable' if not issues else '; '.join(issues)
        }
    
    def check_cta_effectiveness(self):
        """Check call-to-action effectiveness"""
        if not self.soup:
            return
        
        # Look for buttons and prominent links that might be CTAs
        buttons = self.soup.find_all('button')
        cta_links = self.soup.find_all('a', {'class': re.compile(r'btn|button|cta')})
        
        # Also look for links with typical CTA text
        cta_texts = ['sign up', 'register', 'subscribe', 'download', 'get started', 'try', 'buy', 'order', 'shop']
        text_ctas = []
        
        for link in self.soup.find_all('a', href=True):
            link_text = link.get_text().lower().strip()
            if any(cta in link_text for cta in cta_texts):
                text_ctas.append(link)
        
        total_ctas = len(buttons) + len(cta_links) + len(text_ctas)
        
        # Check for above-the-fold CTAs (simplified)
        above_fold_ctas = 0
        for cta in buttons + cta_links + text_ctas:
            # Simplified check - in reality would need to calculate actual position
            if cta.parent and cta.parent.parent and cta.parent.parent.parent:
                if cta.parent.name in ['header', 'nav'] or \
                   cta.parent.parent.name in ['header', 'nav'] or \
                   cta.parent.parent.parent.name in ['header', 'nav']:
                    above_fold_ctas += 1
        
        issues = []
        if total_ctas == 0:
            issues.append('No clear call-to-action elements found')
        elif above_fold_ctas == 0:
            issues.append('No above-the-fold call-to-action elements found')
        
        self.results['cta_effectiveness'] = {
            'value': {
                'total_ctas': total_ctas,
                'above_fold_ctas': above_fold_ctas
            },
            'status': 'good' if total_ctas > 0 and above_fold_ctas > 0 else 'warning',
            'message': 'Effective call-to-action elements found' if total_ctas > 0 and above_fold_ctas > 0 else '; '.join(issues)
        }
    
    def check_navigation_usability(self):
        """Check navigation usability"""
        if not self.soup:
            return
        
        # Look for navigation elements
        nav_elements = self.soup.find_all('nav')
        header_nav = self.soup.find('header') and self.soup.find('header').find_all('ul')
        menu_classes = self.soup.find_all(['ul', 'div'], {'class': re.compile(r'menu|nav|navigation')})
        
        has_navigation = len(nav_elements) > 0 or len(header_nav or []) > 0 or len(menu_classes) > 0
        
        # Check for mobile menu (hamburger)
        has_mobile_menu = False
        hamburger_patterns = [
            # Look for common hamburger menu implementations
            self.soup.find_all(['button', 'div', 'a'], {'class': re.compile(r'hamburger|menu-toggle|navbar-toggle|menu-button')}),
            self.soup.find_all(['i', 'span'], {'class': re.compile(r'fa-bars|hamburger|menu-icon')}),
            self.soup.find_all(string=re.compile(r'☰'))
        ]
        
        for pattern in hamburger_patterns:
            if pattern:
                has_mobile_menu = True
                break
        
        # Check for breadcrumbs
        has_breadcrumbs = bool(self.soup.find_all(['nav', 'div', 'ul'], {'class': re.compile(r'breadcrumb')}))
        
        issues = []
        if not has_navigation:
            issues.append('No clear navigation elements found')
        
        if not has_mobile_menu:
            issues.append('No mobile menu/hamburger menu detected')
        
        self.results['navigation_usability'] = {
            'value': {
                'has_navigation': has_navigation,
                'has_mobile_menu': has_mobile_menu,
                'has_breadcrumbs': has_breadcrumbs
            },
            'status': 'good' if has_navigation and has_mobile_menu else 'warning',
            'message': 'Navigation elements are user-friendly' if has_navigation and has_mobile_menu else '; '.join(issues)
        }
