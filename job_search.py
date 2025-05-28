import requests
import json
import os
from tabulate import tabulate
import re

def load_env_file(file_path):
    """Load environment variables from a file"""
    env_vars = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"Environment file {file_path} not found!")
        return None
    return env_vars

def call_perplexity_api(api_key, prompt):
    """Call Perplexity AI API with the given prompt"""
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-large-128k-online",  # Best web searching model
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
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def parse_markdown_table(text):
    """Parse markdown table from the response text"""
    lines = text.split('\n')
    table_data = []
    headers = []
    
    # Find the table in the response
    in_table = False
    for line in lines:
        line = line.strip()
        if '|' in line and ('Job Title' in line or 'Title' in line):
            # This is likely the header row
            headers = [cell.strip() for cell in line.split('|') if cell.strip()]
            in_table = True
            continue
        elif in_table and '|' in line and ('---' in line or '--' in line):
            # This is the separator row, skip it
            continue
        elif in_table and '|' in line and line.count('|') >= 4:
            # This is a data row
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            if len(row) >= 4:  # Ensure we have enough columns
                table_data.append(row)
        elif in_table and not line:
            # Empty line might indicate end of table
            break
    
    return headers, table_data

def main():
    # Load environment variables
    env_vars = load_env_file('config.env')
    if not env_vars:
        return
    
    api_key = env_vars.get('PERPLEXITY_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("Please set your PERPLEXITY_API_KEY in config.env file")
        return
    
    # Your job search prompt
    prompt = """Find 10 current job openings for SAP ABAP in USA that are available for corp-to-corp (C2C) arrangements and are not restricted only to U.S. citizens or green card holders (open to all visa holders). Please present the results in a markdown table with the following columns: Job Title | Location | C2C Allowed | Visa (H1B, L1) | Apply Link (direct link to the application page). Only include jobs that clearly mention C2C eligibility and do not require U.S. citizenship or green card status. Make sure the job application links are pointing to the job directly and not the job board. Also validate to make sure the job posting is live and not a dead link."""
    
    print("🔍 Searching for SAP ABAP C2C job opportunities...")
    print("=" * 60)
    
    # Call the API
    response = call_perplexity_api(api_key, prompt)
    
    if response and 'choices' in response:
        content = response['choices'][0]['message']['content']
        
        # Parse the markdown table
        headers, table_data = parse_markdown_table(content)
        
        if table_data:
            print(f"\n✅ Found {len(table_data)} job opportunities:\n")
            
            # Display as a formatted table
            print(tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[30, 20, 15, 15, 40]))
            
            # Also show the raw response for reference
            print("\n" + "="*60)
            print("📄 Raw API Response:")
            print("="*60)
            print(content)
            
            # Show citations if available
            if 'citations' in response and response['citations']:
                print("\n" + "="*60)
                print("📚 Sources:")
                print("="*60)
                for i, citation in enumerate(response['citations'], 1):
                    print(f"{i}. {citation}")
        else:
            print("❌ No job table found in the response. Here's the full response:")
            print(content)
    else:
        print("❌ Failed to get response from Perplexity API")

if __name__ == "__main__":
    main() 