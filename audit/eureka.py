#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json
import math
from urllib.parse import urlparse
from datetime import datetime

from config import DEFAULT_USER_AGENT, TIMEOUT

class EurekaAnalysis:
    def __init__(self, url, keywords=None):
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
        self.keywords = keywords or []
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
        self.html = ""
        
    def run_analysis(self):
        """Run all Eureka analysis methods"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            
            self.calculate_eureka_score()
            self.perform_gap_analysis()
            self.generate_auto_recommendations()
            self.create_semantic_differential_map()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform Eureka analysis: {str(e)}'
            }
            return self.results
    
    def calculate_eureka_score(self):
        """Calculate Eureka Score - a composite score for SERP dominance potential"""
        if not self.soup:
            return
            
        # Component scores (each from 0-100)
        technical_score = self._calculate_technical_component()
        content_score = self._calculate_content_component()
        semantic_score = self._calculate_semantic_component()
        ux_score = self._calculate_ux_component()
        
        # Weighted calculation
        eureka_score = (
            technical_score * 0.25 +
            content_score * 0.35 +
            semantic_score * 0.25 +
            ux_score * 0.15
        )
        
        # Determine potential
        if eureka_score >= 80:
            potential = "Excellent"
            message = "Page has high potential for SERP dominance"
        elif eureka_score >= 60:
            potential = "Good"
            message = "Page has good potential with some improvements needed"
        elif eureka_score >= 40:
            potential = "Moderate"
            message = "Page needs significant improvements for better SERP performance"
        else:
            potential = "Poor"
            message = "Page requires major overhaul for SERP competitiveness"
        
        self.results['eureka_score'] = {
            'value': {
                'total_score': round(eureka_score, 2),
                'technical_score': round(technical_score, 2),
                'content_score': round(content_score, 2),
                'semantic_score': round(semantic_score, 2),
                'ux_score': round(ux_score, 2),
                'potential': potential
            },
            'status': 'good' if eureka_score >= 60 else 'warning',
            'message': message
        }
    
    def _calculate_technical_component(self):
        """Calculate technical component of Eureka Score"""
        score = 0
        
        # SSL check
        if self.url.startswith('https'):
            score += 10
        
        # Mobile-friendly check (basic)
        viewport_meta = self.soup.find('meta', {'name': 'viewport'})
        if viewport_meta and 'width=device-width' in viewport_meta.get('content', ''):
            score += 10
        
        # Page speed indicators (simplified)
        if len(self.html) < 100000:  # Rough estimate for page size
            score += 15
        elif len(self.html) < 200000:
            score += 10
        else:
            score += 5
        
        # Schema markup
        if self.soup.find_all('script', {'type': 'application/ld+json'}):
            score += 15
        
        # Canonical tag
        if self.soup.find('link', {'rel': 'canonical'}):
            score += 10
        
        # Headers (simplified check)
        h1_tags = self.soup.find_all('h1')
        if len(h1_tags) == 1:
            score += 10
        
        # URL structure
        if len(self.url) < 100 and not re.search(r'\d{5,}', self.url):
            score += 10
        
        # Normalize to 0-100
        return min(score * 1.25, 100)
    
    def _calculate_content_component(self):
        """Calculate content component of Eureka Score"""
        score = 0
        
        # Content length
        main_content = ""
        for p in self.soup.find_all('p'):
            main_content += p.get_text() + " "
        
        word_count = len(re.findall(r'\b\w+\b', main_content))
        
        if word_count > 1500:
            score += 25
        elif word_count > 1000:
            score += 20
        elif word_count > 750:
            score += 15
        elif word_count > 500:
            score += 10
        elif word_count > 300:
            score += 5
        
        # Keyword usage (if keywords provided)
        if self.keywords:
            keyword_score = 0
            for keyword in self.keywords:
                if keyword.lower() in main_content.lower():
                    keyword_density = main_content.lower().count(keyword.lower()) / word_count if word_count > 0 else 0
                    if 0.005 <= keyword_density <= 0.025:  # Optimal density between 0.5% and 2.5%
                        keyword_score += 5
            score += min(keyword_score, 20)
        else:
            score += 10  # Default if no keywords provided
        
        # Heading structure
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) >= 3:
            score += 15
        elif len(headings) >= 1:
            score += 10
        
        # Media elements
        images = self.soup.find_all('img')
        videos = self.soup.find_all(['video', 'iframe'])
        
        if len(images) >= 3:
            score += 15
        elif len(images) >= 1:
            score += 10
        
        if videos:
            score += 15
        
        # Normalize to 0-100
        return min(score, 100)
    
    def _calculate_semantic_component(self):
        """Calculate semantic component of Eureka Score"""
        score = 0
        
        # Entity markup
        schema_scripts = self.soup.find_all('script', {'type': 'application/ld+json'})
        entity_types = set()
        
        for script in schema_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if '@type' in data:
                        entity_types.add(data['@type'])
            except:
                continue
        
        if len(entity_types) >= 2:
            score += 25
        elif len(entity_types) == 1:
            score += 15
        
        # Topic relevance (simplified)
        headings_text = " ".join([h.get_text() for h in self.soup.find_all(['h1', 'h2', 'h3'])])
        paragraphs_text = " ".join([p.get_text() for p in self.soup.find_all('p')])
        
        # Check for semantic consistency between headings and paragraphs
        if headings_text and paragraphs_text:
            heading_words = set(re.findall(r'\b[a-z]{4,}\b', headings_text.lower()))
            paragraph_words = set(re.findall(r'\b[a-z]{4,}\b', paragraphs_text.lower()))
            
            common_words = heading_words.intersection(paragraph_words)
            if len(common_words) >= 5:
                score += 25
            elif len(common_words) >= 3:
                score += 15
            elif len(common_words) >= 1:
                score += 5
        
        # FAQ-like content
        if re.search(r'<h[2-4][^>]*>[^<]*\?</h[2-4]>', self.html):
            score += 15
        
        # Lists and structured content
        if self.soup.find_all(['ul', 'ol']):
            score += 15
        
        # Tables for data
        if self.soup.find_all('table'):
            score += 10
        
        # Normalize to 0-100
        return min(score * 1.1, 100)
    
    def _calculate_ux_component(self):
        """Calculate UX component of Eureka Score"""
        score = 0
        
        # Mobile viewport
        viewport_meta = self.soup.find('meta', {'name': 'viewport'})
        if viewport_meta and 'width=device-width' in viewport_meta.get('content', ''):
            score += 20
        
        # Navigation elements
        if self.soup.find('nav') or self.soup.find(['ul', 'ol'], {'class': re.compile(r'nav|menu')}):
            score += 15
        
        # Breadcrumbs
        if self.soup.find(class_=re.compile(r'breadcrumb')):
            score += 10
        
        # Font size (basic check)
        style_tags = self.soup.find_all('style')
        inline_styles = []
        for style in style_tags:
            inline_styles.append(style.string if style.string else "")
        
        css_text = " ".join(inline_styles)
        if re.search(r'font-size:\s*1[2-8]px', css_text) or not re.search(r'font-size:\s*[0-9]px', css_text):
            score += 15
        
        # Interactive elements
        forms = self.soup.find_all('form')
        buttons = self.soup.find_all('button')
        
        if forms or len(buttons) > 2:
            score += 15
        
        # Footer information
        if self.soup.find('footer'):
            score += 10
        
        # Contact information
        if re.search(r'contact|email|phone|tel:', self.html, re.IGNORECASE):
            score += 15
        
        # Normalize to 0-100
        return min(score, 100)
    
    def perform_gap_analysis(self):
        """Perform gap analysis to identify improvement opportunities"""
        if not self.soup:
            return
            
        gaps = []
        
        # Technical gaps
        if not self.soup.find('link', {'rel': 'canonical'}):
            gaps.append({
                'category': 'technical',
                'issue': 'Missing canonical tag',
                'impact': 'high',
                'recommendation': 'Add a canonical tag to prevent duplicate content issues'
            })
        
        if not self.soup.find('meta', {'name': 'viewport'}):
            gaps.append({
                'category': 'technical',
                'issue': 'Missing viewport meta tag',
                'impact': 'high',
                'recommendation': 'Add viewport meta tag for mobile responsiveness'
            })
        
        # Content gaps
        h1_tags = self.soup.find_all('h1')
        if not h1_tags:
            gaps.append({
                'category': 'content',
                'issue': 'Missing H1 tag',
                'impact': 'high',
                'recommendation': 'Add a descriptive H1 tag containing your primary keyword'
            })
        elif len(h1_tags) > 1:
            gaps.append({
                'category': 'content',
                'issue': 'Multiple H1 tags',
                'impact': 'medium',
                'recommendation': 'Use only one H1 tag per page'
            })
        
        # Calculate content length
        paragraphs = self.soup.find_all('p')
        content_text = " ".join([p.get_text() for p in paragraphs])
        word_count = len(re.findall(r'\b\w+\b', content_text))
        
        if word_count < 300:
            gaps.append({
                'category': 'content',
                'issue': 'Thin content',
                'impact': 'high',
                'recommendation': 'Expand content to at least 500 words for better topic coverage'
            })
        
        # Image optimization
        images = self.soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        
        if images_without_alt:
            gaps.append({
                'category': 'content',
                'issue': f'{len(images_without_alt)} images missing alt text',
                'impact': 'medium',
                'recommendation': 'Add descriptive alt text to all images'
            })
        
        # Schema gaps
        schema_scripts = self.soup.find_all('script', {'type': 'application/ld+json'})
        if not schema_scripts:
            gaps.append({
                'category': 'semantic',
                'issue': 'No structured data found',
                'impact': 'medium',
                'recommendation': 'Add relevant schema.org markup for better SERP features'
            })
        
        # UX gaps
        if not self.soup.find_all(['ul', 'ol']):
            gaps.append({
                'category': 'ux',
                'issue': 'No list elements found',
                'impact': 'low',
                'recommendation': 'Add lists to break up content and improve readability'
            })
        
        # Sort gaps by impact
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_gaps = sorted(gaps, key=lambda x: impact_order[x['impact']])
        
        self.results['gap_analysis'] = {
            'value': sorted_gaps,
            'status': 'warning' if sorted_gaps else 'good',
            'message': f'Found {len(sorted_gaps)} optimization opportunities' if sorted_gaps else 'No significant gaps found'
        }
    
    def generate_auto_recommendations(self):
        """Generate automatic recommendations based on analysis"""
        if not self.soup or not self.results.get('gap_analysis'):
            return
            
        gaps = self.results['gap_analysis']['value']
        
        recommendations = []
        code_snippets = {}
        
        for gap in gaps:
            if gap['category'] == 'technical' and gap['issue'] == 'Missing canonical tag':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Add canonical tag',
                    'details': 'Add the following code in the <head> section:',
                    'has_code': True,
                    'code_key': 'canonical_tag'
                })
                code_snippets['canonical_tag'] = f'<link rel="canonical" href="{self.url}" />'
            
            elif gap['category'] == 'technical' and gap['issue'] == 'Missing viewport meta tag':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Add viewport meta tag',
                    'details': 'Add the following code in the <head> section:',
                    'has_code': True,
                    'code_key': 'viewport_tag'
                })
                code_snippets['viewport_tag'] = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
            
            elif gap['category'] == 'content' and gap['issue'] == 'Missing H1 tag':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Add H1 heading',
                    'details': 'Add a descriptive H1 tag at the top of your main content:',
                    'has_code': True,
                    'code_key': 'h1_tag'
                })
                
                # Try to generate a title from page content or URL
                title_tag = self.soup.find('title')
                if title_tag and title_tag.string:
                    suggested_h1 = title_tag.string
                else:
                    # Extract from URL
                    path = self.parsed_url.path
                    if path:
                        suggested_h1 = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                        if not suggested_h1 or suggested_h1 == '/':
                            suggested_h1 = self.domain.split('.')[0].title()
                    else:
                        suggested_h1 = self.domain.split('.')[0].title()
                
                code_snippets['h1_tag'] = f'<h1>{suggested_h1}</h1>'
            
            elif gap['category'] == 'content' and gap['issue'] == 'Thin content':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Expand content',
                    'details': 'Add more comprehensive content covering the topic in depth. Consider including:',
                    'has_code': False,
                    'bullet_points': [
                        'More detailed explanations',
                        'Examples or case studies',
                        'Statistics or data points',
                        'Expert opinions or quotes',
                        'Related subtopics'
                    ]
                })
            
            elif gap['category'] == 'semantic' and gap['issue'] == 'No structured data found':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Add structured data',
                    'details': 'Add appropriate schema.org markup based on your content type:',
                    'has_code': True,
                    'code_key': 'schema_markup'
                })
                
                # Determine the most appropriate schema type
                if re.search(r'article|blog|news', self.html, re.IGNORECASE):
                    schema_type = 'Article'
                elif re.search(r'product|price|\$|€|buy|purchase', self.html, re.IGNORECASE):
                    schema_type = 'Product'
                elif re.search(r'recipe|ingredient|cook', self.html, re.IGNORECASE):
                    schema_type = 'Recipe'
                elif re.search(r'faq|question|answer', self.html, re.IGNORECASE):
                    schema_type = 'FAQPage'
                else:
                    schema_type = 'WebPage'
                
                # Create basic schema template
                if schema_type == 'Article':
                    title_tag = self.soup.find('title')
                    title = title_tag.string if title_tag and title_tag.string else 'Article Title'
                    
                    code_snippets['schema_markup'] = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "author": {{
    "@type": "Person",
    "name": "Author Name"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Publisher Name",
    "logo": {{
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }}
  }},
  "datePublished": "{datetime.now().strftime('%Y-%m-%d')}",
  "dateModified": "{datetime.now().strftime('%Y-%m-%d')}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{self.url}"
  }}
}}
</script>"""
                else:
                    code_snippets['schema_markup'] = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "{schema_type}",
  "name": "Page Title",
  "url": "{self.url}"
  // Add more properties specific to your content
}}
</script>"""
        
        self.results['auto_recommendations'] = {
            'value': {
                'recommendations': recommendations,
                'code_snippets': code_snippets
            },
            'status': 'info' if recommendations else 'good',
            'message': f'Generated {len(recommendations)} actionable recommendations' if recommendations else 'No recommendations needed'
        }
    
    def create_semantic_differential_map(self):
        """Create a semantic differential map comparing to typical competitors"""
        if not self.soup:
            return
            
        # This would normally involve competitor analysis
        # For this implementation, we'll create a simplified version based on industry benchmarks
        
        # Extract key metrics from the page
        word_count = len(re.findall(r'\b\w+\b', self.soup.get_text()))
        heading_count = len(self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        image_count = len(self.soup.find_all('img'))
        list_count = len(self.soup.find_all(['ul', 'ol']))
        link_count = len(self.soup.find_all('a'))
        schema_count = len(self.soup.find_all('script', {'type': 'application/ld+json'}))
        
        # Define industry benchmarks (simplified)
        benchmarks = {
            'word_count': 1000,  # Average word count for ranking pages
            'heading_count': 8,  # Average number of headings
            'image_count': 5,    # Average number of images
            'list_count': 3,     # Average number of lists
            'link_count': 15,    # Average number of links
            'schema_count': 2    # Average number of schema types
        }
        
        # Calculate differentials (as percentages of benchmark)
        differentials = {
            'content_volume': (word_count / benchmarks['word_count']) * 100,
            'content_structure': (heading_count / benchmarks['heading_count']) * 100,
            'visual_elements': (image_count / benchmarks['image_count']) * 100,
            'content_formatting': (list_count / benchmarks['list_count']) * 100,
            'internal_linking': (link_count / benchmarks['link_count']) * 100,
            'structured_data': (schema_count / benchmarks['schema_count']) * 100
        }
        
        # Identify strengths and weaknesses
        strengths = [k for k, v in differentials.items() if v >= 120]  # 20% above benchmark
        weaknesses = [k for k, v in differentials.items() if v <= 80]  # 20% below benchmark
        
        # Format for display
        formatted_differentials = {k: round(v, 1) for k, v in differentials.items()}
        
        self.results['semantic_differential'] = {
            'value': {
                'metrics': {
                    'word_count': word_count,
                    'heading_count': heading_count,
                    'image_count': image_count,
                    'list_count': list_count,
                    'link_count': link_count,
                    'schema_count': schema_count
                },
                'benchmarks': benchmarks,
                'differentials': formatted_differentials,
                'strengths': strengths,
                'weaknesses': weaknesses
            },
            'status': 'good' if len(strengths) > len(weaknesses) else 'warning',
            'message': f'Page has {len(strengths)} strengths and {len(weaknesses)} areas for improvement compared to industry benchmarks'
        }
