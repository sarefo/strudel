# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Strudel files repository that provides a web interface for managing and accessing Strudel music pattern files. Strudel is a live coding language for music patterns, and this repository serves as a collection/library of `.strudel` files that can be opened directly in strudel.cc.

## Architecture

The repository has a simple static site architecture:

- `index.html` - Main web interface that displays a sortable table of all Strudel files
- `data/` - Contains generated JSON metadata about files and docs
  - `files.json` - Metadata for all .strudel files (title, author, modified date, path)
  - `docs.json` - Metadata for documentation files
- `files/` - Contains the actual .strudel pattern files
- `samples/` - Audio sample files organized by category, referenced by strudel.json
- `strudel.json` - Configuration mapping sample categories to their file lists
- `scripts/` - Python utilities for data generation and local development
- `docs/` - Documentation files (markdown)

### Key Components

**Web Interface (index.html)**:
- Fetches file metadata from `data/files.json`
- For each file, loads the content and base64-encodes it
- Creates direct links to strudel.cc with encoded content as URL fragment
- Provides sortable table interface

**Data Generation (scripts/update_data.py)**:
- Scans `files/` directory for .strudel files
- Extracts metadata from file comments (@title, @by tags)
- Generates `data/files.json` with file listings
- Also handles documentation files in `docs/` directory

## Common Development Commands

### Local Development Server
```bash
# Check if server is already running
curl -s http://localhost:8001 > /dev/null && echo "Server already running" || echo "Server not running"

# From scripts/ directory (only if not already running)
./run_server.sh
# Or manually:
python3 -m http.server 8001 --directory ../
```
The site will be available at http://localhost:8001 (main interface at http://localhost:8001/index.html)

**Note**: Generally, the local server will already be running at port 8001. Always check if it's running before attempting to start it.

### Update File Metadata
```bash
# From scripts/ directory  
python3 update_data.py
```
This regenerates `data/files.json` and `data/docs.json` based on current files.

### Test Strudel Files
```bash
# Test a .strudel file directly in strudel.cc using puppeteer
python3 scripts/test_strudel_file.py files/your_file.strudel
```
This script:
- URL-encodes the Strudel file content
- Opens it directly in strudel.cc using puppeteer
- Attempts to click the play button and start playback
- Checks for JavaScript errors and audio context status
- Takes screenshots for visual verification (saved to temp/screenshots/)
- Provides comprehensive debugging output

**Puppeteer Setup:**
The test script automatically handles both local and global puppeteer installations. To use global puppeteer:
```bash
# Remove local installation (if exists)
rm -rf node_modules package-lock.json

# Install globally
npm install -g puppeteer

# Verify global installation
npm list -g --depth=0 | grep puppeteer
```

The script will automatically fall back to the global installation if local puppeteer is not found.

### File Organization

**Strudel Files**: Place new .strudel files in the `files/` directory. Include metadata in comments:
```
// @title Your Song Title
// @by Your Name
```

**Audio Samples**: Place samples in `samples/category_name/` and update `strudel.json` to reference them.

## Development Notes

- No build process required - this is a static site
- The main interface dynamically loads and encodes .strudel files for strudel.cc integration
- File metadata is cached in JSON files and should be regenerated when files change
- The repository uses GitHub Pages for hosting at the main branch