#!/usr/bin/env python3
"""
Project Management Summary Generator
Uses GPT-4 via OpenAI API to generate comprehensive project summaries
"""
import os
import sys
import json
from openai import OpenAI

def read_file(filepath):
    """Read file contents"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return ""

def generate_summary(context_file, prompt_file, output_file, model="gpt-4-turbo"):
    """Generate project summary using GPT-4"""
    
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GITHUB_TOKEN')
    if not api_key:
        print("Error: No API key found. Set OPENAI_API_KEY or GITHUB_TOKEN", file=sys.stderr)
        sys.exit(1)
    
    # For GitHub Models, use different base URL
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    if 'GITHUB_TOKEN' in os.environ and 'OPENAI_API_KEY' not in os.environ:
        base_url = 'https://models.inference.ai.azure.com'
        model = os.getenv('MODEL', 'gpt-4o')
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Read inputs
    prompt_template = read_file(prompt_file)
    project_context = read_file(context_file)
    
    if not prompt_template or not project_context:
        print("Error: Missing prompt or context", file=sys.stderr)
        sys.exit(1)
    
    # Build the full prompt
    system_prompt = """You are an expert project management assistant. 
Your task is to analyze project data and create comprehensive, actionable weekly summaries.
Be specific, reference actual data points, and provide strategic insights."""

    user_prompt = f"""{prompt_template}

## Project Data

{project_context}

Now analyze this data and generate a comprehensive weekly project summary following the structure outlined above."""
    
    print(f"Generating summary using model: {model}", file=sys.stderr)
    print(f"Context size: {len(project_context)} characters", file=sys.stderr)
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Extract the summary
        summary = response.choices[0].message.content
        
        # Write to output file
        with open(output_file, 'w') as f:
            f.write(summary)
        
        print(f"Summary generated successfully: {output_file}", file=sys.stderr)
        print(f"Summary length: {len(summary)} characters", file=sys.stderr)
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 4:
        print("Usage: generate_summary.py <context_file> <prompt_file> <output_file> [model]", file=sys.stderr)
        sys.exit(1)
    
    context_file = sys.argv[1]
    prompt_file = sys.argv[2]
    output_file = sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "gpt-4-turbo"
    
    generate_summary(context_file, prompt_file, output_file, model)

if __name__ == "__main__":
    main()
