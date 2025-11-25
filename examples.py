#!/usr/bin/env python3
"""
Quick Start Guide for Integrated Explainer Video with Template-Based Infographics

This example demonstrates how to use the new integrated system.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from main directory
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Add the explainer-video directory to path
sys.path.insert(0, str(Path(__file__).parent))

from integrated_image_generator import IntegratedImageGenerator
from create_explainer_video_integrated import IntegratedExplainerVideoCreator


async def example_1_image_generation():
    """Example 1: Generate images only from a script"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Generate Infographic Images Only")
    print("="*70)
    
    # Assuming you have a video_script.json file
    script_path = "video_segments/video_script.json"
    
    if not Path(script_path).exists():
        print(f"⚠️ Script not found: {script_path}")
        print("   Create a script first or use a different path")
        return
    
    print(f"\n📍 Loading script: {script_path}")
    
    # Create the integrated image generator
    generator = IntegratedImageGenerator(
        output_dir='video_segments',
        use_content_only=True  # Get clean content without outer wrapper
    )
    
    # Generate images for all segments
    print("\n🔄 Starting image generation...")
    success = await generator.generate_images_for_script(script_path)
    
    if success:
        print("\n✅ All images generated successfully!")
    else:
        print("\n⚠️ Some images failed, check output above")


async def example_2_full_video():
    """Example 2: Create a complete explainer video"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Create Complete Explainer Video")
    print("="*70)
    
    topic = "Quantum Computing Basics"
    
    print(f"\n📝 Topic: {topic}")
    print(f"⏱️  Target Duration: 60 seconds")
    print(f"📁 Output: generated_videos/")
    
    # Create the integrated creator
    creator = IntegratedExplainerVideoCreator(use_integrated=True)
    
    print("\n🚀 Starting video generation...")
    print("   (This may take several minutes)\n")
    
    # Generate the video
    result = await creator.generate_video_with_integrated_images(
        prompt=topic,
        target_duration=60,
        output_dir="generated_videos"
    )
    
    if result.get('success'):
        print(f"\n✅ Video generation complete!")
        print(f"📁 Location: {result.get('final_video')}")
        print(f"⏱️  Total time: {result.get('total_time'):.1f}s")
    else:
        print(f"\n❌ Video generation failed")
        if 'error' in result:
            print(f"   Error: {result.get('error')}")


async def example_3_custom_settings():
    """Example 3: Generate with custom settings"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Settings")
    print("="*70)
    
    topic = "Machine Learning in Healthcare"
    duration = 90  # 1.5 minutes
    output_dir = "my_explainer_videos"
    
    print(f"\n⚙️ Settings:")
    print(f"   📝 Topic: {topic}")
    print(f"   ⏱️  Duration: {duration}s")
    print(f"   📁 Output: {output_dir}/")
    print(f"   🔗 Infographics: Template-Based V2 (Integrated)")
    
    creator = IntegratedExplainerVideoCreator(use_integrated=True)
    
    print("\n🚀 Starting with custom settings...")
    
    result = await creator.generate_video_with_integrated_images(
        prompt=topic,
        target_duration=duration,
        output_dir=output_dir
    )
    
    if result.get('success'):
        print(f"\n✅ Success!")
        print(f"📊 Using: {'Template-Based V2' if result.get('using_integrated') else 'External API'}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")


async def example_4_compare_systems():
    """Example 4: Compare integrated vs legacy"""
    print("\n" + "="*70)
    print("EXAMPLE 4: System Comparison")
    print("="*70)
    
    topic = "AI Evolution"
    
    print(f"\n📊 Generating with both systems for comparison...")
    print(f"   Topic: {topic}\n")
    
    # Test 1: Integrated (New)
    print("1️⃣ INTEGRATED SYSTEM (Template-Based V2)")
    print("-" * 50)
    creator_integrated = IntegratedExplainerVideoCreator(use_integrated=True)
    result_integrated = await creator_integrated.generate_video_with_integrated_images(
        prompt=topic,
        target_duration=30,
        output_dir="comparison/integrated"
    )
    
    # Test 2: Legacy (Old)
    print("\n2️⃣ LEGACY SYSTEM (External API)")
    print("-" * 50)
    creator_legacy = IntegratedExplainerVideoCreator(use_integrated=False)
    result_legacy = await creator_legacy.generate_video_with_integrated_images(
        prompt=topic,
        target_duration=30,
        output_dir="comparison/legacy"
    )
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    
    print(f"\nIntegrated System:")
    print(f"  Status: {'✅ Success' if result_integrated.get('success') else '❌ Failed'}")
    if result_integrated.get('final_video'):
        print(f"  Video: {result_integrated.get('final_video')}")
    print(f"  Time: {result_integrated.get('total_time', 'N/A'):.1f}s" 
          if result_integrated.get('total_time') else "  Time: N/A")
    
    print(f"\nLegacy System:")
    print(f"  Status: {'✅ Success' if result_legacy.get('success') else '❌ Failed'}")
    if result_legacy.get('final_video'):
        print(f"  Video: {result_legacy.get('final_video')}")
    print(f"  Time: {result_legacy.get('total_time', 'N/A'):.1f}s"
          if result_legacy.get('total_time') else "  Time: N/A")


async def main():
    """Run examples"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   Integrated Explainer Video with Template-Based Infographics       ║
║                       QUICK START EXAMPLES                          ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    examples = {
        '1': ('Image Generation Only', example_1_image_generation),
        '2': ('Full Video Generation', example_2_full_video),
        '3': ('Custom Settings', example_3_custom_settings),
        '4': ('Compare Systems', example_4_compare_systems),
    }
    
    print("Available Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run All Examples")
    print("  q. Quit")
    
    choice = input("\nSelect example (0-4, q): ").strip().lower()
    
    if choice == 'q':
        print("Goodbye!")
        return
    
    if choice == '0':
        for key in sorted(examples.keys()):
            try:
                await examples[key][1]()
            except Exception as e:
                print(f"\n❌ Error in {examples[key][0]}: {e}")
    elif choice in examples:
        try:
            await examples[choice][1]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice")


if __name__ == '__main__':
    # Run interactively or specific example
    if len(sys.argv) > 1:
        # Run specific example: python examples.py 2
        example_num = sys.argv[1]
        examples = {
            '1': example_1_image_generation,
            '2': example_2_full_video,
            '3': example_3_custom_settings,
            '4': example_4_compare_systems,
        }
        
        if example_num in examples:
            asyncio.run(examples[example_num]())
        else:
            print(f"Example {example_num} not found")
            sys.exit(1)
    else:
        # Interactive menu
        asyncio.run(main())
