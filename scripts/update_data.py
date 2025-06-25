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

def extract_markdown_title(md_file_path):
    """Extract the title from a markdown file (first H1 heading)."""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Look for first # heading
            title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
            return title_match.group(1).strip() if title_match else None
    except Exception as e:
        print(f"Error reading {md_file_path}: {e}")
    
    return None

def generate_strudel_file_list():
    """Scan the files directory and generate a JSON file list for strudel files."""
    files_dir = '../files'
    
    # Ensure the directory exists
    if not os.path.exists(files_dir):
        print(f"Directory {files_dir} does not exist")
        return []
    
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
    
    return file_list

def generate_docs_list():
    """Scan the docs directory and generate a JSON file list for markdown files."""
    docs_dir = '../docs'
    
    # Ensure the directory exists
    if not os.path.exists(docs_dir):
        print(f"Directory {docs_dir} does not exist")
        return []
    
    # Get all .md files
    docs_list = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                # Get the relative path from the docs directory
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                full_path = os.path.join(root, file)
                
                # Extract title from markdown
                title = extract_markdown_title(full_path)
                
                # Get file modification time
                mod_time = os.path.getmtime(full_path)
                mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                
                # Use title if available, otherwise filename without extension
                display_title = title if title else os.path.basename(file).replace('.md', '').replace('-', ' ').replace('_', ' ').title()
                
                docs_list.append({
                    "filename": file,
                    "title": display_title,
                    "modified": mod_date,
                    "path": rel_path.replace('\\', '/')  # Use forward slashes for URLs
                })
    
    # Sort by title alphabetically
    docs_list.sort(key=lambda x: x["title"].lower())
    
    return docs_list

def main():
    """Generate both strudel files and docs lists."""
    # Generate strudel files list
    strudel_files = generate_strudel_file_list()
    
    # Write strudel files JSON
    strudel_json_path = '../data/files.json'
    os.makedirs(os.path.dirname(strudel_json_path), exist_ok=True)
    
    with open(strudel_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(strudel_files, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {strudel_json_path} with {len(strudel_files)} strudel files")
    
    # Generate docs list
    docs_files = generate_docs_list()
    
    # Write docs JSON
    docs_json_path = '../data/docs.json'
    
    with open(docs_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(docs_files, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {docs_json_path} with {len(docs_files)} documentation files")

if __name__ == "__main__":
    main()