#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import csv
import datetime
import uuid
from jinja2 import Environment, FileSystemLoader

from config import REPORT_OUTPUT_DIR, REPORT_TEMPLATE_DIR

class ReportGenerator:
    def __init__(self, url, audit_results, keywords=None):
        self.url = url
        self.audit_results = audit_results
        self.keywords = keywords or []
        self.report_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create output directory if it doesn't exist
        os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(REPORT_TEMPLATE_DIR, exist_ok=True)
    
    def generate_report(self):
        """Generate HTML report by default"""
        return self.generate_html_report()
    
    def generate_html_report(self, output_path=None):
        """Generate HTML report using Jinja2 template"""
        if not output_path:
            output_path = os.path.join(REPORT_OUTPUT_DIR, f'{self.report_id}.html')
        
        # Check if template exists, if not create a default one
        template_path = os.path.join(REPORT_TEMPLATE_DIR, 'report_template.html')
        if not os.path.exists(template_path):
            self._create_default_template()
        
        # Load template
        env = Environment(loader=FileSystemLoader(REPORT_TEMPLATE_DIR))
        template = env.get_template('report_template.html')
        
        # Prepare data for template
        report_data = {
            'url': self.url,
            'report_id': self.report_id,
            'timestamp': self.timestamp,
            'audit_results': self.audit_results,
            'keywords': self.keywords,
            'summary': self.get_summary()
        }
        
        # Render template
        html_content = template.render(**report_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_json_report(self, output_path=None):
        """Generate JSON report"""
        if not output_path:
            output_path = os.path.join(REPORT_OUTPUT_DIR, f'{self.report_id}.json')
        
        # Prepare data
        report_data = {
            'url': self.url,
            'report_id': self.report_id,
            'timestamp': self.timestamp,
            'audit_results': self.audit_results,
            'keywords': self.keywords,
            'summary': self.get_summary()
        }
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        return output_path
    
    def generate_csv_report(self, output_path=None):
        """Generate CSV report"""
        if not output_path:
            output_path = os.path.join(REPORT_OUTPUT_DIR, f'{self.report_id}.csv')
        
        # Flatten audit results for CSV format
        flattened_results = []
        
        for category, category_results in self.audit_results.items():
            for check_name, check_data in category_results.items():
                if isinstance(check_data, dict) and 'status' in check_data:
                    row = {
                        'category': category,
                        'check': check_name,
                        'status': check_data.get('status', ''),
                        'message': check_data.get('message', ''),
                        'value': str(check_data.get('value', ''))
                    }
                    flattened_results.append(row)
        
        # Write to file
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['category', 'check', 'status', 'message', 'value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_results)
        
        return output_path
    
    def get_summary(self):
        """Generate a summary of audit results"""
        summary = {
            'total_checks': 0,
            'passed': 0,
            'warnings': 0,
            'errors': 0,
            'info': 0,
            'score': 0,
            'category_scores': {}
        }
        
        for category, category_results in self.audit_results.items():
            category_summary = {
                'total': 0,
                'passed': 0,
                'warnings': 0,
                'errors': 0,
                'info': 0,
                'score': 0
            }
            
            for check_name, check_data in category_results.items():
                if isinstance(check_data, dict) and 'status' in check_data:
                    summary['total_checks'] += 1
                    category_summary['total'] += 1
                    
                    status = check_data.get('status')
                    if status == 'good':
                        summary['passed'] += 1
                        category_summary['passed'] += 1
                    elif status == 'warning':
                        summary['warnings'] += 1
                        category_summary['warnings'] += 1
                    elif status == 'error':
                        summary['errors'] += 1
                        category_summary['errors'] += 1
                    elif status == 'info':
                        summary['info'] += 1
                        category_summary['info'] += 1
            
            # Calculate category score (excluding info items)
            scorable_items = category_summary['total'] - category_summary['info']
            if scorable_items > 0:
                category_summary['score'] = round((category_summary['passed'] / scorable_items) * 100, 2)
            else:
                category_summary['score'] = 0
            
            summary['category_scores'][category] = category_summary
        
        # Calculate overall score (excluding info items)
        scorable_items = summary['total_checks'] - summary['info']
        if scorable_items > 0:
            summary['score'] = round((summary['passed'] / scorable_items) * 100, 2)
        else:
            summary['score'] = 0
        
        return summary
    
    def _create_default_template(self):
        """Create a default HTML template if none exists"""
        template_path = os.path.join(REPORT_TEMPLATE_DIR, 'report_template.html')
        
        template_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - {{ url }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        header {
            background-color: #4a6cf7;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        header h1 {
            margin-top: 0;
        }
        .summary {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .summary-card {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-right: 20px;
            margin-bottom: 20px;
            min-width: 250px;
            flex: 1;
        }
        .score {
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin: 15px 0;
        }
        .good {
            color: #28a745;
        }
        .warning {
            color: #ffc107;
        }
        .error {
            color: #dc3545;
        }
        .info {
            color: #17a2b8;
        }
        .check-item {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 15px;
        }
        .check-item h4 {
            margin-top: 0;
            display: flex;
            justify-content: space-between;
        }
        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: normal;
        }
        .details {
            margin-top: 10px;
            font-size: 0.9em;
        }
        .category-section {
            margin-bottom: 40px;
        }
        footer {
            text-align: center;
            margin-top: 50px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .summary-card {
                min-width: 100%;
                margin-right: 0;
            }
        }
        .download-pdf {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 20px;
            display: inline-block;
            text-decoration: none;
        }
        .download-pdf:hover {
            background-color: #218838;
        }
        @media print {
            body {
                background-color: white;
                padding: 0;
                font-size: 12pt;
            }
            header {
                background-color: white !important;
                color: black;
                padding: 0;
            }
            .summary-card {
                box-shadow: none;
                border: 1px solid #ddd;
            }
            .check-item {
                box-shadow: none;
                border: 1px solid #ddd;
            }
            .download-pdf {
                display: none;
            }
            .no-print {
                display: none;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>SEO Audit Report</h1>
        <p><strong>URL:</strong> {{ url }}</p>
        <p><strong>Report ID:</strong> {{ report_id }}</p>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
        {% if keywords %}
            <p><strong>Keywords:</strong> {{ keywords|join(', ') }}</p>
        {% endif %}
        <div class="no-print">
            <button class="download-pdf" onclick="window.print()">Download as PDF</button>
        </div>
    </header>
    
    <section class="summary">
        <div class="summary-card">
            <h3>Overall Score</h3>
            <div class="score {% if summary.score >= 80 %}good{% elif summary.score >= 60 %}warning{% else %}error{% endif %}">
                {{ summary.score }}%
            </div>
            <p>Based on {{ summary.total_checks }} checks</p>
        </div>
        
        <div class="summary-card">
            <h3>Results Breakdown</h3>
            <p><span class="status-badge good">Passed:</span> {{ summary.passed }}</p>
            <p><span class="status-badge warning">Warnings:</span> {{ summary.warnings }}</p>
            <p><span class="status-badge error">Errors:</span> {{ summary.errors }}</p>
            <p><span class="status-badge info">Info:</span> {{ summary.info }}</p>
        </div>
        
        <div class="summary-card">
            <h3>Category Scores</h3>
            {% for category, data in summary.category_scores.items() %}
                <p>{{ category|capitalize }}: 
                    <strong class="{% if data.score >= 80 %}good{% elif data.score >= 60 %}warning{% else %}error{% endif %}">
                        {{ data.score }}%
                    </strong>
                </p>
            {% endfor %}
        </div>
    </section>
    
    {% for category, category_results in audit_results.items() %}
        <section class="category-section">
            <h2>{{ category|capitalize }} SEO</h2>
            
            {% for check_name, check_data in category_results.items() %}
                {% if check_data is mapping and check_data.status %}
                    <div class="check-item">
                        <h4>
                            {{ check_name|replace('_', ' ')|capitalize }}
                            <span class="status-badge {{ check_data.status }}">
                                {{ check_data.status|capitalize }}
                            </span>
                        </h4>
                        <p>{{ check_data.message }}</p>
                        
                        {% if check_data.value and check_data.value is mapping %}
                            <div class="details">
                                <strong>Details:</strong>
                                <ul>
                                    {% for key, value in check_data.value.items() %}
                                        {% if value is not mapping and value is not iterable or value is string %}
                                            <li><strong>{{ key|replace('_', ' ')|capitalize }}:</strong> {{ value }}</li>
                                        {% endif %}
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}
                    </div>
                {% endif %}
            {% endfor %}
        </section>
    {% endfor %}
    
    <footer>
        <p>Generated by On-Page SEO Audit Tool &copy; 2025</p>
    </footer>

    <script>
        // Add a custom filename when downloading the PDF
        document.querySelector('.download-pdf').addEventListener('click', function() {
            document.title = 'SEO_Audit_{{ report_id }}_{{ url|replace("http://", "")|replace("https://", "")|replace("/", "_") }}';
        });
    </script>
</body>
</html>
'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
