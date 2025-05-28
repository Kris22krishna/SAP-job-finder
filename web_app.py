from flask import Flask, render_template_string, jsonify, request
import requests
import json
import re
import html
import os

app = Flask(__name__)

def load_env_file(file_path):
    """Load environment variables from a file"""
    env_vars = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Environment file {file_path} not found!")
        return None
    except Exception as e:
        print(f"Error loading environment file: {e}")
        return None
    return env_vars

def sanitize_text(text):
    """Sanitize text to prevent XSS attacks"""
    if not isinstance(text, str):
        return str(text)
    return html.escape(text).strip()

def validate_url(url):
    """Validate if URL is safe and properly formatted"""
    if not url or url == '#':
        return False
    return url.startswith(('http://', 'https://')) and len(url) < 2000

def call_perplexity_api(api_key, prompt):
    """Call Perplexity AI API with the given prompt"""
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that finds job opportunities. Always format job results in a clear markdown table with the exact columns requested. Focus on finding the most current and accurate job postings."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": [],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {type(e).__name__}")
        return None

def parse_markdown_table(text):
    """Parse markdown table from the response text and return structured data"""
    lines = text.split('\n')
    jobs = []
    
    # Find the table in the response
    in_table = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        if '|' in line and ('Job Title' in line or 'Title' in line):
            in_table = True
            continue
        elif in_table and '|' in line and ('---' in line or '--' in line):
            continue
        elif in_table and '|' in line and line.count('|') >= 4:
            # This is a data row
            cells = line.split('|')
            
            if len(cells) >= 5:
                # Clean up the cells and sanitize
                title = sanitize_text(cells[1]) if len(cells) > 1 else "N/A"
                location = sanitize_text(cells[2]) if len(cells) > 2 else "N/A"
                c2c = sanitize_text(cells[3]) if len(cells) > 3 else "N/A"
                visa = sanitize_text(cells[4]) if len(cells) > 4 else "N/A"
                link_cell = cells[5].strip() if len(cells) > 5 else "#"
                
                # Extract actual URL from markdown link if present
                link = "#"  # Default fallback
                
                # Pattern 1: [text](url)
                link_match = re.search(r'\[([^\]]*)\]\(([^)]+)\)', link_cell)
                if link_match:
                    potential_link = link_match.group(2)
                    if validate_url(potential_link):
                        link = potential_link
                # Pattern 2: Look for any URL in the cell
                elif 'http' in link_cell:
                    url_match = re.search(r'https?://[^\s\]]+', link_cell)
                    if url_match:
                        potential_link = url_match.group(0)
                        if validate_url(potential_link):
                            link = potential_link
                
                if title and title != "N/A" and len(title) > 3:
                    job = {
                        "title": title,
                        "location": location,
                        "c2c": c2c,
                        "visa": visa,
                        "link": link
                    }
                    jobs.append(job)
        elif in_table and not line:
            break
    
    return jobs

def extract_citations_as_links(response_data):
    """Extract citation URLs from the response"""
    citations = []
    if 'citations' in response_data and response_data['citations']:
        for citation in response_data['citations']:
            if isinstance(citation, str) and validate_url(citation):
                citations.append(citation)
    return citations

@app.route('/')
def index():
    """Serve the main page"""
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error: index.html not found</h1>
            <p>Please make sure the index.html file exists in the same directory as web_app.py</p>
        </body>
        </html>
        """, 404
    except Exception:
        return """
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error loading page</h1>
            <p>An unexpected error occurred while loading the page.</p>
        </body>
        </html>
        """, 500

@app.route('/search', methods=['POST'])
def search_jobs():
    """API endpoint to search for jobs"""
    try:
        # Load environment variables
        env_vars = load_env_file('config.env')
        if not env_vars:
            return jsonify({"error": "Configuration not available"}), 500
        
        api_key = env_vars.get('PERPLEXITY_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            return jsonify({"error": "API key not configured"}), 500
        
        # Job search prompt
        prompt = """Find 10 current job openings for SAP ABAP in USA that are available for corp-to-corp (C2C) arrangements and are not restricted only to U.S. citizens or green card holders (open to all visa holders). Please present the results in a markdown table with the following columns: Job Title | Location | C2C Allowed | Visa (H1B, L1) | Apply Link (direct link to the application page). Only include jobs that clearly mention C2C eligibility and do not require U.S. citizenship or green card status. Make sure the job application links are pointing to the job directly and not the job board. Also validate to make sure the job posting is live and not a dead link."""
        
        # Call the API
        response = call_perplexity_api(api_key, prompt)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            jobs = parse_markdown_table(content)
            
            # Extract citations as potential job links
            citations = extract_citations_as_links(response)
            
            # If jobs have placeholder links, try to match them with citations
            for i, job in enumerate(jobs):
                if job['link'] == '#' and i < len(citations):
                    job['link'] = citations[i]
            
            return jsonify({
                "jobs": jobs,
                "total": len(jobs),
                "citations": citations[:5],  # Limit citations for security
                "success": True
            })
        else:
            return jsonify({"error": "Search service temporarily unavailable"}), 500
            
    except Exception as e:
        print(f"Error in search_jobs: {type(e).__name__}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    print("🚀 Starting SAP ABAP Job Search Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔍 The app will automatically search for jobs when you load the page!")
    
    # Use production-safe settings
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000) 