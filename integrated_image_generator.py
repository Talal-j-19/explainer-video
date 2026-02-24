#!/usr/bin/env python3
"""
Integrated Image Generator for Explainer Videos
Uses the new template-based infographic system via HTTP API for optimal performance.

Architecture:
  Script Segment → Image Prompt → HTTP API → HTML → Playwright → PNG
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import requests
import time


# Load environment variables from main directory
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠️ .env file not found at {env_path}")


class IntegratedImageGenerator:
    """
    Generate infographic images using the template-based V2 system via HTTP API
    """
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://172.18.160.1:5000")
    INFOGRAPHIC_ENDPOINT = "/api/explainer-infographic"
    
    def __init__(self, output_dir: Optional[str] = None, use_content_only: bool = False):
        """
        Initialize the integrated image generator
        
        Args:
            output_dir: Directory to save generated images
            use_content_only: Legacy parameter, ignored
        """
        self.output_dir = Path(output_dir) if output_dir else Path("video_segments")
        self.output_dir.mkdir(exist_ok=True)
        
        self.api_url = f"{self.API_BASE_URL}{self.INFOGRAPHIC_ENDPOINT}"
        
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🔗 API endpoint: {self.api_url}")
    
    def generate_infographic_via_service(
        self, 
        prompt: str,
        slide_type: str,
        view_mode: str = "landscape",
        preferred_layout: Optional[str] = None,
        color_scheme: Optional[str] = None,
        title: Optional[str] = None,
        text_overlay: Optional[str] = None,
        narration: Optional[str] = None,
        key_points: Optional[any] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate infographic using the HTTP API
        
        Args:
            prompt: Topic/text for infographic generation
            view_mode: 'landscape' or 'portrait'
            preferred_layout: Optional preferred layout type
            color_scheme: Optional color scheme name (e.g., 'techBlue', 'forestGreen')
            title: Optional title text from the script segment
            text_overlay: Optional text overlay from the script segment
            narration: Optional narration text from the script segment
        """
        if preferred_layout:
            # Add layout hint to prompt
            layout_hints = {
                'cards': 'Present as individual cards with key points and visual elements',
                'timeline': 'Show chronologically as a timeline with events or sequential steps',
                'comparison': 'Present as a side-by-side comparison showing contrasts or alternatives',
                'list': 'Organize as a structured list with numbered or bulleted key points',
                'process-flow': 'Visualize as a step-by-step process flow with arrows and stages',
                'chart': 'Represent with charts, graphs, or data visualization elements',
                'hierarchy': 'Structure as a hierarchical diagram showing levels or relationships'
            }
            hint = layout_hints.get(preferred_layout, '')
            if hint:
                prompt = f"{prompt}. {hint}"
        
        try:
            # Prepare request payload
            payload = {
                "topic": prompt,
                "viewMode": view_mode,
                "slideType": slide_type,
            }
            
            # Add optional fields if provided
            if preferred_layout:
                payload["preferredLayout"] = preferred_layout
            if color_scheme:
                payload["colorScheme"] = color_scheme
            if title:
                payload["title"] = title
            if text_overlay:
                payload["textOverlay"] = text_overlay
            if narration:
                payload["narration"] = narration
            if key_points:
                payload["keyPoints"] = key_points

            # 🔹 Print payload before sending
            print("📤 Payload being sent to API:")
            for k, v in payload.items():
                print(f"  {k}: {v}")
            
            print(f"   🌐 Making API request to {self.api_url}")
            if color_scheme:
                print(f"   🎨 Using color scheme: {color_scheme}")
            
            # Make HTTP POST request to the API
            response = requests.post(
                self.api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ API request successful")
                    return {
                        'success': True,
                        'html': result.get('html', ''),
                        'data': result.get('data', {}),
                        'meta': result.get('meta', {})
                    }
                else:
                    print(f"   ❌ API error: {result.get('error')}")
                    return None
            else:
                print(f"   ❌ HTTP Error {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection error: Cannot reach {self.api_url}")
            return None
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout: API took too long to respond")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    async def render_html_to_png(self, html_content: str, output_path: str) -> bool:
        """
        Render HTML content to PNG using Playwright
        
        Args:
            html_content: HTML content to render
            output_path: Path to save PNG
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    viewport={"width": 1200, "height": 600}
                )
                
                await page.set_content(html_content, wait_until="networkidle")
                
                # Target the infographic content
                element = await page.query_selector("body > div:first-of-type")
                
                if not element:
                    print("⚠️ No infographic element found, using full page")
                    await page.screenshot(path=str(output_path), full_page=False)
                else:
                    await element.screenshot(path=str(output_path))
                
                await browser.close()
                print(f"✅ PNG rendered: {output_path}")
                return True
                
        except Exception as e:
            print(f"❌ Rendering failed: {e}")
            return False
    
    def _get_topic_gradient(self, topic_or_scheme: str) -> tuple:
        """
        Get gradient colors based on topic keywords or scheme name.

        Args:
            topic_or_scheme (str): Either a topic string (e.g., "AI and tech") 
                                or a scheme name (e.g., "techBlue").

        Returns:
            tuple: (gradient_colors, accent_color)
        """
        # Color schemes with gradients (primary1, primary2, accent)
        color_schemes = {
            'techBlue': (['#caf0f8', '#90e0ef'], '#0077b6'),
            'forestGreen': (['#d8f3dc', '#b7e4c7'], '#2d6a4f'),
            'culinaryRed': (['#ffe5e5', '#ffcccc'], '#e63946'),
            'creativeViolet': (['#f3e5f5', '#e1bee7'], '#8e24aa'),
            'travelTeal': (['#e0f7fa', '#b2ebf2'], '#00acc1'),
            'academicYellow': (['#fff9e6', '#fff3cc'], '#f4a259'),
            'scienceBlue': (['#e8eaf6', '#c5cae9'], '#3f51b5'),
            'corporateGold': (['#fff4e6', '#ffe8cc'], '#e67700'),
            'medicalBlue': (['#e0f4ff', '#c6e7ff'], '#0096c7'),
        }

        # If the input is a valid scheme name, return directly
        if topic_or_scheme in color_schemes:
            return color_schemes[topic_or_scheme]

        # Semantic groups for topic matching (ordered by specificity)
        semanticGroups = {
            'medicalBlue': ['health', 'medical', 'medicine', 'hospital', 'doctor', 'healthcare', 'wellness', 'disease', 'treatment', 'patient', 'clinical', 'nurse', 'pharmacy'],
            'culinaryRed': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef', 'culinary', 'baking', 'kitchen', 'dish', 'meal', 'appetizer', 'dessert'],
            'creativeViolet': ['art', 'design', 'music', 'artist', 'illustration', 'culture', 'painting', 'graphic', 'creative', 'visual', 'photography', 'cinema', 'film', 'animation', 'drawing'],
            'techBlue': ['technology', 'tech', 'computer', 'programming', 'software', 'ai', 'artificial', 'intelligence', 'digital', 'coding', 'development', 'web', 'algorithm', 'data', 'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'machine learning', 'deep learning', 'automation', 'neural'],
            'forestGreen': ['nature', 'environment', 'green', 'eco', 'plant', 'forest', 'sustainability', 'earth', 'climate', 'renewable', 'energy', 'solar', 'wind', 'organic', 'ecological', 'conservation'],
            'travelTeal': ['travel', 'adventure', 'tourism', 'vacation', 'journey', 'explore', 'destination', 'trip', 'tour', 'excursion', 'wanderlust', 'backpack'],
            'academicYellow': ['education', 'school', 'university', 'student', 'academic', 'course', 'teaching', 'tutorial', 'training', 'college', 'study', 'classroom'],
            'scienceBlue': ['science', 'physics', 'chemistry', 'biology', 'laboratory', 'experiment', 'quantum', 'genetic', 'discovery', 'scientific'],
            'corporateGold': ['business', 'corporate', 'company', 'finance', 'money', 'banking', 'market', 'investment', 'entrepreneur', 'startup', 'sales', 'commerce', 'enterprise'],
        }

        lower_topic = topic_or_scheme.lower()

        # Match topic to scheme
        for scheme, keywords in semanticGroups.items():
            if any(keyword in lower_topic for keyword in keywords):
                return color_schemes[scheme]

        # Default to techBlue
        return color_schemes['techBlue']

    async def generate_opening_page(self, topic: str,color_scheme: str, output_dir: Optional[str] = None) -> Optional[str]:
        """Generate a professional opening page using the exact template design with topic-based gradient"""
        output_dir = Path(output_dir) if output_dir else self.output_dir
        
        print(f"\n🎬 GENERATING OPENING PAGE")
        print(f"{'='*60}")
        
        # Get gradient colors based on topic
        gradient_colors, accent_color = self._get_topic_gradient(color_scheme)
        gradient_start = gradient_colors[0]
        gradient_end = gradient_colors[1]
        
        print(f"   🎨 Using gradient: {gradient_start} → {gradient_end} (accent: {accent_color})")
        
        opening_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Explainer Thumbnail</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        /* --- Reset --- */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #111;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}

        /* --- Main Thumbnail Container (16:9 Aspect Ratio) --- */
        .thumbnail-container {{
            width: 90vw;
            max-width: 1280px;
            aspect-ratio: 16 / 9;
            background: #0f172a; /* Deep Slate Background */
            position: relative;
            overflow: hidden;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            padding: 0 8%;
        }}

        /* --- Animated Background Blobs --- */
        .blob {{
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.6;
            animation: float 10s infinite ease-in-out alternate;
        }}
        .blob-1 {{ top: -10%; right: -10%; width: 600px; height: 600px; background: {gradient_start}; animation-delay: 0s; }}
        .blob-2 {{ bottom: -20%; left: -10%; width: 500px; height: 500px; background: {gradient_end}; animation-delay: 2s; }}
        .blob-3 {{ top: 40%; right: 30%; width: 300px; height: 300px; background: {accent_color}; animation-delay: 4s; }}

        /* --- Grid Overlay for Texture --- */
        .grid-overlay {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 1;
        }}

        /* --- Content Wrapper (Glassmorphism) --- */
        .content-wrapper {{
            position: relative;
            z-index: 10;
            max-width: 65%;
            backdrop-filter: blur(10px); /* Subtle blur behind text */
        }}

        /* --- Tags / Badges --- */
        .badge-container {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }}
        .badge {{
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .badge-highlight {{
            background: linear-gradient(135deg, #4f46e5, #ec4899);
            border: none;
        }}

        /* --- Typography --- */
        h1 {{
            font-family: 'Playfair Display', serif; /* Elegant Serif for Contrast */
            font-size: clamp(3rem, 5vw, 5rem);
            line-height: 1.1;
            color: #fff;
            margin-bottom: 20px;
            text-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        h1 span {{
            background: linear-gradient(to right, {accent_color}, {gradient_end});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-style: italic;
        }}

        p.subtitle {{
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 300;
            line-height: 1.6;
            margin-bottom: 40px;
            border-left: 4px solid {accent_color};
            padding-left: 20px;
        }}

        /* --- Play Button --- */
        .play-btn-wrapper {{
            display: none;
        }}

        .play-btn {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            backdrop-filter: blur(5px);
        }}

        .play-btn i {{
            color: #fff;
            font-size: 30px;
            margin-left: 5px; /* Visual centering fix */
        }}

        /* Pulse Animation */
        .play-btn::before, .play-btn::after {{
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.5);
            width: 100%; height: 100%;
            animation: pulse 2s infinite;
        }}
        .play-btn::after {{ animation-delay: 0.5s; }}

        .watch-text {{
            color: #fff;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-weight: 600;
            opacity: 0.8;
        }}

        /* --- Animations --- */
        @keyframes float {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(30px, 50px); }}
        }}

        @keyframes pulse {{
            0% {{ width: 100%; height: 100%; opacity: 1; }}
            100% {{ width: 180%; height: 180%; opacity: 0; }}
        }}

    </style>
</head>
<body>

    <div class="thumbnail-container">
        
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
        <div class="grid-overlay"></div>

        <div class="content-wrapper">
            <div class="badge-container">
                <div class="badge">
                    <i class="far fa-circle-play"></i> Educational Content
                </div>
            </div>

            <h1>Master the Essentials of <br><span>{topic}</span></h1>
            
            <p class="subtitle">
                Join us on an educational journey. Discover comprehensive insights, learn practical strategies, and transform your understanding with this expertly crafted video guide.
            </p>
        </div>

    </div>

</body>
</html>"""
        
        html_path = output_dir / "opening_page.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(opening_html)
        print(f"✅ Opening page HTML created")
        
        png_path = output_dir / "opening_page.png"
        success = await self.render_html_to_png(opening_html, str(png_path))
        
        if success:
            print(f"✅ Opening page rendered: {png_path}")
            return str(png_path)
        else:
            print(f"❌ Failed to render opening page")
            return None
    
    async def generate_closing_page_with_summary(self, topic: str,color_scheme: str, output_dir: Optional[str] = None, video_segments: list = None) -> Optional[str]:
        """Generate a professional closing page with summary infographic (new b.html design)"""
        output_dir = Path(output_dir) if output_dir else self.output_dir
        
        print(f"\n🎬 GENERATING CLOSING PAGE WITH SUMMARY")
        print(f"{'='*60}")
        
        # Get gradient colors matching opening page
        gradient_colors, accent_color = self._get_topic_gradient(color_scheme)
        gradient_start = gradient_colors[0]
        gradient_end = gradient_colors[1]
        
        print(f"   🎨 Using gradient: {gradient_start} → {gradient_end} (accent: {accent_color})")
        
        # Generate summary infographic based on video content
        print(f"   📝 Generating key takeaways text...")
        
        # Extract key points from video segments for takeaways
        key_takeaways = []
        if video_segments:
            # Get titles from segments (skip opening/closing)
            key_takeaways = [seg.get('title', '') for seg in video_segments[1:-1] if seg.get('title')][:8]
        
        # Create formatted takeaways list
        takeaways_html = ""
        if key_takeaways:
            for idx, takeaway in enumerate(key_takeaways, 1):
                takeaways_html += f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 18px;">
                    <div style="min-width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, {gradient_start}, {accent_color}); display: flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: 700; color: #0f172a; font-size: 14px;">{idx}</div>
                    <div style="color: rgba(255,255,255,0.95); font-size: 16px; line-height: 1.6; flex: 1;">{takeaway}</div>
                </div>
                """
        else:
            # Fallback takeaways
            for idx, text in enumerate([
                f"Understanding core concepts of {topic}",
                "Key principles and fundamentals",
                "Practical applications and use cases",
                "Best practices and methodologies"
            ], 1):
                takeaways_html += f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 18px;">
                    <div style="min-width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, {gradient_start}, {accent_color}); display: flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: 700; color: #0f172a; font-size: 14px;">{idx}</div>
                    <div style="color: rgba(255,255,255,0.95); font-size: 16px; line-height: 1.6; flex: 1;">{text}</div>
                </div>
                """
        
        summary_content = f"""
        <div style="background: rgba(255,255,255,0.08); padding: 40px 35px; border-radius: 20px; border: 2px solid rgba(255,255,255,0.15); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); height: 100%;">
            <div style="display: flex; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid rgba(255,255,255,0.1);">
                <div style="width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, {gradient_start}, {accent_color}); display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                    <i class="fas fa-lightbulb" style="color: #0f172a; font-size: 24px;"></i>
                </div>
                <h3 style="color: white; font-size: 28px; margin: 0; font-weight: 700;">Key Takeaways</h3>
            </div>
            <div style="max-height: 400px; overflow-y: auto;">
                {takeaways_html}
            </div>
        </div>
        """
        print(f"   ✅ Key takeaways generated")
        
        closing_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Explainer Outro</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #111;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}

        .thumbnail-container {{
            width: 90vw;
            max-width: 1280px;
            aspect-ratio: 16 / 9;
            background: #0f172a;
            position: relative;
            overflow: hidden;
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 6%;
        }}

        .blob {{
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.5;
            animation: float 12s infinite ease-in-out alternate;
        }}
        .blob-1 {{ top: -10%; left: -10%; width: 600px; height: 600px; background: {gradient_start}; }}
        .blob-2 {{ bottom: -20%; right: -10%; width: 500px; height: 500px; background: {gradient_end}; animation-delay: 2s; }}
        
        .grid-overlay {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 1;
        }}

        .outro-layout {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            width: 100%;
            z-index: 10;
            align-items: center;
        }}

        .cta-section h1 {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(2.5rem, 4vw, 4rem);
            line-height: 1.1;
            color: #fff;
            margin-bottom: 15px;
        }}

        .cta-section h1 span {{
            background: linear-gradient(to right, {accent_color}, {gradient_end});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-style: italic;
        }}

        .cta-text {{
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1rem;
            font-weight: 300;
            margin-bottom: 40px;
            max-width: 400px;
        }}

        .subscribe-card {{
            display: flex;
            align-items: center;
            gap: 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px 25px;
            border-radius: 100px;
            width: fit-content;
            backdrop-filter: blur(10px);
        }}

        .channel-logo {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, {gradient_start}, {gradient_end});
            display: flex;
            justify-content: center;
            align-items: center;
            color: #fff;
            font-size: 20px;
        }}

        .sub-btn {{
            background: linear-gradient(135deg, {gradient_start}, {accent_color});
            color: #fff;
            border: none;
            padding: 10px 25px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .sub-btn:hover {{ transform: scale(1.05); }}

        .summary-section {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
            height: 100%;
        }}

        .summary-content {{
            width: 100%;
            max-width: 550px;
        }}
        
        /* Scrollbar styling for takeaways */
        .summary-content div::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .summary-content div::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }}
        
        .summary-content div::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, {gradient_start}, {accent_color});
            border-radius: 10px;
        }}

        @keyframes float {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(30px, 50px); }}
        }}
    </style>
