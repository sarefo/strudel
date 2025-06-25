#!/usr/bin/env python3
import os
import re
import json
import datetime

def extract_title_and_author(strudel_file_path):
    """Extract the title and author from a strudel file."""
    try:
        with open(strudel_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Look for @title and @by in comments
            title_match = re.search(r'@title\s+(.+?)(?:\s+@by|\n|$)', content)
            author_match = re.search(r'@by\s+(.+?)(?:\n|$)', content)
            
            title = title_match.group(1).strip() if title_match else None
            author = author_match.group(1).strip() if author_match else None
            
            return title, author
    except Exception as e:
        print(f"Error reading {strudel_file_path}: {e}")
    
    return None, None

def generate_strudel_file_list():
    """Scan the files directory and generate a JSON file list for strudel files."""
    files_dir = '../files'
    
    # Ensure the directory exists
    if not os.path.exists(files_dir):
        print(f"Directory {files_dir} does not exist")
        return
    
    # Get all .strudel files
    file_list = []
    for root, dirs, files in os.walk(files_dir):
        for file in files:
            if file.endswith('.strudel'):
                # Get the relative path from the files directory
                rel_path = os.path.relpath(os.path.join(root, file), files_dir)
                full_path = os.path.join(root, file)
                
                # Extract title and author
                title, author = extract_title_and_author(full_path)
                
                # Get file modification time
                mod_time = os.path.getmtime(full_path)
                mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                
                # Use title if available, otherwise filename without extension
                display_title = title if title else os.path.basename(file).replace('.strudel', '')
                
                file_list.append({
                    "filename": file,
                    "title": display_title,
                    "author": author or "Unknown",
                    "modified": mod_date,
                    "path": rel_path.replace('\\', '/')  # Use forward slashes for URLs
                })
    
    # Sort by modification date (newest first) by default
    file_list.sort(key=lambda x: x["modified"], reverse=True)
    
    # Write JSON file
    json_path = '../data/files.json'
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(file_list, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {json_path} with {len(file_list)} strudel files")

if __name__ == "__main__":
    generate_strudel_file_list()