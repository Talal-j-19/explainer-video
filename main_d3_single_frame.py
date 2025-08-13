from gemini_api_d3_single_frame import get_d3_code_single_frame
import asyncio
from pathlib import Path


async def headless_svg_extract_async(html_file, output_svg):
    """Async wrapper for headless SVG extraction"""
    from playwright.async_api import async_playwright

    print(f"[Headless] Starting SVG extraction...")

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
                print(f"[Headless] ERROR: D3.js failed to load")
                return False

            # Wait for SVG
            await page.wait_for_selector('svg', timeout=15000)
            await page.wait_for_timeout(2000)

            # Validate SVG content
            svg_info = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return null;
                    return {
                        children: svg.children.length,
                        textElements: svg.querySelectorAll('text').length,
                        width: svg.getBoundingClientRect().width,
                        height: svg.getBoundingClientRect().height
                    };
                }
            """)

            if not svg_info or svg_info['children'] < 5:
                print(f"[Headless] ERROR: Invalid SVG content")
                return False

            print(f"[Headless] SVG validated: {svg_info['children']} children, {svg_info['textElements']} text elements")

            # Extract SVG content
            svg_content = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return null;
                    return svg.outerHTML;
                }
            """)

            if not svg_content:
                print(f"[Headless] ERROR: Failed to extract SVG")
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
            print(f"[Headless] ERROR: {e}")
            return False

        finally:
            await browser.close()


async def headless_png_extract_async(html_file, output_png):
    """Async wrapper for headless PNG extraction"""
    from playwright.async_api import async_playwright

    print(f"[Headless] Starting PNG extraction...")

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
                print(f"[Headless] ERROR: D3.js failed to load")
                return False

            # Wait for SVG
            await page.wait_for_selector('svg', timeout=15000)
            await page.wait_for_timeout(2000)

            # Get SVG element for screenshot
            svg_element = await page.query_selector('svg')
            if not svg_element:
                print(f"[Headless] ERROR: No SVG element found")
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


def headless_svg_extract_sync(html_file, output_svg):
    """Synchronous wrapper for headless SVG extraction"""
    return asyncio.run(headless_svg_extract_async(html_file, output_svg))


def headless_png_extract_sync(html_file, output_png):
    """Synchronous wrapper for headless PNG extraction"""
    return asyncio.run(headless_png_extract_async(html_file, output_png))


