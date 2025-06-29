#!/usr/bin/env python3
"""
Script to test a Strudel file directly in strudel.cc using puppeteer.
This script reads a .strudel file, encodes it, and opens it in strudel.cc for testing.
"""

import sys
import os
import base64
import urllib.parse
import subprocess
import json
from pathlib import Path

def encode_strudel_content(content):
    """Encode Strudel content for URL fragment (same as index.html logic)"""
    # Handle Unicode properly like the JavaScript version
    encoded_bytes = content.encode('utf-8')
    b64_encoded = base64.b64encode(encoded_bytes).decode('ascii')
    return b64_encoded

def create_strudel_url(content):
    """Create a strudel.cc URL with encoded content"""
    encoded = encode_strudel_content(content)
    return f"https://strudel.cc/#{encoded}"

def test_with_puppeteer(strudel_url, filename):
    """Use puppeteer to test the Strudel file"""
    # Ensure screenshot directory exists
    screenshot_dir = "temp/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Create a simple Node.js script to run puppeteer
    puppeteer_script = f"""
const puppeteer = (() => {{
  try {{
    return require('puppeteer');
  }} catch (e) {{
    // Try global installation path
    const globalPath = require('child_process').execSync('npm root -g', {{encoding: 'utf8'}}).trim();
    return require(globalPath + '/puppeteer');
  }}
}})();

(async () => {{
  const browser = await puppeteer.launch({{ 
    headless: false, 
    args: [
      '--no-sandbox',
      '--autoplay-policy=no-user-gesture-required',
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor'
    ]
  }});
  const page = await browser.newPage();
  
  // Set up audio permissions
  const context = browser.defaultBrowserContext();
  await context.overridePermissions('https://strudel.cc', ['microphone']);
  
  console.log('Opening strudel.cc with encoded file...');
  await page.goto('{strudel_url}', {{ waitUntil: 'networkidle0', timeout: 30000 }});
  
  console.log('Waiting for Strudel to initialize...');
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  // Check what's available in the global scope
  const globalCheck = await page.evaluate(() => {{
    const globals = Object.keys(window).filter(key => 
      key.toLowerCase().includes('strudel') || 
      key.toLowerCase().includes('tone') ||
      key.toLowerCase().includes('audio')
    );
    return {{ globals, hasStrudel: !!window.strudel, hasTone: !!window.Tone }};
  }});
  
  console.log('Global scope check:', globalCheck);
  
  // Take a screenshot
  await page.screenshot({{ path: 'temp/screenshots/strudel_test_{filename}.png', fullPage: true }});
  console.log('Screenshot saved as temp/screenshots/strudel_test_{filename}.png');
  
  // Monitor for JavaScript errors
  page.on('pageerror', error => {{
    console.log('Page error:', error.message);
  }});
  
  page.on('console', msg => {{
    if (msg.type() === 'error') {{
      console.log('Console error:', msg.text());
    }}
  }});
  
  // Try multiple selectors for the play button
  const playSelectors = [
    'button[title*="play"]',
    'button[aria-label*="play"]',
    '.play-button',
    '[data-testid="play"]',
    'button:has-text("play")',
    'button:has-text("▶")',
    'button[class*="play"]',
    '.transport button:first-child',
    'button svg[class*="play"]'
  ];
  
  let playButton = null;
  for (const selector of playSelectors) {{
    try {{
      playButton = await page.$(selector);
      if (playButton) {{
        console.log(`Found play button with selector: ${{selector}}`);
        break;
      }}
    }} catch (e) {{
      // Continue to next selector
    }}
  }}
  
  if (!playButton) {{
    // Try to find any button that might be the play button
    const buttons = await page.$$('button');
    console.log(`Found ${{buttons.length}} buttons on page`);
    
    for (let i = 0; i < buttons.length; i++) {{
      const button = buttons[i];
      const text = await button.evaluate(el => el.textContent || el.title || el.getAttribute('aria-label') || '');
      console.log(`Button ${{i}}: "${{text}}"`);
      
      if (text.toLowerCase().includes('play') || text.includes('▶')) {{
        playButton = button;
        console.log(`Using button ${{i}} as play button`);
        break;
      }}
    }}
  }}
  
  if (playButton) {{
    try {{
      console.log('Clicking play button...');
      await playButton.click();
      
      // Wait for playback to start
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check if audio context is running and try to detect Strudel activity
      const audioStatus = await page.evaluate(() => {{
        const result = {{ contexts: [], strudelActive: false, errors: [] }};
        
        try {{
          // Check for any audio contexts
          if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {{
            // Check global audio context
            if (window.audioContext) {{
              result.contexts.push({{ type: 'global', state: window.audioContext.state }});
            }}
            
            // Check for Strudel-specific contexts
            if (window.strudel) {{
              if (window.strudel.audioContext) {{
                result.contexts.push({{ type: 'strudel', state: window.strudel.audioContext.state }});
              }}
              if (window.strudel.ctx) {{
                result.contexts.push({{ type: 'strudel.ctx', state: window.strudel.ctx.state }});
              }}
            }}
            
            // Check for Tone.js contexts (commonly used by Strudel)
            if (window.Tone && window.Tone.context) {{
              result.contexts.push({{ type: 'Tone', state: window.Tone.context.state }});
            }}
            
            // Check if Strudel is actively playing
            if (window.strudel && typeof window.strudel.playing === 'boolean') {{
              result.strudelActive = window.strudel.playing;
            }}
          }}
        }} catch (e) {{
          result.errors.push(e.message);
        }}
        
        return result;
      }});
      
      console.log('Audio context status:', JSON.stringify(audioStatus, null, 2));
      
      const hasRunningContext = audioStatus.contexts.some(ctx => ctx.state === 'running');
      
      if (hasRunningContext || audioStatus.strudelActive) {{
        console.log('✅ Audio playback started successfully!');
        
        // Let it play for 5 seconds
        console.log('Playing for 5 seconds...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Try to stop playback
        await playButton.click();
        console.log('Stopped playback');
      }} else if (audioStatus.contexts.length > 0) {{
        console.log('⚠️  Audio contexts found but not running. Trying to resume...');
        
        // Try to resume audio contexts
        await page.evaluate(() => {{
          if (window.audioContext && window.audioContext.state === 'suspended') {{
            window.audioContext.resume();
          }}
          if (window.Tone && window.Tone.context && window.Tone.context.state === 'suspended') {{
            window.Tone.context.resume();
          }}
        }});
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        console.log('Attempted to resume audio contexts');
      }} else {{
        console.log('⚠️  No audio contexts found - playback may not have started');
      }}
      
      if (audioStatus.errors.length > 0) {{
        console.log('JavaScript errors during audio check:');
        audioStatus.errors.forEach(err => console.log(`  - ${{err}}`));
      }}
      
    }} catch (error) {{
      console.log('Error during playback:', error.message);
    }}
  }} else {{
    console.log('❌ Could not find play button');
    
    // Take a screenshot of the current state for debugging
    await page.screenshot({{ path: 'temp/screenshots/debug_no_play_button_{filename}.png', fullPage: true }});
    console.log('Debug screenshot saved as temp/screenshots/debug_no_play_button_{filename}.png');
  }}
  
  // Check for any error messages on the page
  const errorMessages = await page.evaluate(() => {{
    const errors = [];
    
    // Look for common error indicators
    const errorSelectors = [
      '.error',
      '.error-message',
      '[class*="error"]',
      '.alert-danger',
      '.notification.error'
    ];
    
    errorSelectors.forEach(selector => {{
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {{
        if (el.textContent.trim()) {{
          errors.push(el.textContent.trim());
        }}
      }});
    }});
    
    return errors;
  }});
  
  if (errorMessages.length > 0) {{
    console.log('❌ Found error messages on page:');
    errorMessages.forEach(msg => console.log(`  - ${{msg}}`));
  }} else {{
    console.log('✅ No error messages found on page');
  }}
  
  console.log('Test completed. Check the screenshot for results.');
  await browser.close();
}})();
"""
    
    # Write the puppeteer script
    script_path = f'puppeteer_test_{filename}.js'
    with open(script_path, 'w') as f:
        f.write(puppeteer_script)
    
    # Run the puppeteer script
    try:
        result = subprocess.run(['node', script_path], capture_output=True, text=True, timeout=60)
        print("Puppeteer output:")
        print(result.stdout)
        if result.stderr:
            print("Puppeteer errors:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Puppeteer test timed out after 60 seconds")
    except FileNotFoundError:
        print("Error: Node.js not found. Please install Node.js and puppeteer to run tests.")
        print("To install puppeteer: npm install puppeteer")
    finally:
        # Clean up the temporary script
        if os.path.exists(script_path):
            os.remove(script_path)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_strudel_file.py <path_to_strudel_file>")
        print("Example: python3 test_strudel_file.py ../files/korobeiniki_enhanced.strudel")
        sys.exit(1)
    
    strudel_file = sys.argv[1]
    
    if not os.path.exists(strudel_file):
        print(f"Error: File '{strudel_file}' not found")
        sys.exit(1)
    
    # Read the Strudel file
    try:
        with open(strudel_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Create the strudel.cc URL
    strudel_url = create_strudel_url(content)
    filename = Path(strudel_file).stem
    
    print(f"Testing Strudel file: {strudel_file}")
    print(f"Generated URL length: {len(strudel_url)} characters")
    print(f"Strudel.cc URL: {strudel_url[:100]}...")
    print()
    
    # Test with puppeteer
    test_with_puppeteer(strudel_url, filename)

if __name__ == "__main__":
    main()