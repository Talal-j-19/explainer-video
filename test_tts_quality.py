#!/usr/bin/env python3
"""
Comprehensive TTS Quality Test Script
Tests the new Google TTS service with various text samples and evaluates audio quality
"""

import os
import sys
import time
from pathlib import Path
from tts_processor import TTSProcessor
import json

def create_test_samples():
    """Create various test text samples for TTS quality evaluation"""
    samples = [
        {
            "name": "Short Simple",
            "text": "Hello world. This is a test of the text to speech system.",
            "expected_duration": "3-4 seconds"
        },
        {
            "name": "Technical Content",
            "text": "Artificial intelligence and machine learning are transforming how we process data and make decisions in modern technology.",
            "expected_duration": "6-7 seconds"
        },
        {
            "name": "Narration Style",
            "text": "Welcome to our explainer video. Today we'll explore the fascinating world of computer science and its impact on our daily lives.",
            "expected_duration": "8-9 seconds"
        },
        {
            "name": "Complex Terms",
            "text": "The algorithm processes neural networks through backpropagation, optimizing weights using gradient descent and stochastic optimization.",
            "expected_duration": "7-8 seconds"
        },
        {
            "name": "Long Paragraph",
            "text": "In this comprehensive overview, we examine the fundamental principles of data science, including statistical analysis, machine learning algorithms, data visualization techniques, and the ethical considerations surrounding artificial intelligence implementation in enterprise environments.",
            "expected_duration": "12-15 seconds"
        }
    ]
    return samples

def test_tts_quality():
    """Run comprehensive TTS quality tests"""
    print("=== TTS Quality Test Suite ===")
    print(f"Testing Google Text-to-Speech Implementation")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test output directory
    test_dir = Path("tts_quality_test")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize TTS processor
    tts = TTSProcessor(video_segments_dir=str(test_dir))
    
    # Get test samples
    samples = create_test_samples()
    
    results = []
    
    print(f"Running {len(samples)} test samples...")
    print("=" * 60)
    
    for i, sample in enumerate(samples, 1):
        print(f"\nTest {i}/{len(samples)}: {sample['name']}")
        print(f"Text: {sample['text']}")
        print(f"Expected Duration: {sample['expected_duration']}")
        
        # Create test narration data
        output_file = test_dir / f"test_{i:02d}_{sample['name'].replace(' ', '_').lower()}.wav"
        
        narration_data = {
            'segment_number': i,
            'clean_text': sample['text'],
            'output_audio': str(output_file)
        }
        
        # Time the generation
        start_time = time.time()
        
        # Generate audio
        success = tts.generate_audio_for_segment(narration_data, tts_service='gemini_tts')
        
        generation_time = time.time() - start_time
        
        if success and Path(output_file).exists():
            file_size = Path(output_file).stat().st_size
            
            result = {
                'test_name': sample['name'],
                'text': sample['text'],
                'expected_duration': sample['expected_duration'],
                'file_path': str(output_file),
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'generation_time_seconds': round(generation_time, 2),
                'success': True
            }
            
            print(f"  Success! File: {output_file.name}")
            print(f"  File Size: {result['file_size_mb']} MB ({file_size:,} bytes)")
            print(f"  Generation Time: {result['generation_time_seconds']} seconds")
            
        else:
            result = {
                'test_name': sample['name'],
                'text': sample['text'],
                'expected_duration': sample['expected_duration'],
                'file_path': str(output_file),
                'file_size_bytes': 0,
                'file_size_mb': 0,
                'generation_time_seconds': round(generation_time, 2),
                'success': False
            }
            
            print(f"  Failed to generate audio!")
        
        results.append(result)
        print("-" * 40)
    
    # Generate summary report
    generate_summary_report(results, test_dir)
    
    # Test audio playback if possible
    print_audio_playback_instructions(results, test_dir)
    
    return results

def generate_summary_report(results, test_dir):
    """Generate a detailed summary report of the test results"""
    report_file = test_dir / "tts_quality_report.json"
    
    # Calculate statistics
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    if successful_tests:
        avg_file_size = sum(r['file_size_bytes'] for r in successful_tests) / len(successful_tests)
        avg_generation_time = sum(r['generation_time_seconds'] for r in successful_tests) / len(successful_tests)
        total_size = sum(r['file_size_bytes'] for r in successful_tests)
    else:
        avg_file_size = 0
        avg_generation_time = 0
        total_size = 0
    
    report = {
        'test_summary': {
            'total_tests': len(results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': f"{(len(successful_tests) / len(results) * 100):.1f}%" if results else "0%",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'statistics': {
            'average_file_size_bytes': round(avg_file_size),
            'average_file_size_mb': round(avg_file_size / (1024 * 1024), 2),
            'average_generation_time_seconds': round(avg_generation_time, 2),
            'total_audio_size_bytes': total_size,
            'total_audio_size_mb': round(total_size / (1024 * 1024), 2)
        },
        'detailed_results': results
    }
    
    # Save JSON report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TTS QUALITY TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Successful: {report['test_summary']['successful_tests']}")
    print(f"Failed: {report['test_summary']['failed_tests']}")
    print(f"Success Rate: {report['test_summary']['success_rate']}")
    print()
    print("STATISTICS:")
    print(f"Average File Size: {report['statistics']['average_file_size_mb']} MB")
    print(f"Average Generation Time: {report['statistics']['average_generation_time_seconds']} seconds")
    print(f"Total Audio Size: {report['statistics']['total_audio_size_mb']} MB")
    print()
    print(f"Detailed report saved to: {report_file}")
    print(f"Audio files saved to: {test_dir}")

def print_audio_playback_instructions(results, test_dir):
    """Print instructions for listening to the generated audio files"""
    successful_tests = [r for r in results if r['success']]
    
    if successful_tests:
        print("\n" + "=" * 60)
        print("AUDIO PLAYBACK INSTRUCTIONS")
        print("=" * 60)
        print("To listen to the generated audio files:")
        print()
        print("Method 1 - Direct file opening:")
        for result in successful_tests:
            print(f"  - {result['file_path']}")
        
        print("\nMethod 2 - Using PowerShell:")
        print("  # Copy and paste these commands one by one:")
        for result in successful_tests:
            print(f"  Start-Process \"{result['file_path']}\"")
        
        print("\nMethod 3 - Using Windows Media Player:")
        print("  # Open Windows Media Player and drag the audio files")
        print(f"  # Files are located in: {test_dir}")
        
        print("\nAudio Quality Assessment:")
        print("  - Listen for clarity and naturalness")
        print("  - Check for proper pacing and intonation")
        print("  - Verify pronunciation of technical terms")
        print("  - Note any robotic or unnatural artifacts")

def main():
    """Main test execution"""
    try:
        results = test_tts_quality()
        
        if all(r['success'] for r in results):
            print(f"\nAll tests passed! TTS service is working correctly.")
            return True
        else:
            failed_count = sum(1 for r in results if not r['success'])
            print(f"\n{failed_count} test(s) failed. Check the report for details.")
            return False
            
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
