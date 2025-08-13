#!/usr/bin/env python3
"""
Test the new JSON-based video explainer pipeline
"""

import json
from video_explainer_generator import VideoExplainerGenerator
from image_generator import ImageGenerator


def test_pipeline():
    """Test the complete pipeline with sample text"""
    
    # Sample text for testing
    sample_text = """
    Jellyfish exhibit complex and varying life cycles, often reproducing both sexually and asexually, with different species employing diverse strategies. Their distribution and life cycle are significantly influenced by a combination of environmental factors and human activities.
Environmental Factors:
• Temperature:
    ◦ Warmer waters generally favor jellyfish growth, provided there is sufficient food.
    ◦ Temperature is considered a crucial factor for the budding of medusae from polyps in species like Craspedacusta sowerbii, with some studies indicating that temperatures of at least 28°C are necessary for medusa production in temperate regions, leading to their prevalence in summer.
    ◦ Lakes at lower altitudes, which typically have higher average temperatures, show a significantly higher occurrence of C. sowerbii medusae. This aligns with the adiabatic lapse rate, where air temperature decreases by about 0.6°C per 100 meters of altitude, influencing lake surface temperatures.
    ◦ Projected elevated temperatures due to climate change are expected to directly increase medusa production by C. sowerbii polyps.
    ◦ Decreased precipitation, leading to lower water levels and increased lake temperatures, can also enhance medusa production.
• Oxygen Levels: Declining oxygen levels, which are anticipated to increase globally due to climate change, can favor certain jellyfish types. Some jellyfish are more tolerant of very low-oxygen conditions than most other plankton, potentially leading to their dominance in deoxygenated waters.
• Salinity: Some jellyfish species thrive in normal or higher salinity levels, meaning drier conditions could lead to more jellyfish. Conversely, heavier rainfall can reduce coastal seawater salinity, potentially decreasing jellyfish outbreaks in those areas.
• Nutrient and Food Availability:
    ◦ Jellyfish growth is supported when their food sources, such as krill larvae, copepods, or fish eggs, become more abundant.
    ◦ Jelly blooms, or mass reproduction events, are linked to an abundance of nutrients and suitable conditions. This often occurs in spring when warmer temperate waters stimulate the growth of phytoplankton, which in turn feeds zooplankton, providing ample energy for jellies to reproduce.
    ◦ Nitrate, a common pollutant from agricultural sources, has a negative impact on the growth of C. sowerbii polyps, even at low concentrations, under both acute and chronic exposure. Field observations support this, showing significantly lower polyp numbers in rivers with higher nitrate concentrations.
• Water Chemistry (General): The overall chemical composition of water, including factors influenced by altitude such as organic matter, light intensity, pH, and CO2 concentration, can affect the budding process of C. sowerbii polyps. Conditions at higher altitudes (less organic matter, higher light, lower CO2, higher pH) are thought to hinder medusa development.
• Physical Stress: For species like Turritopsis dohrnii (the immortal jellyfish), environmental stress, physical assault, sickness, or old age can induce a unique process called transdifferentiation, allowing them to revert from their adult medusa stage back to an immature polyp stage. In nature, however, predation or disease often prevents this reversal. Jellyfish can also die from damage due to rough waves, boat propellers, or bacteria.
Human Activities:
• Coastal Development: Increased construction of harbors and marinas provides additional hard surfaces for jellyfish polyps to attach, which can lead to rapid population growth and more jellyfish in coastal areas.
• Shipping and Ballast Water: The global spread of jellyfish, including Turritopsis, is largely attributed to ballast water discharge from ships. This has resulted in a "worldwide silent invasion" due to their small size and generally unnoticed impact.
• Modification of River Systems: Human-made modifications to river systems, such as the creation of vast connected waterways and artificial ponds/impoundments (like those in Europe connecting major seas), serve as "stepping stones" for aquatic organisms. These modified systems act as significant dispersal routes for invasive species like C. sowerbii, facilitating their long-distance transport.
• Introduction of Ornamental Plants: The initial introduction of C. sowerbii to Europe is believed to have occurred via the transport of tropical ornamental plants in botanical gardens.
• Agricultural Runoff (ARO):
    ◦ The widespread use of nitrogen fertilizers in modern agriculture significantly contributes to nitrate pollution in surface waters, affecting jellyfish polyp growth.
    ◦ Agricultural pesticides, entering freshwater systems through runoff, have been shown to impact C. sowerbii polyps, potentially influencing their distribution. Increased heavy rainfall events, exacerbated by global warming, further intensify the flow of pesticides into aquatic ecosystems.
    ◦ The herbicide Terbuthylazine (TBA), for instance, was found to have an overall positive effect on the growth of C. sowerbii polyps in experiments.
    ◦ Conversely, the fungicide Tebuconazole had a negative effect on polyp growth, with lower concentrations sometimes having a greater effect, possibly due to its impact on fungi that could stress polyps, while higher concentrations might reduce fungal infections, allowing for better growth.
    ◦ The insecticide Pirimicarb, in the tested concentrations, showed no significant effect on the growth of C. sowerbii polyps.
• Climate Change (Human-induced):
    ◦ Beyond direct temperature effects, climate change influences precipitation patterns, leading to more flood events that can enhance C. sowerbii dispersal by temporarily connecting isolated freshwater bodies.
    ◦ Climate change also contributes to eutrophication in lakes, increasing nutrient concentrations and leading to more algal blooms and dissolved organic matter. This reduces light availability, which can favor tactile predators like jellyfish over visually oriented fish, potentially shifting the top predator in aquatic food webs.
In summary, jellyfish, particularly resilient species like C. sowerbii, are adept at adapting to a wide range of environmental conditions. Human activities, from global shipping to agricultural practices and climate change, appear to create conditions that often favor the expansion of jellyfish populations, leading to their increasing distribution and potential ecological impacts worldwide
    """
    
    print("🧪 TESTING VIDEO EXPLAINER PIPELINE")
    print("=" * 50)
    print(f"Sample text length: {len(sample_text)} characters")
    print()
    
    # Step 1: Generate video script with image prompts
    print("📝 Step 1: Generating video script...")
    generator = VideoExplainerGenerator()
    
    result = generator.generate_explainer_video_plan(
        text_content=sample_text,
        target_duration=45,  # 45 seconds
        segments_count=5     # 5 segments
    )
    
    if not result:
        print("❌ Failed to generate video script")
        return False
    
    script_path = result['script_path']
    script = result['script']
    
    # Display the generated segments
    print("\n📋 Generated Segments:")
    for segment in script['segments']:
        print(f"\n🎬 Segment {segment['segment_number']}: {segment['title']}")
        print(f"   ⏱️  Duration: {segment['duration_seconds']}s")
        print(f"   🗣️  Narration: {segment['narration_text'][:80]}...")
        print(f"   📝 Overlay: {segment['text_overlay']}")
        print(f"   🎨 Image prompt: {segment['image_prompt'][:100]}...")
    
    # Step 2: Generate images using the prompts
    print(f"\n🎨 Step 2: Generating background images...")
    image_gen = ImageGenerator()
    
    images_success = image_gen.generate_images_for_script(script_path)
    
    if images_success:
        print("✅ All images generated successfully")
    else:
        print("⚠️  Some images failed to generate (check fallbacks)")
    
    # Step 3: Display final results
    print(f"\n📊 PIPELINE TEST RESULTS")
    print("=" * 30)
    
    # Reload script to see updated paths
    with open(script_path, 'r') as f:
        final_script = json.load(f)
    
    metadata = final_script['video_metadata']
    print(f"✅ Video segments: {metadata['total_segments']}")
    print(f"✅ Total duration: {metadata['estimated_duration']} seconds")
    print(f"✅ Generation method: {metadata.get('generation_method', 'standard')}")
    print(f"✅ Script file: {script_path}")
    
    print(f"\n📁 Generated Files:")
    for segment in final_script['segments']:
        print(f"   🖼️  {segment['background_image']}")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Review generated script: {script_path}")
    print(f"2. Check background images in: video_segments/")
    print(f"3. Use TTS to generate audio from narration")
    print(f"4. Combine into final video")
    
    return True