</head>
<body>
    <div class="thumbnail-container">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="grid-overlay"></div>

        <div class="outro-layout">
            <div class="cta-section">
                <h1>Thanks for <br><span>Watching.</span></h1>
            </div>

            <div class="summary-section">
                <div class="summary-content">
                    {summary_content}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        html_path = output_dir / "closing_page_new.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(closing_html)
        print(f"✅ Closing page HTML created")
        
        png_path = output_dir / "closing_page.png"
        success = await self.render_html_to_png(closing_html, str(png_path))
        
        if success:
            print(f"✅ Closing page rendered: {png_path}")
            return str(png_path)
        else:
            print(f"❌ Failed to render closing page")
            return None
    
    def _get_color_scheme_name_from_gradient(self, gradient_color: str) -> str:
        """Map gradient color to color scheme name"""
        color_map = {
            '#d8f3dc': 'forestGreen',
            '#caf0f8': 'techBlue',
            '#ffc6c4': 'culinaryRed',
            '#e0aaff': 'creativeViolet',
            '#a8dadc': 'travelTeal',
            '#ffe8a3': 'academicYellow',
            '#d4e09b': 'scienceBlue',
            '#ffd89b': 'corporateGold',
            '#cfe2f3': 'medicalBlue'
        }
        return color_map.get(gradient_color, 'techBlue')
    
    async def generate_images_for_script(
        self, 
        script_path: str, 
        topic: str = None, 
        color_scheme: str = None,
        tts_processor = None,
        job_dir: Path = None
    ) -> bool:
        """
        Generate infographic images for all segments in a script
        
        Args:
            script_path: Path to video script JSON
            topic: Topic for consistent color scheme (optional)
            color_scheme: Override color scheme (optional)
            tts_processor: Optional TTS processor to generate audio in parallel
            job_dir: Optional job directory for audio output
            
        Returns:
            True if all successful, False otherwise
        """
        print("\n🎨 GENERATING INFOGRAPHIC IMAGES (Template-Based V2)")
        print("=" * 60)
        
        if tts_processor:
            print("🎙️ Staggered Audio Generation enabled: Audio will be generated as images complete.")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load script: {e}")
            return False
        
        segments = script.get('segments', [])
        if not segments:
            print("❌ No segments found in script")
            return False
        
        # Determine consistent color scheme based on topic or override
        if color_scheme:
            consistent_color_scheme = color_scheme
        elif topic:
            gradient_colors, _ = self._get_topic_gradient(topic)
            consistent_color_scheme = self._get_color_scheme_name_from_gradient(gradient_colors[0])
        else:
            # Fallback if topic not provided
            consistent_color_scheme = 'techBlue'
        
        # Define layout types for variety (but keep color consistent)
        layout_rotation = ['cards', 'process-flow', 'comparison', 'timeline', 'list', 'hierarchy', 'chart']
        
        print(f"🎨 Using consistent color scheme across all {len(segments)} segments for visual coherence")
        print(f"   🎨 Color Scheme: {consistent_color_scheme} (matches opening/closing pages)")
        print(f"   📐 Layout rotation: {' → '.join(layout_rotation[:min(len(segments), len(layout_rotation))])}")
        
        # Parallel processing configuration - OPTIMIZED
        max_concurrent = 10  # Process up to 10 segments simultaneously (2x improvement)
        tasks_data = []
        used_layouts = []
        
        # Pre-calculate all task data to minimize lock time
        print(f"   📊 Preparing {len(segments)} tasks for parallel execution...")
        
        for idx, segment in enumerate(segments):
            segment_num = segment.get('segment_number', idx)
            title = segment.get('title', f"Segment {segment_num}")
            slide_type = segment.get('slide_type', '')
    
            # Skip title/summary slides for image generation, but we might still want audio
            if slide_type in ('title', 'summary'):
                if tts_processor and job_dir:
                    # Special case: process audio only for these segments
                    tasks_data.append({
                        'segment': segment,
                        'segment_num': segment_num,
                        'audio_only': True,
                        'title': title
                    })
                    print(f"🎙️ [{segment_num:02d}] Added to audio queue ({slide_type})")
                else:
                    print(f"⏭ Skipping segment {segment_num} ({slide_type})")
                continue

            image_prompt = segment.get('image_prompt', '')
            slide_type = segment.get('slide_type','')
            text_overlay = segment.get('text_overlay', '')  # Extract new field
            narration = segment.get('narration_text', '')
            key_points = segment.get('key_points','')  # Extract new field
            
            # Rotate through different layout types but keep color consistent
            preferred_layout = layout_rotation[idx % len(layout_rotation)]
            preferred_color = consistent_color_scheme  # Same color for all segments
            used_layouts.append(preferred_layout)
            
            if not image_prompt:
                continue
            
            # Prepare task data for parallel processing
            tasks_data.append({
                'segment': segment,
                'segment_num': segment_num,
                'title': title,
                'slide_type' : slide_type,
                'image_prompt': image_prompt,
                'preferred_layout': preferred_layout,
                'preferred_color': consistent_color_scheme,  # Consistent color
                'text_overlay': text_overlay,  # Add new field
                'narration_text': narration, 
                'key_points': key_points, # Add new field
                'idx': idx
            })
        
        # Process segments in parallel batches
        print(f"\n🚀 Processing {len(tasks_data)} segments in parallel (max {max_concurrent} concurrent)...\n")
        
        async def process_segment(task_data):
            """Process a single segment: API call + PNG rendering"""
            segment = task_data['segment']
            segment_num = task_data['segment_num']
            title = task_data['title']
            
            # Handle audio-only segments (title/summary slides)
            if task_data.get('audio_only'):
                if tts_processor and job_dir:
                    narration_data = {
                        'segment_number': segment_num,
                        'clean_text': segment.get('narration_text', ''),
                        'output_audio': str(job_dir / "audio" / f"segment_{segment_num:02d}_audio.wav")
                    }
                    (job_dir / "audio").mkdir(exist_ok=True)
                    print(f"🎙️ [{segment_num:02d}] Audio-only segment: {title}")
                    await asyncio.to_thread(
                        tts_processor.generate_audio_for_segment, 
                        narration_data, 
                        tts_service='custom_api'
                    )
                return True

            slide_type = task_data['slide_type']
            image_prompt = task_data['image_prompt']
            preferred_layout = task_data['preferred_layout']
            preferred_color = task_data['preferred_color']
            text_overlay = task_data.get('text_overlay')  # Extract new field
            narration = task_data.get('narration_text')  # Extract new field
            key_points = task_data.get('key_points')
            
            print(f"📍 [{segment_num:02d}] {title} | {preferred_layout} | {preferred_color}")
            
            try:
                start_time = time.time()
                
                # Generate infographic via HTTP API (non-blocking)
                result = self.generate_infographic_via_service(
                    image_prompt, 
                    preferred_layout=preferred_layout,
                    color_scheme=preferred_color,
                    slide_type=slide_type,
                    title=title,  # Pass new field
                    text_overlay=text_overlay,  
                    narration=narration,
                    key_points=key_points
                )
                
                if not result or not result.get('success'):
                    print(f"   ❌ [{segment_num:02d}] Service failed")
                    return False
                
                html_content = result.get('html', '')
                if not html_content:
                    print(f"   ❌ [{segment_num:02d}] No HTML returned")
                    return False
                
                # Render to PNG (async)
                png_path = self.output_dir / f"segment_{segment_num:02d}_background.png"
                png_success = await self.render_html_to_png(html_content, str(png_path))
                
                if png_success:
                    segment['background_image'] = str(png_path)
                    elapsed = time.time() - start_time
                    print(f"   ✅ [{segment_num:02d}] Complete in {elapsed:.1f}s")
                    
                    # Generate audio for this segment immediately (Staggered Load)
                    if tts_processor and job_dir:
                        narration_file = job_dir / f"segment_{segment_num:02d}_narration.txt"
                        if narration_file.exists():
                            # Prepare narration data structure for the processor
                            narration_data = {
                                'segment_number': segment_num,
                                'clean_text': segment.get('narration_text', ''),
                                'output_audio': str(job_dir / "audio" / f"segment_{segment_num:02d}_audio.wav")
                            }
                            # Ensure audio dir exists
                            (job_dir / "audio").mkdir(exist_ok=True)
                            
                            print(f"   🎙️ [{segment_num:02d}] Triggering audio generation...")
                            # Run synchronous audio gen in a thread to not block image parallelization
                            await asyncio.to_thread(
                                tts_processor.generate_audio_for_segment, 
                                narration_data, 
                                tts_service='custom_api'
                            )
                    
                    return True
                else:
                    print(f"   ❌ [{segment_num:02d}] PNG rendering failed")
                    return False
                    
            except Exception as e:
                print(f"   ❌ [{segment_num:02d}] Error: {e}")
                return False
        
        # Process all segments with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_process(task_data):
            async with semaphore:
                return await process_segment(task_data)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*[bounded_process(task) for task in tasks_data], return_exceptions=True)
        
        # Count successes
        success_count = sum(1 for r in results if r is True)
        
        # Save updated script
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2, ensure_ascii=False)
            print(f"\n📝 Updated script: {script_path}")
        except Exception as e:
            print(f"⚠️ Failed to save script: {e}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 SUMMARY: Generated {success_count}/{len(segments)} images")
        
        # Show layout variety
        from collections import Counter
        layout_counts = Counter(used_layouts)
        unique_layouts = len(layout_counts)
        
        print(f"🎨 Visual summary:")
        print(f"   📐 Layouts: {unique_layouts} different types - {', '.join([f'{layout}({count})' for layout, count in layout_counts.items()])}")
        print(f"   🌈 Color Scheme: {consistent_color_scheme} (consistent across all segments)")
        
        print(f"📁 Output: {self.output_dir}")
        
        return success_count == len(segments)

async def main():
    """Command line interface"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description='Generate infographic images using template-based V2 system'
    )
    parser.add_argument('script_path', help='Path to video script JSON')
    parser.add_argument(
        '--output-dir',
        default='video_segments',
        help='Output directory for generated images'
    )
    
    args = parser.parse_args()
    
    if not Path(args.script_path).exists():
        print(f"❌ Script not found: {args.script_path}")
        sys.exit(1)
    
    generator = IntegratedImageGenerator(
        output_dir=args.output_dir
    )
    
    success = await generator.generate_images_for_script(args.script_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
