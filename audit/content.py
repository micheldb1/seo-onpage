#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import os
import sys

# Set NLTK data path to a directory in the project
NLTK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.insert(0, NLTK_DATA_DIR)  # Make our custom path the highest priority

# Define fallback tokenizers that don't rely on NLTK data
def simple_word_tokenize(text):
    return re.findall(r'\w+', text.lower())

def simple_sent_tokenize(text):
    return re.split(r'[.!?]+', text)

# Download necessary NLTK data with better error handling
def download_nltk_data():
    try:
        # Try to find the punkt tokenizer
        try:
            nltk.data.find('tokenizers/punkt')
            print("NLTK punkt tokenizer already downloaded.")
            return True
        except LookupError:
            # Download punkt tokenizer
            print(f"Downloading NLTK punkt tokenizer to {NLTK_DATA_DIR}...")
            nltk.download('punkt', download_dir=NLTK_DATA_DIR, quiet=False, raise_on_error=True, proxy=None)
            print("NLTK punkt tokenizer successfully downloaded.")
            return True
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        print("Using simple tokenization as fallback...")
        return False

# Try to download NLTK data
nltk_download_success = download_nltk_data()

# Define our tokenizer functions (not just references to the functions)
def word_tokenizer(text):
    return simple_word_tokenize(text)

def sent_tokenizer(text):
    return simple_sent_tokenize(text)

from config import (
    DEFAULT_USER_AGENT,
    TIMEOUT,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    MAX_META_DESCRIPTION_LENGTH,
    MIN_META_DESCRIPTION_LENGTH,
    MIN_CONTENT_LENGTH
)

