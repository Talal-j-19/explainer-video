#!/usr/bin/env python3
"""
Image Generator for Video Explainer
Generates background images for video segments using various AI image generation services
"""

import os
import json
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai


class ImageGenerator:
    """Generate background images for video segments using various AI services"""

    def __init__(self, output_dir=None):
        load_dotenv()
        self.output_dir = Path(output_dir) if output_dir else Path("video_segments")
        self.output_dir.mkdir(exist_ok=True)

        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY2")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            print("⚠️  GOOGLE_API_KEY not found. Gemini image generation will be unavailable.")

    def generate_with_gemini(self, prompt, output_path, width=1920, height=1080):
        """
        Generate image using Gemini's image generation
        Requires GOOGLE_API_KEY environment variable
        """
        api_key = os.getenv("GOOGLE_API_KEY2")
        if not api_key:
            print("❌ GOOGLE_API_KEY2 not found. Skipping Gemini generation.")
            return False

        try:
            print(f"🎨 Attempting Gemini image generation for: {Path(output_path).name}")
            print(f"📝 Prompt: {prompt[:100]}...")

            # Enhanced prompt for better image generation
            enhanced_prompt = f"""
            Create a professional background image for an explainer video.

            Requirements:
            - Aspect ratio: 16:9 ({width}x{height})
            - Style: Clean, modern, professional, educational
            - Colors: Subtle, won't compete with text overlays
            - Composition: Leave space for text overlays
            - Quality: High resolution, crisp details

            Content description: {prompt}

            Visual style: Minimalist, business-appropriate, suitable for educational content.
            """

            # IMPORTANT: As of 2024, Gemini API doesn't directly support image generation
            # Image generation requires either:
            # 1. Vertex AI with Imagen model (requires Google Cloud project setup)
            # 2. Alternative services like Stability AI, DALL-E, etc.

            # Method 1: Try Vertex AI Imagen (if configured)
            try:
                # This requires: pip install google-cloud-aiplatform
                # And proper Google Cloud project setup
                import vertexai
                from vertexai.preview.vision_models import ImageGenerationModel

                # Would need project configuration:
                # vertexai.init(project="your-project-id", location="us-central1")
                # model = ImageGenerationModel.from_pretrained("imagegeneration@002")
                # response = model.generate_images(prompt=enhanced_prompt, number_of_images=1)
                # image = response.images[0]
                # image.save(location=output_path)
                # return True

                print("⚠️  Vertex AI Imagen requires Google Cloud project setup")

            except ImportError:
                print("⚠️  Vertex AI not installed (pip install google-cloud-aiplatform)")
            except Exception as e:
                print(f"⚠️  Vertex AI setup issue: {e}")

            # Method 2: Try Gemini 2.0 Flash Image Generation
            try:
                # Use the correct Gemini 2.0 Flash image generation model
                model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")

                print("🔄 Making Gemini 2.0 Flash image generation request...")

                # Configure generation to request both image and text
                generation_config = {
                    "response_modalities": ["IMAGE", "TEXT"]
                }

                # Generate image using the model with proper configuration
                response = model.generate_content(
                    enhanced_prompt,
                    generation_config=generation_config
                )

                # Check if the response contains image data
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]

                    # Look for image parts in the response
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # Extract image data
                                image_data = part.inline_data.data
                                mime_type = part.inline_data.mime_type

                                print(f"🔍 Found inline data: {mime_type}, {len(image_data)} bytes")

                                # Handle the image data (it's already binary, not base64)
                                try:
                                    # Check if it's already binary data or base64 string
                                    if isinstance(image_data, bytes):
                                        print("✅ Data is already binary")
                                        image_bytes = image_data
                                    else:
                                        print("🔄 Data is string, decoding base64...")
                                        import base64
                                        # Clean and decode base64
                                        clean_data = image_data.replace('\n', '').replace('\r', '').replace(' ', '')
                                        image_bytes = base64.b64decode(clean_data)

                                    print(f"🔍 Final image: {len(image_bytes)} bytes")

                                    # Verify it's a valid PNG
                                    png_signature = b'\x89PNG\r\n\x1a\n'
                                    if image_bytes.startswith(png_signature):
                                        print("✅ Valid PNG signature detected")
                                    else:
                                        print("❌ Invalid PNG signature - first 20 bytes:")
                                        print(f"   {image_bytes[:20].hex()}")
                                        # Try to save anyway, might still work

                                    # Save the image
                                    with open(output_path, 'wb') as f:
                                        f.write(image_bytes)

                                    file_size = Path(output_path).stat().st_size
                                    print(f"✅ Gemini 2.0 Flash image saved: {output_path} ({file_size} bytes)")

                                    # Verify the saved file can be opened
                                    try:
                                        from PIL import Image
                                        img = Image.open(output_path)
                                        print(f"✅ Image verified: {img.size} pixels, mode: {img.mode}")
                                        return True
                                    except ImportError:
                                        print("⚠️  PIL not available for verification")
                                        return True
                                    except Exception as e:
                                        print(f"❌ Image verification failed: {e}")
                                        return False

                                except Exception as e:
                                    print(f"❌ Error processing image data: {e}")
                                    return False

                print("❌ No image data found in Gemini response")
                if hasattr(response, 'text'):
                    print(f"Response text: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Error with Gemini 2.0 Flash image generation: {e}")
                # Don't print full traceback for expected API errors
                if "response modalities" not in str(e):
                    import traceback
                    traceback.print_exc()

            # Method 3: Save prompt for manual use with other services
            prompt_file = str(output_path).replace('.png', '_prompt.txt')
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"Enhanced Gemini Image Generation Prompt:\n\n{enhanced_prompt}")

            print(f"✅ Enhanced prompt saved: {prompt_file}")
            print("ℹ️  Gemini image generation failed, saved prompt for manual use")
            print("💡 Options:")
            print("   1. Use saved prompts with Stability AI (add STABILITY_API_KEY)")
            print("   2. Use saved prompts with DALL-E (add OPENAI_API_KEY)")
            print("   3. Setup Vertex AI for Imagen model")
            print("   4. Fallback to simple background generation")

            return False  # Return False to trigger fallback methods

        except Exception as e:
            print(f"❌ Error with Gemini generation: {e}")
            return False

    def generate_with_stability_ai(self, prompt, output_path, width=1920, height=1080):
        """
        Generate image using Stability AI (Stable Diffusion)
        Requires STABILITY_API_KEY environment variable
        """
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            print("❌ STABILITY_API_KEY not found. Skipping Stability AI generation.")
            return False
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                data = response.json()
                
                for i, image in enumerate(data["artifacts"]):
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(image["base64"]))
                
                print(f"✅ Generated image with Stability AI: {output_path}")
                return True
            else:
                print(f"❌ Stability AI error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error with Stability AI: {e}")
            return False
    
    def generate_with_openai_dalle(self, prompt, output_path, size="1792x1024"):
        """
        Generate image using OpenAI DALL-E
        Requires OPENAI_API_KEY environment variable
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found. Skipping DALL-E generation.")
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "standard"
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                
                # Download the image
                img_response = requests.get(image_url)
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                print(f"✅ Generated image with DALL-E: {output_path}")
                return True
            else:
                print(f"❌ DALL-E error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error with DALL-E: {e}")
            return False
    
    def create_simple_background(self, segment, output_path, width=1920, height=1080):
        """
        Create a simple colored background with text as fallback
        Uses PIL to create basic backgrounds
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import colorsys
            
            # Create base image
            img = Image.new('RGB', (width, height), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Generate a color based on segment title
            title = segment.get('title', 'Segment')
            color_hash = hash(title) % 360
            rgb = colorsys.hsv_to_rgb(color_hash/360, 0.3, 0.9)
            bg_color = tuple(int(c * 255) for c in rgb)
            
            # Create gradient background
            for y in range(height):
                alpha = y / height
                blend_color = tuple(int(bg_color[i] * (1-alpha) + 240 * alpha) for i in range(3))
                draw.line([(0, y), (width, y)], fill=blend_color)
            
            # Add subtle pattern
            for x in range(0, width, 100):
                for y in range(0, height, 100):
                    draw.ellipse([x-10, y-10, x+10, y+10], fill=(255, 255, 255, 30))
            
            img.save(output_path)
            print(f"✅ Created simple background: {output_path}")
            return True
            
        except ImportError:
            print("❌ PIL not available. Install with: pip install Pillow")
            return False
        except Exception as e:
            print(f"❌ Error creating simple background: {e}")
            return False
    
    def enhance_prompt_for_video(self, segment):
        """
        Enhance the visual description for better image generation
        """
        base_prompt = segment.get('visual_description', '')
        title = segment.get('title', '')
        key_points = segment.get('key_points', [])
        
        enhanced_prompt = f"""
        Professional explainer video background image.
        
        Main concept: {title}
        Visual style: Clean, modern, educational, minimalist
        Aspect ratio: 16:9 (1920x1080)
        
        Content description: {base_prompt}
        
        Key elements to include: {', '.join(key_points[:3]) if key_points else 'abstract concepts'}
        
        Requirements:
        - Professional business/educational aesthetic
        - Clean composition with plenty of white space
        - Subtle colors that won't compete with text overlays
        - High contrast areas for text readability
        - Modern flat design style
        - No text or typography in the image
        - Suitable for corporate/educational content
        """
        
        return enhanced_prompt.strip()
    
    def generate_images_for_script(self, script_path):
        """
        Generate all background images for a video script using image prompts

        Args:
            script_path: Path to the video script JSON file
        """
        print("🎨 GENERATING BACKGROUND IMAGES")
        print("=" * 40)

        # Load script
        with open(script_path, 'r', encoding='utf-8') as f:
            script = json.load(f)

        segments = script.get('segments', [])
        success_count = 0

        for segment in segments:
            segment_num = segment['segment_number']
            title = segment['title']

            print(f"\n🖼️  Generating image for Segment {segment_num}: {title}")

            # Use the image_prompt from the segment (generated by Gemini)
            image_prompt = segment.get('image_prompt', '')
            if not image_prompt:
                print(f"⚠️  No image_prompt found for segment {segment_num}, using fallback")
                image_prompt = self.enhance_prompt_for_video(segment)

            print(f"📝 Using prompt: {image_prompt[:100]}...")

            # Output path
            output_path = self.output_dir / f"segment_{segment_num:02d}_background.png"

            # Try different generation methods in order of preference
            success = False

            # Method 1: Gemini (preferred)
            if not success:
                success = self.generate_with_gemini(image_prompt, output_path)

            # Method 2: Stability AI
            if not success:
                success = self.generate_with_stability_ai(image_prompt, output_path)

            # Method 3: DALL-E
            if not success:
                success = self.generate_with_openai_dalle(image_prompt, output_path)

            # Method 4: Simple background fallback
            if not success:
                success = self.create_simple_background(segment, output_path)

            if success:
                success_count += 1
                # Update script with actual image path
                segment['background_image'] = str(output_path)
            else:
                print(f"❌ Failed to generate image for segment {segment_num}")

        # Save updated script
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Generated {success_count}/{len(segments)} background images")
        print(f"📁 Images saved in: {self.output_dir}")

        return success_count == len(segments)


def main():
    """Command line interface for image generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate background images for video explainer')
    parser.add_argument('script_path', help='Path to video script JSON file')
    parser.add_argument('--method', choices=['stability', 'dalle', 'simple', 'auto'], 
                       default='auto', help='Image generation method')
    
    args = parser.parse_args()
    
    if not Path(args.script_path).exists():
        print(f"❌ Script file not found: {args.script_path}")
        return
    
    generator = ImageGenerator()
    
    if args.method == 'auto':
        success = generator.generate_images_for_script(args.script_path)
    else:
        # Load script for manual method selection
        with open(args.script_path, 'r') as f:
            script = json.load(f)
        
        for segment in script['segments']:
            segment_num = segment['segment_number']
            output_path = generator.output_dir / f"segment_{segment_num:02d}_background.png"
            enhanced_prompt = generator.enhance_prompt_for_video(segment)
            
            if args.method == 'stability':
                generator.generate_with_stability_ai(enhanced_prompt, output_path)
            elif args.method == 'dalle':
                generator.generate_with_openai_dalle(enhanced_prompt, output_path)
            elif args.method == 'simple':
                generator.create_simple_background(segment, output_path)
    
    print("\n🎉 Image generation complete!")


if __name__ == '__main__':
    main()
