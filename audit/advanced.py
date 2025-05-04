#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json

from config import DEFAULT_USER_AGENT, TIMEOUT

class AdvancedSEOAudit:
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
        """Run all advanced SEO audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            
            self.check_javascript_rendering()
            self.check_serp_features()
            self.check_semantic_analysis()
            self.check_content_freshness()
            self.check_entity_recognition()
            self.check_internationalization()
            self.check_page_segmentation()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform advanced SEO audit: {str(e)}'
            }
            return self.results
    
    def check_javascript_rendering(self):
        """Check for JavaScript-dependent content"""
        if not self.soup or not self.html:
            return
        
        # Look for JavaScript frameworks and libraries
        js_frameworks = {
            'React': r'react\.js|react-dom',
            'Angular': r'angular\.js|ng-app|ng-controller',
            'Vue': r'vue\.js|v-app|v-bind',
            'jQuery': r'jquery\.js|\$\(document\)',
            'Next.js': r'__NEXT_DATA__|next/dist',
            'Gatsby': r'___gatsby',
            'Nuxt.js': r'__NUXT__|nuxt-link'
        }
        
        detected_frameworks = []
        for framework, pattern in js_frameworks.items():
            if re.search(pattern, self.html, re.IGNORECASE):
                detected_frameworks.append(framework)
        
        # Check for JavaScript-rendered content
        js_content_indicators = [
            self.soup.find_all('div', {'id': re.compile(r'app|root|application')}),
            self.soup.find_all('div', {'v-if': True}),
            self.soup.find_all('div', {'ng-if': True}),
            self.soup.find_all('div', {'data-reactroot': True}),
            self.soup.find_all('noscript')
        ]
        
        has_js_content = any(indicators for indicators in js_content_indicators if indicators)
        
        # Check for lazy-loaded content
        lazy_load_indicators = [
            self.soup.find_all(attrs={'data-src': True}),
            self.soup.find_all(attrs={'data-lazy': True}),
            self.soup.find_all(attrs={'loading': 'lazy'}),
            re.search(r'lazyload|lazy-load|lazy_load', self.html, re.IGNORECASE)
        ]
        
        has_lazy_content = any(indicators for indicators in lazy_load_indicators if indicators)
        
        issues = []
        if detected_frameworks:
            issues.append(f'JavaScript frameworks detected: {", ".join(detected_frameworks)}')
        
        if has_js_content:
            issues.append('Page likely contains JavaScript-rendered content')
        
        if has_lazy_content:
            issues.append('Page contains lazy-loaded content')
        
        self.results['javascript_rendering'] = {
            'value': {
                'frameworks': detected_frameworks,
                'has_js_content': has_js_content,
                'has_lazy_content': has_lazy_content
            },
            'status': 'warning' if (detected_frameworks or has_js_content) else 'good',
            'message': 'JavaScript rendering may affect SEO' if issues else 'No JavaScript rendering issues detected'
        }
    
    def check_serp_features(self):
        """Check for SERP feature optimization"""
        if not self.soup:
            return
        
        # Check for featured snippet optimization
        has_definition_lists = bool(self.soup.find_all('dl'))
        has_tables = bool(self.soup.find_all('table'))
        has_lists = bool(self.soup.find_all(['ul', 'ol']))
        has_step_headings = False
        
        # Check for step-by-step headings (how-to content)
        headings = self.soup.find_all(['h2', 'h3', 'h4'])
        step_patterns = [r'^step\s*\d+', r'^\d+\.\s', r'how\s+to']
        for heading in headings:
            heading_text = heading.get_text().lower()
            if any(re.search(pattern, heading_text) for pattern in step_patterns):
                has_step_headings = True
                break
        
        # Check for FAQ schema
        has_faq_schema = False
        scripts = self.soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                if script.string and '@type' in script.string and 'FAQPage' in script.string:
                    has_faq_schema = True
                    break
            except:
                continue
        
        # Check for FAQ-like content without schema
        has_faq_content = bool(self.soup.find_all(['dt', 'dd'])) or bool(re.search(r'<h[2-4][^>]*>[^<]*\?</h[2-4]>', self.html))
        
        # Check for video content (for video features)
        has_video = bool(self.soup.find_all('video')) or bool(self.soup.find_all('iframe', {'src': re.compile(r'youtube|vimeo')}))
        
        features_targeted = []
        if has_definition_lists or has_tables or has_lists:
            features_targeted.append('Featured Snippets')
        
        if has_step_headings:
            features_targeted.append('How-to Results')
        
        if has_faq_schema or has_faq_content:
            features_targeted.append('FAQ Results')
        
        if has_video:
            features_targeted.append('Video Results')
        
        self.results['serp_features'] = {
            'value': {
                'features_targeted': features_targeted,
                'has_faq_schema': has_faq_schema,
                'has_step_content': has_step_headings,
                'has_structured_content': has_definition_lists or has_tables or has_lists
            },
            'status': 'good' if features_targeted else 'info',
            'message': f'Content is optimized for SERP features: {", ".join(features_targeted)}' if features_targeted else 'Content is not specifically optimized for SERP features'
        }
    
    def check_semantic_analysis(self):
        """Perform basic semantic analysis"""
        if not self.soup:
            return
        
        # Extract main content
        main_content = ""
        content_elements = self.soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        for element in content_elements:
            main_content += element.get_text() + " "
        
        main_content = main_content.strip()
        
        if not main_content:
            self.results['semantic_analysis'] = {
                'value': None,
                'status': 'warning',
                'message': 'No content found for semantic analysis'
            }
            return
        
        # Simple topic extraction (in a real implementation, use NLP libraries)
        # Here we'll just count word frequencies as a simple approximation
        words = re.findall(r'\b[a-zA-Z]{3,}\b', main_content.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'is', 'in', 'it', 'to', 'of', 'for', 'with', 'on', 'that', 'this', 'are', 'as', 'be', 'by'}
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequencies
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top topics
        top_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Check for topic consistency
        top_words = [word for word, count in top_topics]
        
        # Check if top words appear in headings
        headings = self.soup.find_all(['h1', 'h2', 'h3'])
        heading_text = ' '.join([h.get_text().lower() for h in headings])
        
        topic_in_headings = sum(1 for word in top_words[:5] if word in heading_text)
        semantic_consistency = (topic_in_headings / 5) * 100 if top_words else 0
        
        self.results['semantic_analysis'] = {
            'value': {
                'top_topics': top_topics,
                'semantic_consistency': round(semantic_consistency, 2)
            },
            'status': 'good' if semantic_consistency >= 60 else 'warning',
            'message': f'Content shows good semantic consistency' if semantic_consistency >= 60 else 'Content may lack semantic focus'
        }
    
    def check_content_freshness(self):
        """Check for content freshness indicators"""
        if not self.soup:
            return
        
        # Look for publication dates
        date_patterns = [
            # Common date meta tags
            self.soup.find('meta', {'property': 'article:published_time'}),
            self.soup.find('meta', {'name': 'date'}),
            self.soup.find('meta', {'name': 'pubdate'}),
            self.soup.find('meta', {'name': 'lastmod'}),
            
            # Common date elements
            self.soup.find(['time', 'span', 'div'], {'class': re.compile(r'date|time|published|updated')}),
            self.soup.find(['time', 'span', 'div'], {'itemprop': re.compile(r'date|time|published|updated')})
        ]
        
        has_date = any(date for date in date_patterns if date)
        
        # Look for "last updated" text
        last_updated_pattern = re.compile(r'last\s+updated|updated\s+on|revised\s+on', re.IGNORECASE)
        has_last_updated = bool(self.soup.find(string=last_updated_pattern))
        
        # Look for recent years in content
        current_year = 2025  # This would normally be dynamically determined
        last_year = current_year - 1
        has_current_year = str(current_year) in self.html
        has_last_year = str(last_year) in self.html
        
        freshness_indicators = []
        if has_date:
            freshness_indicators.append('Publication date found')
        if has_last_updated:
            freshness_indicators.append('Last updated information found')
        if has_current_year:
            freshness_indicators.append(f'Current year ({current_year}) mentioned')
        elif has_last_year:
            freshness_indicators.append(f'Last year ({last_year}) mentioned')
        
        self.results['content_freshness'] = {
            'value': {
                'has_date': has_date,
                'has_last_updated': has_last_updated,
                'has_current_year': has_current_year,
                'has_last_year': has_last_year
            },
            'status': 'good' if freshness_indicators else 'warning',
            'message': f'Content freshness indicators found: {", ".join(freshness_indicators)}' if freshness_indicators else 'No content freshness indicators found'
        }
    
    def check_entity_recognition(self):
        """Check for entity recognition and knowledge graph optimization"""
        if not self.soup:
            return
        
        # Check for entity markup
        has_person_schema = False
        has_org_schema = False
        has_product_schema = False
        has_event_schema = False
        has_place_schema = False
        
        # Check schema.org markup
        scripts = self.soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                if not script.string:
                    continue
                    
                data = json.loads(script.string)
                if not isinstance(data, dict):
                    continue
                    
                entity_type = data.get('@type', '')
                
                if entity_type in ['Person', 'ProfilePage']:
                    has_person_schema = True
                elif entity_type in ['Organization', 'Corporation', 'LocalBusiness']:
                    has_org_schema = True
                elif entity_type in ['Product', 'Offer']:
                    has_product_schema = True
                elif entity_type in ['Event']:
                    has_event_schema = True
                elif entity_type in ['Place', 'LocalBusiness', 'Restaurant', 'Hotel']:
                    has_place_schema = True
            except:
                continue
        
        # Check for microdata
        has_microdata = bool(self.soup.find_all(attrs={'itemtype': re.compile(r'schema.org')}))
        
        # Check for RDFa
        has_rdfa = bool(self.soup.find_all(attrs={'vocab': re.compile(r'schema.org')}))
        
        entities_found = []
        if has_person_schema:
            entities_found.append('Person')
        if has_org_schema:
            entities_found.append('Organization')
        if has_product_schema:
            entities_found.append('Product')
        if has_event_schema:
            entities_found.append('Event')
        if has_place_schema:
            entities_found.append('Place')
        
        markup_types = []
        if scripts:
            markup_types.append('JSON-LD')
        if has_microdata:
            markup_types.append('Microdata')
        if has_rdfa:
            markup_types.append('RDFa')
        
        self.results['entity_recognition'] = {
            'value': {
                'entities_found': entities_found,
                'markup_types': markup_types
            },
            'status': 'good' if entities_found and markup_types else 'info',
            'message': f'Entities found: {", ".join(entities_found)}' if entities_found else 'No entity markup detected'
        }
    
    def check_internationalization(self):
        """Check for internationalization and hreflang"""
        if not self.soup:
            return
        
        # Check for hreflang tags
        hreflang_tags = self.soup.find_all('link', {'rel': 'alternate', 'hreflang': True})
        
        # Check for language meta tag
        lang_meta = self.soup.find('meta', {'http-equiv': 'content-language'}) or self.soup.find('meta', {'name': 'language'})
        
        # Check html lang attribute
        html_tag = self.soup.find('html')
        html_lang = html_tag.get('lang') if html_tag else None
        
        # Extract languages
        languages = []
        if hreflang_tags:
            for tag in hreflang_tags:
                lang = tag.get('hreflang')
                if lang and lang not in languages:
                    languages.append(lang)
        
        if lang_meta and lang_meta.get('content'):
            meta_lang = lang_meta.get('content')
            if meta_lang and meta_lang not in languages:
                languages.append(meta_lang)
        
        if html_lang and html_lang not in languages:
            languages.append(html_lang)
        
        # Check for x-default
        has_x_default = any(tag.get('hreflang') == 'x-default' for tag in hreflang_tags)
        
        issues = []
        if not languages:
            issues.append('No language specification found')
        elif len(languages) > 1 and not has_x_default:
            issues.append('Multiple languages but no x-default hreflang')
        
        if html_lang and lang_meta and lang_meta.get('content') and html_lang != lang_meta.get('content'):
            issues.append('Inconsistent language specification between HTML and meta tag')
        
        self.results['internationalization'] = {
            'value': {
                'languages': languages,
                'has_hreflang': bool(hreflang_tags),
                'has_x_default': has_x_default
            },
            'status': 'good' if languages and not issues else 'warning',
            'message': f'Language specification found: {", ".join(languages)}' if languages and not issues else '; '.join(issues) if issues else 'No language specification found'
        }
    
    def check_page_segmentation(self):
        """Check page segmentation for content focus"""
        if not self.soup:
            return
        
        # Identify main content area
        main_content_candidates = [
            self.soup.find('main'),
            self.soup.find('article'),
            self.soup.find('div', {'id': re.compile(r'content|main|article')}),
            self.soup.find('div', {'class': re.compile(r'content|main|article')})
        ]
        
        main_content = next((c for c in main_content_candidates if c), None)
        
        if not main_content:
            self.results['page_segmentation'] = {
                'value': None,
                'status': 'warning',
                'message': 'Could not identify main content area'
            }
            return
        
        # Count words in main content vs. entire page
        main_text = main_content.get_text()
        main_words = len(re.findall(r'\b\w+\b', main_text))
        
        all_text = self.soup.get_text()
        all_words = len(re.findall(r'\b\w+\b', all_text))
        
        # Calculate content ratio
        content_ratio = (main_words / all_words) * 100 if all_words > 0 else 0
        
        # Check for clear page sections
        has_header = bool(self.soup.find('header'))
        has_footer = bool(self.soup.find('footer'))
        has_nav = bool(self.soup.find('nav'))
        has_sidebar = bool(self.soup.find(['aside', 'div'], {'class': re.compile(r'sidebar')}))
        
        sections_found = []
        if has_header:
            sections_found.append('Header')
        if has_footer:
            sections_found.append('Footer')
        if has_nav:
            sections_found.append('Navigation')
        if has_sidebar:
            sections_found.append('Sidebar')
        if main_content:
            sections_found.append('Main Content')
        
        issues = []
        if content_ratio < 50:
            issues.append(f'Main content only {round(content_ratio, 2)}% of page (should be >50%)')
        
        if len(sections_found) < 3:
            issues.append('Page lacks clear semantic structure')
        
        self.results['page_segmentation'] = {
            'value': {
                'content_ratio': round(content_ratio, 2),
                'sections_found': sections_found
            },
            'status': 'good' if content_ratio >= 50 and len(sections_found) >= 3 else 'warning',
            'message': 'Page has good content focus and structure' if content_ratio >= 50 and len(sections_found) >= 3 else '; '.join(issues)
        }