async def headless_extract_both_async(html_file, output_svg, output_png):
    """Extract both SVG and PNG from the same browser session for efficiency"""
    from playwright.async_api import async_playwright

    print(f"[Headless] Starting SVG and PNG extraction...")

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
                print(f"[Headless] ERROR: D3.js failed to load")
                return False, False

            # Wait for SVG
            await page.wait_for_selector('svg', timeout=15000)
            await page.wait_for_timeout(2000)

            # Get SVG element
            svg_element = await page.query_selector('svg')
            if not svg_element:
                print(f"[Headless] ERROR: No SVG element found")
                return False, False

            # Extract SVG content
            svg_content = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return null;
                    return svg.outerHTML;
                }
            """)

            svg_success = False
            png_success = False

            # Save SVG
            if svg_content:
                try:
                    # Add XML declaration and namespace
                    if not svg_content.startswith('<?xml'):
                        svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

                    if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
                        svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')

                    # Save SVG file
                    with open(output_svg, 'w', encoding='utf-8') as f:
                        f.write(svg_content)

                    svg_size = Path(output_svg).stat().st_size
                    print(f"[Headless] SUCCESS: SVG saved to {output_svg} ({svg_size} bytes)")
                    svg_success = True
                except Exception as e:
                    print(f"[Headless] ERROR saving SVG: {e}")

            # Save PNG
            try:
                await svg_element.screenshot(path=output_png, type='png')
                png_size = Path(output_png).stat().st_size
                print(f"[Headless] SUCCESS: PNG saved to {output_png} ({png_size} bytes)")
                png_success = True
            except Exception as e:
                print(f"[Headless] ERROR saving PNG: {e}")

            return svg_success, png_success

        except Exception as e:
            print(f"[Headless] ERROR: {e}")
            return False, False

        finally:
            await browser.close()


def headless_extract_both_sync(html_file, output_svg, output_png):
    """Synchronous wrapper for extracting both SVG and PNG"""
    return asyncio.run(headless_extract_both_async(html_file, output_svg, output_png))


def main():
    import json
    import sys

    # Check Playwright availability for headless SVG extraction
    try:
        import playwright
        print("✅ Playwright available for headless SVG extraction")
    except ImportError:
        print("❌ Playwright not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
        print("✅ Playwright installed")

    print("=== D3.js Infographic Generator ===")
    print("Provide your text content and we'll create an infographic from it.")
    print()

    # Get user text input
    print("Enter your text content (can be multiple lines, press Ctrl+D or Ctrl+Z when done):")
    print("(Or paste your content and press Enter twice)")

    text_lines = []
    empty_line_count = 0

    try:
        while True:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:  # Two empty lines = done
                    break
            else:
                empty_line_count = 0
                text_lines.append(line)
    except EOFError:
        # Ctrl+D pressed
        pass

    user_text = "\n".join(text_lines).strip()

    if not user_text:
        print("No text provided. Exiting.")
        return

    print(f"\nReceived {len(user_text)} characters of text.")
    print("You can optionally enter advanced options as JSON (or just press Enter to skip):")
    options_input = input("Advanced options (JSON): ")
    options = {}
    if options_input.strip():
        try:
            options = json.loads(options_input)
        except Exception as e:
            print(f"[WARN] Could not parse JSON, ignoring advanced options: {e}")
            options = {}

    # Step 1: Ask LLM to extract key points from the user's text
    from gemini_api_d3_single_frame import get_d3_code_single_frame as llm_call
    print("Analyzing your text and extracting key points for infographic...")

    elements_prompt = {
        "user_text": user_text,
        "task": "analyze_text_for_infographic",
        "instruction": "Analyze the provided text and extract the most important key points that should be visualized in a single-frame D3.js infographic. Focus on the main concepts, data points, relationships, or insights that would work well visually. Return as a JSON list of key points/elements that can fit on one screen. Each element should be a concise description of what to visualize. Do not include code or explanations, just the JSON list."
    }
    elements_prompt.update(options)
    elements_response = llm_call(elements_prompt)

    try:
        elements_list = json.loads(elements_response)
        if not isinstance(elements_list, list):
            raise ValueError("LLM did not return a JSON list.")
    except Exception as e:
        print(f"[ERROR] Could not parse key points from LLM: {e}\nRaw response: {elements_response}")
        return

    print("Key points extracted for infographic:")
    for i, el in enumerate(elements_list, 1):
        print(f"  {i}. {el}")

    # Generate a topic name for job management
    topic_prompt = {
        "user_text": user_text,
        "task": "generate_topic_name",
        "instruction": "Based on the provided text, generate a short, descriptive topic name (2-5 words) that summarizes the main subject. Return only the topic name, no explanations."
    }
    topic_response = llm_call(topic_prompt)
    topic = topic_response.strip().replace('"', '').replace("'", "")[:50]  # Clean and limit length

    print(f"Generated topic: {topic}")

    # Initialize job manager for unique generation
    from job_manager import InfographicJobManager

    job_manager = InfographicJobManager()
    job_id, job_dir = job_manager.create_new_job(topic)
    file_paths = job_manager.get_file_paths()

    # Step 2: Ask LLM to generate D3.js code based on the user's text and extracted elements
    print("Generating D3.js infographic code from your text...")
    code_prompt_obj = {
        "user_text": user_text,
        "topic": topic,
        "elements": elements_list,
        "task": "create_infographic_from_text",
        "instruction": "Create a D3.js (HTML+JS) infographic that visualizes the key points from the provided text. Use the extracted elements as a guide, but focus on representing the actual content and insights from the user's text. The infographic should be informative, visually appealing, and fit on one screen. Include relevant data, concepts, and relationships from the text. Follow all D3.js best practices."
    }
    code_prompt_obj.update(options)
    max_attempts = 10
    attempt = 0
    code_file = str(file_paths['html'])  # Use job-specific path
    d3_code = get_d3_code_single_frame(code_prompt_obj)

    while attempt < max_attempts:
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(d3_code)
        print(f"Generated D3.js code saved to: {code_file}")

        # Add responsive scaling to ensure infographic fits on screen
        try:
            from add_responsive_scaling import add_responsive_scaling
            add_responsive_scaling(code_file)
            print("✅ Added responsive scaling for proper display")
        except Exception as e:
            print(f"[WARN] Could not add responsive scaling: {e}")

        # Try to open the HTML file in the default browser for preview
        import webbrowser
        import os
        abs_path = os.path.abspath(code_file)
        print(f"Opening {abs_path} in your default browser...")
        webbrowser.open(f"file://{abs_path}")

        # Ask user if the output looks correct
        user_feedback = input("Does the output look correct? (y/n): ").strip().lower()
        if user_feedback == 'y':
            # Export both PNG and SVG using headless method (more efficient)
            try:
                print("Exporting infographic as PNG and SVG using headless browser...")
                svg_success, png_success = headless_extract_both_sync(
                    code_file, str(file_paths['svg']), str(file_paths['png'])
                )

                if png_success:
                    print(f"PNG saved to: {file_paths['png']}")
                else:
                    print("[WARN] Failed to extract PNG using headless method")

                if svg_success:
                    print(f"SVG saved to: {file_paths['svg']}")
                else:
                    print("[WARN] Failed to extract SVG using headless method")

                if not (png_success or svg_success):
                    print("[ERROR] Failed to extract both PNG and SVG")

            except Exception as e:
                print(f"[ERROR] Could not export files automatically: {e}")
                import traceback
                traceback.print_exc()

            # Save job information
            job_manager.save_job_info(topic, len(elements_list))
            print(f"✅ Job completed: {job_id}")
            print(f"📁 Files saved in: {job_dir}")
            break
        else:
            print("Attempting to fix code using Gemini API...")
            from gemini_api_d3_single_frame import get_d3_code_single_frame as fix_d3_code
            error_prompt_obj = {
                "user_text": user_text,
                "topic": topic,
                "elements": elements_list,
                "task": "fix_infographic_code",
                "error_message": "User feedback: output is not correct.",
                "previous_code": d3_code,
                "instruction": "Fix the D3.js infographic code based on user feedback. The infographic should accurately represent the content from the user's text. Ensure it's visually appealing, informative, and follows D3.js best practices.",
                "rules": [
                    "Only return valid, working D3.js (v7+) and SVG code.",
                    "The output must be a single static frame (no animation unless requested).",
                    "Focus on representing the user's text content accurately.",
                    "Use only valid D3.js and SVG syntax and functions.",
                    "DO NOT use any markdown, explanations, or extra text.",
                    "DO NOT use '```' or 'html' code blocks.",
                    "If you are unsure, copy working patterns from the official D3.js documentation."
                ]
            }
            error_prompt_obj.update(options)
            d3_code = fix_d3_code(error_prompt_obj)
            attempt += 1
    else:
        print("Failed to generate correct D3.js code after 5 attempts.")

if __name__ == "__main__":
    main()
