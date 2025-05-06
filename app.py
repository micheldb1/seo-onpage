#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from audit.technical import TechnicalSEOAudit
from audit.content import ContentSEOAudit
from audit.structured_data import StructuredDataAudit
from audit.links import LinkAnalysis
from audit.ux import UXFactorsAudit
from audit.advanced import AdvancedSEOAudit
from audit.enhanced_technical import EnhancedTechnicalAudit
from audit.multimedia import MultimediaAudit
from audit.eureka import EurekaAnalysis
from utils.url_processor import URLProcessor
from utils.report_generator import ReportGenerator
from config import REPORT_OUTPUT_DIR, GOOGLE_PAGESPEED_API_KEY

# Debug: Print API key to console
print(f"PageSpeed API Key: {GOOGLE_PAGESPEED_API_KEY}")

# Initialize Flask app
app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static', static_url_path='/static')

# Configure CORS - not needed for single-domain deployment but kept for flexibility
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Create necessary directories if they don't exist
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)

# Add a route to serve report files directly from the reports/output directory
@app.route('/static/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(REPORT_OUTPUT_DIR, filename)

# Add a route to serve static files explicitly
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('ui/static/css', filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('ui/static/js', filename)

@app.route('/static/img/<path:filename>')
def serve_img(filename):
    return send_from_directory('ui/static/img', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('ui/static', filename)

@app.route('/audit', methods=['POST'])
def run_audit():
    data = request.get_json()
    url = data.get('url')
    audit_types = data.get('audit_types', ['technical', 'content', 'structured_data', 'links', 'ux', 'advanced', 'enhanced_technical', 'multimedia', 'eureka'])
    keywords = data.get('keywords', [])
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Process URL
    url_processor = URLProcessor(url)
    processed_url = url_processor.process()
    
    # Initialize audit results
    audit_results = {}
    
    # Run selected audits
    if 'technical' in audit_types:
        technical_audit = TechnicalSEOAudit(processed_url)
        audit_results['technical'] = technical_audit.run_audit()
    
    if 'content' in audit_types:
        content_audit = ContentSEOAudit(processed_url, keywords)
        audit_results['content'] = content_audit.run_audit()
    
    if 'structured_data' in audit_types:
        structured_data_audit = StructuredDataAudit(processed_url)
        audit_results['structured_data'] = structured_data_audit.run_audit()
    
    if 'links' in audit_types:
        link_analysis = LinkAnalysis(processed_url)
        audit_results['links'] = link_analysis.run_audit()
    
    if 'ux' in audit_types:
        ux_audit = UXFactorsAudit(processed_url)
        audit_results['ux'] = ux_audit.run_audit()
    
    if 'advanced' in audit_types:
        advanced_audit = AdvancedSEOAudit(processed_url)
        audit_results['advanced'] = advanced_audit.run_audit()
        
    if 'enhanced_technical' in audit_types:
        enhanced_technical_audit = EnhancedTechnicalAudit(processed_url)
        audit_results['enhanced_technical'] = enhanced_technical_audit.run_audit()
        
    if 'multimedia' in audit_types:
        multimedia_audit = MultimediaAudit(processed_url)
        audit_results['multimedia'] = multimedia_audit.run_audit()
        
    if 'eureka' in audit_types:
        eureka_analysis = EurekaAnalysis(processed_url, keywords)
        audit_results['eureka'] = eureka_analysis.run_analysis()
    
    # Generate report
    report_generator = ReportGenerator(processed_url, audit_results, keywords)
    report_path = report_generator.generate_report()
    
    # Extract report ID from the report path
    report_id = os.path.basename(report_path).split('.')[0]
    
    return jsonify({
        'success': True,
        'url': processed_url,
        'report_path': report_path,
        'report_id': report_id,
        'summary': report_generator.get_summary()
    })

@app.route('/api/audit', methods=['POST'])
def api_audit():
    data = request.get_json()
    url = data.get('url')
    audit_types = data.get('audit_types', ['technical', 'content', 'structured_data', 'links', 'ux', 'advanced', 'enhanced_technical', 'multimedia', 'eureka'])
    keywords = data.get('keywords', [])
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Process URL
    url_processor = URLProcessor(url)
    processed_url = url_processor.process()
    
    # Initialize audit results
    audit_results = {}
    
    # Run selected audits
    if 'technical' in audit_types:
        technical_audit = TechnicalSEOAudit(processed_url)
        audit_results['technical'] = technical_audit.run_audit()
    
    if 'content' in audit_types:
        content_audit = ContentSEOAudit(processed_url, keywords)
        audit_results['content'] = content_audit.run_audit()
    
    if 'structured_data' in audit_types:
        structured_data_audit = StructuredDataAudit(processed_url)
        audit_results['structured_data'] = structured_data_audit.run_audit()
    
    if 'links' in audit_types:
        link_analysis = LinkAnalysis(processed_url)
        audit_results['links'] = link_analysis.run_audit()
    
    if 'ux' in audit_types:
        ux_audit = UXFactorsAudit(processed_url)
        audit_results['ux'] = ux_audit.run_audit()
    
    if 'advanced' in audit_types:
        advanced_audit = AdvancedSEOAudit(processed_url)
        audit_results['advanced'] = advanced_audit.run_audit()
        
    if 'enhanced_technical' in audit_types:
        enhanced_technical_audit = EnhancedTechnicalAudit(processed_url)
        audit_results['enhanced_technical'] = enhanced_technical_audit.run_audit()
        
    if 'multimedia' in audit_types:
        multimedia_audit = MultimediaAudit(processed_url)
        audit_results['multimedia'] = multimedia_audit.run_audit()
        
    if 'eureka' in audit_types:
        eureka_analysis = EurekaAnalysis(processed_url, keywords)
        audit_results['eureka'] = eureka_analysis.run_analysis()
    
    # Generate report
    report_generator = ReportGenerator(processed_url, audit_results, keywords)
    report_path = report_generator.generate_report()
    
    # Extract report ID from the report path
    report_id = os.path.basename(report_path).split('.')[0]
    
    return jsonify({
        'success': True,
        'url': processed_url,
        'report_path': report_path,
        'report_id': report_id,
        'summary': report_generator.get_summary()
    })

@app.route('/api/reports/<report_id>', methods=['GET'])
def api_view_report(report_id):
    report_path = os.path.join(REPORT_OUTPUT_DIR, f'{report_id}.html')
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    return jsonify({'error': 'Report not found'}), 404

@app.route('/reports/<report_id>')
def view_report(report_id):
    report_path = os.path.join(REPORT_OUTPUT_DIR, f'{report_id}.html')
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    return render_template('404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def run_cli():
    parser = argparse.ArgumentParser(description='On-Page SEO Audit Tool')
    parser.add_argument('url', help='URL to audit')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['html', 'json', 'csv'], default='html', help='Output format')
    parser.add_argument('--types', '-t', nargs='+', 
                      choices=['technical', 'content', 'structured_data', 'links', 'ux', 'advanced', 'enhanced_technical', 'multimedia', 'eureka', 'all'], 
                      default=['all'], help='Audit types to run')
    parser.add_argument('--keywords', '-k', nargs='+', help='Target keywords for the content')
    
    args = parser.parse_args()
    
    # Process URL
    url_processor = URLProcessor(args.url)
    processed_url = url_processor.process()
    
    # Determine which audit types to run
    audit_types = ['technical', 'content', 'structured_data', 'links', 'ux', 'advanced', 'enhanced_technical', 'multimedia', 'eureka'] if 'all' in args.types else args.types
    
    # Initialize audit results
    audit_results = {}
    
    # Run selected audits
    for audit_type in audit_types:
        if audit_type == 'technical':
            technical_audit = TechnicalSEOAudit(processed_url)
            audit_results['technical'] = technical_audit.run_audit()
        elif audit_type == 'content':
            content_audit = ContentSEOAudit(processed_url, args.keywords or [])
            audit_results['content'] = content_audit.run_audit()
        elif audit_type == 'structured_data':
            structured_data_audit = StructuredDataAudit(processed_url)
            audit_results['structured_data'] = structured_data_audit.run_audit()
        elif audit_type == 'links':
            link_analysis = LinkAnalysis(processed_url)
            audit_results['links'] = link_analysis.run_audit()
        elif audit_type == 'ux':
            ux_audit = UXFactorsAudit(processed_url)
            audit_results['ux'] = ux_audit.run_audit()
        elif audit_type == 'advanced':
            advanced_audit = AdvancedSEOAudit(processed_url)
            audit_results['advanced'] = advanced_audit.run_audit()
        elif audit_type == 'enhanced_technical':
            enhanced_technical_audit = EnhancedTechnicalAudit(processed_url)
            audit_results['enhanced_technical'] = enhanced_technical_audit.run_audit()
        elif audit_type == 'multimedia':
            multimedia_audit = MultimediaAudit(processed_url)
            audit_results['multimedia'] = multimedia_audit.run_audit()
        elif audit_type == 'eureka':
            eureka_analysis = EurekaAnalysis(processed_url, args.keywords or [])
            audit_results['eureka'] = eureka_analysis.run_analysis()
    
    # Generate report
    report_generator = ReportGenerator(processed_url, audit_results, args.keywords or [])
    
    if args.format == 'html':
        output_path = args.output or os.path.join(REPORT_OUTPUT_DIR, f'{processed_url.replace("://", "_").replace(".", "_").replace("/", "_")}.html')
        report_generator.generate_html_report(output_path)
        print(f'HTML report generated: {output_path}')
    elif args.format == 'json':
        output_path = args.output or os.path.join(REPORT_OUTPUT_DIR, f'{processed_url.replace("://", "_").replace(".", "_").replace("/", "_")}.json')
        report_generator.generate_json_report(output_path)
        print(f'JSON report generated: {output_path}')
    elif args.format == 'csv':
        output_path = args.output or os.path.join(REPORT_OUTPUT_DIR, f'{processed_url.replace("://", "_").replace(".", "_").replace("/", "_")}.csv')
        report_generator.generate_csv_report(output_path)
        print(f'CSV report generated: {output_path}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_cli()
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)
