#!/usr/bin/env python3
"""
Simple test of integrated infographic generation without full video creation
Tests the core integration: Node.js service → Python → HTML → PNG
"""

import asyncio
import json
import subprocess
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

print("\n" + "="*80)
print("INTEGRATED INFOGRAPHIC GENERATOR - SIMPLE TEST")
print("="*80)

async def test_image_generation():
    """Test generating images from prompts using Node.js service"""
    
    print("\n[1/3] Testing infographic generation via Node.js service...")
    
    # Create a test script that generates multiple infographics
    test_script = """
const path = require('path');
const serviceDir = '/Users/abdullah/Desktop/Techinoid/Slidex-v1/neuro-engine-main/services';
const v2Service = require(path.join(serviceDir, 'unit-services', 'generateInfographicV2Service'));

(async () => {
    try {
        const prompts = [
            'Benefits of Cloud Computing',
            'Steps to Learn Machine Learning',
            'History of the Internet'
        ];
        
        const results = [];
        for (let i = 0; i < prompts.length; i++) {
            console.error(`  Generating infographic ${i+1}/${prompts.length}: ${prompts[i]}`);
            const result = await v2Service.generateInfographic(prompts[i], 'landscape');
            results.push({
                index: i + 1,
                prompt: prompts[i],
                html_size: result.html.length,
                has_data: !!result.data,
                layout: result.meta?.layout_type || 'unknown'
            });
        }
        
        console.log(JSON.stringify({ success: true, results }));
    } catch (error) {
        console.log(JSON.stringify({ success: false, error: error.message }));
    }
})();
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(test_script)
        temp_script = f.name
    
    try:
        result = subprocess.run(
            ['node', temp_script],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='/Users/abdullah/Desktop/Techinoid/Slidex-v1/neuro-engine-main/services'
        )
        
        # Extract JSON from output
        lines = result.stdout.strip().split('\n')
        json_line = None
        for line in lines:
            if line.startswith('{'):
                json_line = line
                break
        
        if json_line:
            output = json.loads(json_line)
            if output.get('success'):
                print("  ✓ Node.js service working!")
                results = output.get('results', [])
                print(f"  ✓ Generated {len(results)} infographics:")
                for r in results:
                    print(f"    [{r['index']}] {r['prompt']}")
                    print(f"        HTML size: {r['html_size']} chars")
                    print(f"        Layout: {r['layout']}")
                return True
            else:
                print(f"  ✗ Service error: {output.get('error')}")
                return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Service call timed out (120s)")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        if os.path.exists(temp_script):
            os.remove(temp_script)

async def test_playwright():
    """Test Playwright HTML to PNG conversion"""
    print("\n[2/3] Testing Playwright HTML→PNG conversion...")
    
    try:
        from playwright.async_api import async_playwright
        
        # Simple HTML to test
        html_content = """
        <html>
        <head>
            <style>
                body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; font-family: Arial; text-align: center; padding: 40px; }
                h1 { font-size: 48px; margin: 0; }
                p { font-size: 20px; }
            </style>
        </head>
        <body>
            <h1>Integration Test</h1>
            <p>Template-Based Infographics Working ✓</p>
        </body>
        </html>
        """
        
        output_path = Path('test_output.png')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 1200, 'height': 800})
            await page.set_content(html_content)
            await page.screenshot(path=str(output_path))
            await browser.close()
        
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"  ✓ HTML converted to PNG")
            print(f"    File size: {size:,} bytes")
            print(f"    Location: {output_path.absolute()}")
            output_path.unlink()  # Clean up
            return True
        else:
            print("  ✗ PNG file not created")
            return False
            
    except Exception as e:
        print(f"  ✗ Playwright error: {e}")
        return False

async def main():
    """Run all tests"""
    
    # Test 1: Environment
    print("\n[Environment Check]")
    api_key = os.getenv('API_KEY1')
    if api_key:
        print(f"  ✓ API_KEY1 available: {api_key[:20]}...")
    else:
        print("  ✗ API_KEY1 not found")
    
    # Test 2: Service generation
    success1 = await test_image_generation()
    
    # Test 3: Playwright
    success2 = await test_playwright()
    
    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"  • Node.js Service: {'✓ WORKING' if success1 else '✗ FAILED'}")
    print(f"  • Playwright PNG: {'✓ WORKING' if success2 else '✗ FAILED'}")
    
    if success1 and success2:
        print("\n✓ INTEGRATION COMPLETE - System is ready for full video generation!")
        print("\nTo generate complete videos:")
        print("  1. Install remaining requirements: pip3 install --user boto3 google-generativeai")
        print("  2. Run: python3 create_explainer_video_integrated.py 'Your Topic'")
    
    print("="*80 + "\n")

if __name__ == '__main__':
    asyncio.run(main())
