#!/usr/bin/env python3
"""
Standalone Headless Extraction Tool
Extract PNG or SVG from D3.js HTML files using headless browser
"""

import asyncio
import sys
from pathlib import Path


async def headless_png_extract(html_file, output_png):
    """Extract PNG from HTML file using headless browser"""
    from playwright.async_api import async_playwright
    
    print(f"[Headless] Starting PNG extraction from {html_file}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            # Navigate to HTML file
            file_url = f"file://{Path(html_file).absolute()}"
            await page.goto(file_url, wait_until='networkidle', timeout=30000)
            
            # Wait for D3.js and SVG rendering
            await page.wait_for_timeout(3000)
            
            # Check D3.js availability
            d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            if not d3_available:
                await page.wait_for_timeout(5000)
                d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            
            if not d3_available:
                print("[Headless] ERROR: D3.js failed to load")
                return False
            
            # Wait for SVG
            await page.wait_for_selector('svg', timeout=15000)
            await page.wait_for_timeout(2000)
            
            # Get SVG element for screenshot
            svg_element = await page.query_selector('svg')
            if not svg_element:
                print("[Headless] ERROR: No SVG element found")
                return False
            
            # Take screenshot of the SVG element
            await svg_element.screenshot(path=output_png, type='png')
            
            file_size = Path(output_png).stat().st_size
            print(f"[Headless] SUCCESS: PNG saved to {output_png} ({file_size} bytes)")
            
            return True
            
        except Exception as e:
            print(f"[Headless] ERROR: {e}")
            return False
            
        finally:
            await browser.close()


async def headless_svg_extract(html_file, output_svg):
    """Extract SVG from HTML file using headless browser"""
    from playwright.async_api import async_playwright
    
    print(f"[Headless] Starting SVG extraction from {html_file}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            # Navigate to HTML file
            file_url = f"file://{Path(html_file).absolute()}"
            await page.goto(file_url, wait_until='networkidle', timeout=30000)
            
            # Wait for D3.js and SVG rendering
            await page.wait_for_timeout(3000)
            
            # Check D3.js availability
            d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            if not d3_available:
                await page.wait_for_timeout(5000)
                d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            
            if not d3_available:
                print("[Headless] ERROR: D3.js failed to load")
                return False
            
            # Wait for SVG
            await page.wait_for_selector('svg', timeout=15000)
            await page.wait_for_timeout(2000)
            
            # Extract SVG content
            svg_content = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return null;
                    return svg.outerHTML;
                }
            """)
            
            if not svg_content:
                print("[Headless] ERROR: Failed to extract SVG")
                return False
            
            # Add XML declaration and namespace
            if not svg_content.startswith('<?xml'):
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content
            
            if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
                svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
            
            # Save SVG file
            with open(output_svg, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            file_size = Path(output_svg).stat().st_size
            print(f"[Headless] SUCCESS: SVG saved to {output_svg} ({file_size} bytes)")
            
            return True
            
        except Exception as e:
            print("[Headless] ERROR: {e}")
            return False
            
        finally:
            await browser.close()


def extract_png(html_file, output_png):
    """Synchronous PNG extraction"""
    return asyncio.run(headless_png_extract(html_file, output_png))


def extract_svg(html_file, output_svg):
    """Synchronous SVG extraction"""
    return asyncio.run(headless_svg_extract(html_file, output_svg))


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract PNG or SVG from D3.js HTML files')
    parser.add_argument('html_file', help='Path to HTML file')
    parser.add_argument('output_file', help='Output file path (.png or .svg)')
    parser.add_argument('--format', choices=['png', 'svg', 'auto'], default='auto',
                       help='Output format (auto-detects from file extension)')
    
    args = parser.parse_args()
    
    # Check Playwright availability
    try:
        import playwright
        print("✅ Playwright available")
    except ImportError:
        print("❌ Playwright not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        print("✅ Playwright installed")
    
    # Determine format
    if args.format == 'auto':
        if args.output_file.lower().endswith('.png'):
            format_type = 'png'
        elif args.output_file.lower().endswith('.svg'):
            format_type = 'svg'
        else:
            print("❌ Cannot auto-detect format. Please specify --format png or --format svg")
            sys.exit(1)
    else:
        format_type = args.format
    
    # Extract file
    if format_type == 'png':
        success = extract_png(args.html_file, args.output_file)
    else:
        success = extract_svg(args.html_file, args.output_file)
    
    if success:
        print(f"🎉 Successfully extracted {format_type.upper()} to {args.output_file}")
        sys.exit(0)
    else:
        print(f"💥 Failed to extract {format_type.upper()}")
        sys.exit(1)


if __name__ == '__main__':
    main()
