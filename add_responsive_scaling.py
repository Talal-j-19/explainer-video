#!/usr/bin/env python3
"""
Add responsive scaling to D3.js infographics to prevent viewport issues
Simple, focused solution that doesn't interfere with the main flow
"""

import re
from pathlib import Path


def add_responsive_scaling(html_file_path):
    """
    Add responsive scaling to ensure infographic fits on screen.
    Only adds viewport meta tag and responsive CSS - no complex scripts.
    """
    html_path = Path(html_file_path)
    
    if not html_path.exists():
        print(f"❌ HTML file {html_path} not found")
        return False
    
    try:
        # Read the HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already responsive
        if 'viewport' in content and 'max-width: 100%' in content:
            print("✅ Infographic is already responsive")
            return True
        
        # Add viewport meta tag if not present
        if 'viewport' not in content:
            if '<head>' in content:
                content = content.replace(
                    '<head>',
                    '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                )
            elif '<meta charset=' in content:
                # Insert after charset meta tag
                content = re.sub(
                    r'(<meta charset="[^"]*">)',
                    r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                    content
                )
        
        # Add responsive CSS styles
        responsive_css = """
        /* Responsive infographic styles */
        body { 
            margin: 0; 
            padding: 20px; 
            box-sizing: border-box;
            background-color: #f5f5f5;
            overflow-x: auto;
        }
        svg { 
            max-width: 100%; 
            max-height: 90vh; 
            display: block; 
            margin: 0 auto; 
            background-color: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        /* Ensure SVG maintains aspect ratio */
        svg[viewBox] {
            width: auto;
            height: auto;
        }"""
        
        # Add the CSS to existing style section or create new one
        if '</style>' in content:
            content = content.replace('</style>', responsive_css + '\n    </style>')
        elif '<head>' in content:
            # Add new style section
            style_section = f'    <style>{responsive_css}\n    </style>\n'
            content = content.replace('</head>', style_section + '</head>')
        else:
            # Fallback: add style section before body
            style_section = f'<style>{responsive_css}\n</style>\n'
            content = style_section + content
        
        # Add simple JavaScript to ensure proper scaling after D3 renders
        responsive_js = """
        // Simple responsive scaling for D3.js infographics
        function ensureResponsiveDisplay() {
            const svg = document.querySelector('svg');
            if (!svg) return;
            
            // Get original dimensions
            const width = svg.getAttribute('width') || svg.viewBox?.baseVal?.width || 800;
            const height = svg.getAttribute('height') || svg.viewBox?.baseVal?.height || 600;
            
            // Set viewBox if not already set
            if (!svg.getAttribute('viewBox')) {
                svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
            }
            
            // Ensure preserveAspectRatio for proper scaling
            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            
            // Remove fixed width/height to allow CSS to control sizing
            svg.removeAttribute('width');
            svg.removeAttribute('height');
            
            console.log('✅ Responsive scaling applied');
        }
        
        // Apply responsive scaling after DOM loads and D3 renders
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(ensureResponsiveDisplay, 500);
            });
        } else {
            setTimeout(ensureResponsiveDisplay, 500);
        }"""
        
        # Add the JavaScript before closing body tag
        if '</body>' in content:
            script_section = f'    <script>\n        {responsive_js}\n    </script>\n'
            content = content.replace('</body>', script_section + '</body>')
        elif '</html>' in content:
            # Fallback: add before closing html tag
            script_section = f'<script>\n{responsive_js}\n</script>\n'
            content = content.replace('</html>', script_section + '</html>')
        
        # Write the updated content
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Added responsive scaling to {html_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding responsive scaling: {e}")
        return False


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add responsive scaling to D3.js infographic')
    parser.add_argument('html_file', help='Path to HTML file')
    
    args = parser.parse_args()
    
    success = add_responsive_scaling(args.html_file)
    if not success:
        exit(1)


if __name__ == '__main__':
    main()
