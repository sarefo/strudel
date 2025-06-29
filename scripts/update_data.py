#!/usr/bin/env python3
import os
import re
import json
import datetime
from pathlib import Path

def extract_title_and_author(strudel_file_path):
    """Extract the title, author, version, and stage from a strudel file."""
    try:
        with open(strudel_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Look for @title, @by, and @version in comments
            title_match = re.search(r'@title\s+(.+?)(?:\s+@by|\n|$)', content)
            author_match = re.search(r'@by\s+(.+?)(?:\n|$)', content)
            version_match = re.search(r'@version\s+(.+?)(?:\n|$)', content)
            
            # Look for @stage with [x] checkboxes
            stage_match = re.search(r'@stage\s+(.+?)(?:\n|$)', content)
            stage = "test"  # default
            if stage_match:
                stage_line = stage_match.group(1).strip()
                if '[x] published' in stage_line:
                    stage = "published"
                elif '[x] building' in stage_line:
                    stage = "building"
                else:
                    stage = "test"
            
            title = title_match.group(1).strip() if title_match else None
            author = author_match.group(1).strip() if author_match else None
            version = version_match.group(1).strip() if version_match else None
            
            return title, author, version, stage
    except Exception as e:
        print(f"Error reading {strudel_file_path}: {e}")
    
    return None, None, None, "test"

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
    # Get the script directory and build absolute path to files directory
    script_dir = Path(__file__).parent.absolute()
    files_dir = script_dir.parent / 'files'
    
    # Ensure the directory exists
    if not files_dir.exists():
        print(f"Directory {files_dir} does not exist")
        return []
    
    # Get all .strudel files
    file_list = []
    for root, dirs, files in os.walk(str(files_dir)):
        for file in files:
            if file.endswith('.strudel'):
                # Get the relative path from the files directory
                rel_path = os.path.relpath(os.path.join(root, file), str(files_dir))
                full_path = os.path.join(root, file)
                
                # Extract title, author, version, and stage
                title, author, version, stage = extract_title_and_author(full_path)
                
                # Get file modification time
                mod_time = os.path.getmtime(full_path)
                mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
                
                # Use title if available, otherwise filename without extension
                display_title = title if title else os.path.basename(file).replace('.strudel', '')
                
                file_list.append({
                    "filename": file,
                    "title": display_title,
                    "author": author or "Unknown",
                    "version": version,
                    "modified": mod_date,
                    "stage": stage,
                    "path": rel_path.replace('\\', '/')  # Use forward slashes for URLs
                })
    
    # Sort by modification date (newest first) by default
    file_list.sort(key=lambda x: x["modified"], reverse=True)
    
    return file_list

def generate_docs_list():
    """Scan the docs directory and generate a JSON file list for markdown files."""
    # Get the script directory and build absolute path to docs directory
    script_dir = Path(__file__).parent.absolute()
    docs_dir = script_dir.parent / 'docs'
    
    # Ensure the directory exists
    if not docs_dir.exists():
        print(f"Directory {docs_dir} does not exist")
        return []
    
    # Get all .md files
    docs_list = []
    for root, dirs, files in os.walk(str(docs_dir)):
        for file in files:
            if file.endswith('.md'):
                # Get the relative path from the docs directory
                rel_path = os.path.relpath(os.path.join(root, file), str(docs_dir))
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

def generate_strudel_sample_config():
    """Scan the samples directory and generate strudel.json configuration."""
    # Get the script directory and build absolute path to samples directory
    script_dir = Path(__file__).parent.absolute()
    samples_dir = script_dir.parent / 'samples'
    
    # Ensure the directory exists
    if not samples_dir.exists():
        print(f"Directory {samples_dir} does not exist")
        return {}
    
    # Build the sample configuration
    config = {}
    
    # Scan each subdirectory in samples/
    for category_dir in samples_dir.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            category_files = []
            
            # Get all .wav files in this category
            for wav_file in category_dir.glob("*.wav"):
                # Store as category/filename.wav format
                relative_path = f"{category_name}/{wav_file.name}"
                category_files.append(relative_path)
            
            # Sort files for consistent output
            category_files.sort()
            
            if category_files:  # Only add categories that have files
                config[category_name] = category_files
    
    # Add the base URL for GitHub raw content
    config["_base"] = "https://raw.githubusercontent.com/sarefo/strudel/main/samples/"
    
    return config

def main():
    """Generate strudel files, docs lists, and sample configuration."""
    # Get the script directory and build absolute paths for output
    script_dir = Path(__file__).parent.absolute()
    data_dir = script_dir.parent / 'data'
    repo_root = script_dir.parent
    
    # Generate strudel files list
    strudel_files = generate_strudel_file_list()
    
    # Write strudel files JSON
    strudel_json_path = data_dir / 'files.json'
    data_dir.mkdir(exist_ok=True)
    
    with open(strudel_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(strudel_files, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {strudel_json_path} with {len(strudel_files)} strudel files")
    
    # Generate docs list
    docs_files = generate_docs_list()
    
    # Write docs JSON
    docs_json_path = data_dir / 'docs.json'
    
    with open(docs_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(docs_files, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {docs_json_path} with {len(docs_files)} documentation files")
    
    # Generate strudel sample configuration
    sample_config = generate_strudel_sample_config()
    
    # Write strudel.json
    strudel_config_path = repo_root / 'strudel.json'
    
    with open(strudel_config_path, 'w', encoding='utf-8') as json_file:
        json.dump(sample_config, json_file, indent=2, ensure_ascii=False)
    
    print(f"Generated {strudel_config_path} with {len(sample_config) - 1} sample categories")

if __name__ == "__main__":
    main()