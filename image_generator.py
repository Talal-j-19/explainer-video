import os
import json
import requests
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright

class ImageGenerator:
    API_URL = "https://dev.slidexy.net/api/infographic"

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else Path("video_segments")
        self.output_dir.mkdir(exist_ok=True)

    async def render_html_to_png(self, html_content, output_path):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(html_content, wait_until="networkidle")

            # Target main infographic wrapper
            element = await page.query_selector("body > div:first-of-type")
            if not element:
                raise ValueError("❌ No infographic element found in HTML")

            # Optional: enforce square corners
            await page.add_style_tag(content="body > div:first-of-type { border-radius: 0 !important; }")

            await element.screenshot(path=str(output_path))
            await browser.close()

    async def generate_images_for_script(self, script_path):
        print("🎨 GENERATING INFOGRAPHIC IMAGES")
        print("=" * 40)

        with open(script_path, 'r', encoding='utf-8') as f:
            script = json.load(f)

        segments = script.get('segments', [])
        success_count = 0

        for segment in segments:
            segment_num = segment['segment_number']
            title = segment['title']

            print(f"\n Generating infographic for Segment {segment_num}: {title}")

            image_prompt = segment.get('image_prompt', '')
            print(f"📝 Using prompt: {image_prompt[:100]}...")

            output_path = self.output_dir / f"segment_{segment_num:02d}_background.png"

            try:
                response = requests.post(
                    self.API_URL,
                    json={"prompt": image_prompt, "useReferences": True},
                    timeout=60
                )
                print(f"📡 API Status: {response.status_code}")
                print(f"📄 API Raw Response: {response.text[:500]}...")
                response.raise_for_status()

                data = response.json()
                if not data.get("success") or "infographic" not in data:
                    raise ValueError(f"Unexpected API response: {data}")

                html_content = data["infographic"]["html"]

                # Save raw HTML
                html_path = self.output_dir / f"segment_{segment_num:02d}_background.html"
                with open(html_path, "w", encoding="utf-8") as f_html:
                    f_html.write(html_content)
                print(f"💾 Saved raw HTML → {html_path}")

                # Render PNG
                await self.render_html_to_png(html_content, output_path)

                # Save path into segment
                segment['background_image'] = str(output_path)
                success_count += 1
                print(f"✅ Saved infographic image → {output_path}")

            except Exception as e:
                print(f"❌ Failed to generate infographic for segment {segment_num}: {e}")

        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Generated {success_count}/{len(segments)} background images")
        print(f"📁 Images saved in: {self.output_dir}")

        return success_count == len(segments)


def main():
    import argparse
    import sys
    
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    parser = argparse.ArgumentParser(description='Generate background images for video explainer')
    parser.add_argument('script_path', help='Path to video script JSON file')
    args = parser.parse_args()

    if not Path(args.script_path).exists():
        print(f"❌ Script file not found: {args.script_path}")
        return

    generator = ImageGenerator()
    asyncio.run(generator.generate_images_for_script(args.script_path))
    print("\n🎉 Image generation complete!")


if __name__ == '__main__':
    main()
    