class ContentSEOAudit:
    def __init__(self, url, user_keywords=None):
        self.url = url
        self.results = {}
        self.headers = {
            'User-Agent': DEFAULT_USER_AGENT
        }
        self.soup = None
        self.text_content = ""
        self.word_count = 0
        self.keywords = []
        self.user_keywords = user_keywords or []
    
    def run_audit(self):
        """Run all content SEO audit checks"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            self.soup = BeautifulSoup(response.text, 'html.parser')
            self.extract_text_content()
            
            self.check_title_tag()
            self.check_meta_description()
            self.check_heading_structure()
            self.check_content_length()
            self.check_keyword_usage()
            self.check_content_quality()
            self.check_image_alt_text()
            self.check_outbound_links()
            
            return self.results
        except Exception as e:
            self.results['error'] = {
                'value': str(e),
                'status': 'error',
                'message': f'Failed to perform content audit: {str(e)}'
            }
            return self.results
    
    def extract_text_content(self):
        """Extract and clean text content from the page"""
        if not self.soup:
            return
        
        # Remove script and style elements
        for script_or_style in self.soup(['script', 'style', 'nav', 'footer', 'header']):
            script_or_style.decompose()
        
        # Get text and clean it
        text = self.soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        self.text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Calculate word count
        self.word_count = len(word_tokenizer(self.text_content))
    
    def check_title_tag(self):
        """Check title tag"""
        title_tag = self.soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            title_length = len(title)
            
            issues = []
            if title_length > MAX_TITLE_LENGTH:
                issues.append(f'Title length ({title_length}) exceeds recommended maximum ({MAX_TITLE_LENGTH})')
            elif title_length < MIN_TITLE_LENGTH:
                issues.append(f'Title length ({title_length}) is below recommended minimum ({MIN_TITLE_LENGTH})')
            
            # Check for user-specified keywords in title
            if self.user_keywords:
                title_lower = title.lower()
                missing_keywords = [kw for kw in self.user_keywords if kw.lower() not in title_lower]
                if missing_keywords:
                    issues.append(f'Title does not contain these target keywords: {", ".join(missing_keywords)}')
            
            # Get potential keywords for reference
            potential_keywords = self.extract_potential_keywords()[:5]
            
            self.results['title_tag'] = {
                'value': title,
                'length': title_length,
                'potential_keywords': potential_keywords,
                'user_keywords': self.user_keywords,
                'status': 'good' if not issues else 'warning',
                'message': 'Title tag is well-optimized' if not issues else '; '.join(issues)
            }
        else:
            self.results['title_tag'] = {
                'value': None,
                'length': 0,
                'status': 'error',
                'message': 'No title tag found'
            }
    
    def check_meta_description(self):
        """Check meta description"""
        meta_desc = self.soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
            desc_length = len(description)
            
            issues = []
            if desc_length > MAX_META_DESCRIPTION_LENGTH:
                issues.append(f'Meta description length ({desc_length}) exceeds recommended maximum ({MAX_META_DESCRIPTION_LENGTH})')
            elif desc_length < MIN_META_DESCRIPTION_LENGTH:
                issues.append(f'Meta description length ({desc_length}) is below recommended minimum ({MIN_META_DESCRIPTION_LENGTH})')
            
            # Check for user-specified keywords in meta description
            if self.user_keywords:
                desc_lower = description.lower()
                missing_keywords = [kw for kw in self.user_keywords if kw.lower() not in desc_lower]
                if missing_keywords:
                    issues.append(f'Meta description does not contain these target keywords: {", ".join(missing_keywords)}')
            
            # Get potential keywords for reference
            potential_keywords = self.extract_potential_keywords()[:5]
            
            self.results['meta_description'] = {
                'value': description,
                'length': desc_length,
                'potential_keywords': potential_keywords,
                'user_keywords': self.user_keywords,
                'status': 'good' if not issues else 'warning',
                'message': 'Meta description is well-optimized' if not issues else '; '.join(issues)
            }
        else:
            self.results['meta_description'] = {
                'value': None,
                'length': 0,
                'status': 'error',
                'message': 'No meta description found'
            }
    
    def check_heading_structure(self):
        """Check heading structure (H1, H2, etc.)"""
        headings = {
            'h1': self.soup.find_all('h1'),
            'h2': self.soup.find_all('h2'),
            'h3': self.soup.find_all('h3'),
            'h4': self.soup.find_all('h4'),
            'h5': self.soup.find_all('h5'),
            'h6': self.soup.find_all('h6')
        }
        
        h1_count = len(headings['h1'])
        h2_count = len(headings['h2'])
        
        issues = []
        if h1_count == 0:
            issues.append('No H1 heading found')
        elif h1_count > 1:
            issues.append(f'Multiple H1 headings found ({h1_count})')
        
        if h2_count == 0:
            issues.append('No H2 headings found')
        
        # Check if headings follow a hierarchical structure
        if h1_count > 0 and h2_count > 0:
            # Get the positions of all headings
            all_headings = []
            for level, tags in headings.items():
                for tag in tags:
                    all_headings.append((level, tag))
            
            # Sort headings by their position in the document
            try:
                # Try to sort by the position of the tag in the document
                all_headings.sort(key=lambda x: str(x[1]))
            except Exception:
                # If sorting fails, we can still proceed with the unsorted list
                pass
            
            # Check for hierarchy issues
            for i in range(1, len(all_headings)):
                prev_level = int(all_headings[i-1][0][1])
                curr_level = int(all_headings[i][0][1])
                if curr_level > prev_level + 1:
                    issues.append(f'Heading hierarchy skip from {all_headings[i-1][0]} to {all_headings[i][0]}')
        
        # Extract heading texts for analysis
        heading_texts = {}
        for level, tags in headings.items():
            heading_texts[level] = [tag.get_text().strip() for tag in tags]
        
        # Check for user-specified keywords in H1
        if h1_count > 0 and self.user_keywords:
            h1_text = heading_texts['h1'][0].lower()
            missing_keywords = [kw for kw in self.user_keywords if kw.lower() not in h1_text]
            if missing_keywords:
                issues.append(f'H1 heading does not contain these target keywords: {", ".join(missing_keywords)}')
        
        # Get potential keywords for reference
        potential_keywords = self.extract_potential_keywords()[:5]
        
        self.results['heading_structure'] = {
            'value': {
                'h1_count': h1_count,
                'h2_count': h2_count,
                'h3_count': len(headings['h3']),
                'h4_count': len(headings['h4']),
                'h5_count': len(headings['h5']),
                'h6_count': len(headings['h6']),
                'heading_texts': heading_texts,
                'potential_keywords': potential_keywords,
                'user_keywords': self.user_keywords
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Heading structure is well-optimized' if not issues else '; '.join(issues)
        }
    
    def check_content_length(self):
        """Check content length"""
        if self.word_count < MIN_CONTENT_LENGTH:
            status = 'warning'
            message = f'Content length ({self.word_count} words) is below recommended minimum ({MIN_CONTENT_LENGTH} words)'
        else:
            status = 'good'
            message = f'Content length ({self.word_count} words) is sufficient'
        
        self.results['content_length'] = {
            'value': self.word_count,
            'status': status,
            'message': message
        }
    
    def extract_potential_keywords(self):
        """Extract potential keywords from the content"""
        if not self.text_content:
            return []
        
        # Tokenize and count words
        words = word_tokenizer(self.text_content.lower())
        
        # Remove stopwords (simple approach)
        stopwords = ['the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were']
        filtered_words = [word for word in words if word.isalnum() and word not in stopwords]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        # Get most common words as potential keywords
        self.keywords = [word for word, count in word_freq.most_common(10)]
        return self.keywords
    
    def check_keyword_usage(self):
        """Check keyword usage and density"""
        if not self.text_content or self.word_count == 0:
            self.results['keyword_usage'] = {
                'value': None,
                'status': 'error',
                'message': 'No content to analyze keywords'
            }
            return
        
        # Extract potential keywords
        keywords = self.extract_potential_keywords()
        if not keywords:
            self.results['keyword_usage'] = {
                'value': None,
                'status': 'warning',
                'message': 'Could not extract potential keywords'
            }
            return
        
        # Calculate keyword density
        keyword_density = {}
        for keyword in keywords[:5]:  # Top 5 keywords
            count = self.text_content.lower().count(keyword)
            density = (count / self.word_count) * 100
            keyword_density[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        # Check for keyword stuffing
        has_keyword_stuffing = any(data['density'] > 5.0 for data in keyword_density.values())
        
        self.results['keyword_usage'] = {
            'value': keyword_density,
            'status': 'warning' if has_keyword_stuffing else 'good',
            'message': 'Potential keyword stuffing detected' if has_keyword_stuffing else 'Keyword usage appears natural'
        }
    
    def check_content_quality(self):
        """Check content quality metrics"""
        if not self.text_content:
            self.results['content_quality'] = {
                'value': None,
                'status': 'error',
                'message': 'No content to analyze quality'
            }
            return
        
        # Sentence count
        sentences = sent_tokenizer(self.text_content)
        sentence_count = len(sentences)
        
        # Average sentence length
        avg_sentence_length = self.word_count / max(1, sentence_count)
        
        # Average word length
        avg_word_length = sum(len(word) for word in word_tokenizer(self.text_content)) / max(1, self.word_count)
        
        # Readability score (simplified Flesch-Kincaid)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        
        issues = []
        if avg_sentence_length > 25:
            issues.append('Average sentence length is too high')
        if readability_score < 60:
            issues.append('Content may be difficult to read')
        if sentence_count < 5:
            issues.append('Content has very few sentences')
        
        self.results['content_quality'] = {
            'value': {
                'sentence_count': sentence_count,
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_word_length': round(avg_word_length, 2),
                'readability_score': round(readability_score, 2)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Content quality is good' if not issues else '; '.join(issues)
        }
    
    def check_image_alt_text(self):
        """Check image alt text"""
        images = self.soup.find_all('img')
        
        if not images:
            self.results['image_alt_text'] = {
                'value': None,
                'status': 'info',
                'message': 'No images found on the page'
            }
            return
        
        images_with_alt = [img for img in images if img.get('alt')]
        images_without_alt = [img for img in images if not img.get('alt')]
        
        alt_text_percentage = (len(images_with_alt) / len(images)) * 100
        
        issues = []
        if images_without_alt:
            issues.append(f'{len(images_without_alt)} out of {len(images)} images missing alt text')
        
        # Check if alt text contains keywords
        keywords = self.extract_potential_keywords()[:5]
        keyword_in_alt = False
        
        for img in images_with_alt:
            alt_text = img.get('alt', '').lower()
            if any(kw.lower() in alt_text for kw in keywords):
                keyword_in_alt = True
                break
        
        if not keyword_in_alt and images_with_alt:
            issues.append('Image alt text may not include relevant keywords')
        
        self.results['image_alt_text'] = {
            'value': {
                'total_images': len(images),
                'images_with_alt': len(images_with_alt),
                'alt_text_percentage': round(alt_text_percentage, 2)
            },
            'status': 'good' if alt_text_percentage > 90 and not issues else 'warning',
            'message': 'Images have proper alt text' if alt_text_percentage > 90 and not issues else '; '.join(issues)
        }
    
    def check_outbound_links(self):
        """Check outbound links"""
        links = self.soup.find_all('a', href=True)
        
        if not links:
            self.results['outbound_links'] = {
                'value': None,
                'status': 'info',
                'message': 'No links found on the page'
            }
            return
        
        internal_links = []
        external_links = []
        
        for link in links:
            href = link.get('href')
            if href.startswith('#') or not href or href.startswith('javascript:'):
                continue
            
            if href.startswith('/') or self.url in href:
                internal_links.append(href)
            else:
                external_links.append(href)
        
        # Check for nofollow attributes
        nofollow_links = [link for link in links if 'nofollow' in link.get('rel', [])]
        
        issues = []
        if not external_links:
            issues.append('No external links found')
        
        if len(internal_links) < 3:
            issues.append('Few internal links found')
        
        self.results['outbound_links'] = {
            'value': {
                'total_links': len(links),
                'internal_links': len(internal_links),
                'external_links': len(external_links),
                'nofollow_links': len(nofollow_links)
            },
            'status': 'good' if not issues else 'warning',
            'message': 'Link structure is good' if not issues else '; '.join(issues)
        }

    def extract_keywords(self):
        """Extract keywords from content"""
        if not self.text_content:
            return []
        
        # Tokenize and count words
        words = word_tokenizer(self.text_content.lower())
        
        # Remove stopwords (simple approach)
        stopwords = ['the', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were']
        filtered_words = [word for word in words if word.isalnum() and word not in stopwords]
        
        # Count word frequency
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(10)
        
        # Calculate keyword density
        total_words = len(filtered_words)
        keyword_density = {word: (count / total_words) * 100 for word, count in top_keywords}
        
        # Store keywords with density
        self.keywords = [(word, count, keyword_density[word]) for word, count in top_keywords]
        
        return self.keywords
    
    def check_keyword_in_title(self):
        """Check if primary keyword is in title"""
        title = self.soup.title.string if self.soup.title else ""
        
        if not title or not self.keywords:
            self.results['keyword_in_title'] = {
                'status': 'warning',
                'message': 'Could not check keyword in title: missing title or keywords.'
            }
            return
        
        # Get primary keyword (most frequent)
        primary_keyword = self.keywords[0][0] if self.keywords else ""
        
        if primary_keyword.lower() in title.lower():
            self.results['keyword_in_title'] = {
                'status': 'good',
                'message': f'Primary keyword "{primary_keyword}" found in title.'
            }
        else:
            self.results['keyword_in_title'] = {
                'status': 'warning',
                'message': f'Primary keyword "{primary_keyword}" not found in title.'
            }
    
    def check_readability(self):
        """Check content readability"""
        if not self.text_content or self.word_count < 100:
            self.results['readability'] = {
                'status': 'warning',
                'message': 'Not enough content to analyze readability.'
            }
            return
        
        # Sentence count
        sentences = sent_tokenizer(self.text_content)
        sentence_count = len(sentences)
        
        # Average sentence length
        avg_sentence_length = self.word_count / max(1, sentence_count)
        
        # Average word length
        avg_word_length = sum(len(word) for word in word_tokenizer(self.text_content)) / max(1, self.word_count)
        
        # Readability score (simplified Flesch-Kincaid)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        
        # Interpret score
        if readability_score >= 80:
            status = 'good'
            message = 'Content is very easy to read.'
        elif readability_score >= 60:
            status = 'good'
            message = 'Content is easy to read.'
        elif readability_score >= 50:
            status = 'warning'
            message = 'Content is fairly difficult to read.'
        else:
            status = 'warning'
            message = 'Content is difficult to read. Consider simplifying.'
        
        self.results['readability'] = {
            'status': status,
            'message': message,
            'value': {
                'score': round(readability_score, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_word_length': round(avg_word_length, 2)
            }
        }