def test_json_prompting():
    """Test JSON prompting specifically"""
    
    print("\n🧪 TESTING JSON PROMPTING")
    print("=" * 30)
    
    sample_text = "Machine learning algorithms can predict customer behavior with 85% accuracy."
    
    generator = VideoExplainerGenerator()
    
    # Test the analyze_text_for_video method directly
    segments = generator.analyze_text_for_video(
        text_content=sample_text,
        target_duration=20,
        segments_count=3
    )
    
    if segments:
        print("✅ JSON prompting successful")
        print(f"Generated {len(segments)} segments")
        
        for i, segment in enumerate(segments, 1):
            print(f"\nSegment {i}:")
            print(f"  Title: {segment.get('title', 'N/A')}")
            print(f"  Image prompt: {segment.get('image_prompt', 'N/A')[:80]}...")
            print(f"  Duration: {segment.get('duration_seconds', 'N/A')}s")
        
        return True
    else:
        print("❌ JSON prompting failed")
        return False


def main():
    """Run all tests"""
    print("🚀 TESTING NEW VIDEO PIPELINE")
    print("=" * 60)
    
    # Test 1: JSON prompting
    json_success = test_json_prompting()
    
    # Test 2: Complete pipeline
    if json_success:
        pipeline_success = test_pipeline()
        
        if pipeline_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"The new JSON-based pipeline is working correctly.")
        else:
            print(f"\n⚠️  Pipeline test had issues, but JSON prompting works.")
    else:
        print(f"\n❌ JSON prompting failed - check Gemini API configuration")


if __name__ == '__main__':
    main()
