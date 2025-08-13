#!/usr/bin/env python3
"""
Test JSON cleaning functionality
"""

import json
import re

def clean_json_response(result):
    """Test the JSON cleaning logic"""
    
    # Clean up JSON response
    if result.startswith("```json"):
        result = result[7:]
    if result.startswith("```"):
        result = result[3:]
    if result.endswith("```"):
        result = result[:-3]
    result = result.strip()
    
    # Additional cleaning for common AI response issues
    # Remove any text that appears after the JSON array
    if result.find(']') != -1:
        end_bracket_pos = result.rfind(']')
        result = result[:end_bracket_pos + 1]
    
    # Remove any stray text that might appear in the middle
    # Look for patterns like "Tapi" or other non-JSON text
    result = re.sub(r'\n\s*[A-Za-z]+\s*\n', '\n', result)
    
    return result

# Test with the problematic response
test_response = """[
  {
    "segment_number": 1,
    "title": "Unlocking Data Insights",
    "narration_text": "Machine learning algorithms are transforming how businesses understand vast amounts of data.",
    "key_points": [
      "Machine Learning",
      "Data Analysis",
      "Business Insights"
    ],
    "image_prompt": "A clean, modern, professional background image...",
    "text_overlay": "MACHINE LEARNING INSIGHTS",
    "duration_seconds": 9
  Tapi
  },
  {
    "segment_number": 2,
    "title": "Predicting Customer Actions",
    "narration_text": "This advanced technology enables companies to predict future customer behavior.",
    "key_points": [
      "Customer Behavior",
      "Predictive Analytics"
    ],
    "image_prompt": "A modern, professional visual representation...",
    "text_overlay": "PREDICTING CUSTOMER BEHAVIOR",
    "duration_seconds": 9
  }
]"""

print("🧪 Testing JSON cleaning...")
print(f"Original length: {len(test_response)}")

cleaned = clean_json_response(test_response)
print(f"Cleaned length: {len(cleaned)}")

try:
    parsed = json.loads(cleaned)
    print(f"✅ Successfully parsed {len(parsed)} segments")
    for i, seg in enumerate(parsed, 1):
        print(f"  Segment {i}: {seg.get('title', 'No title')}")
except json.JSONDecodeError as e:
    print(f"❌ Still failed: {e}")
    print(f"Cleaned text preview:")
    print(cleaned[:500])
    
    # Try additional fixes
    print("\n🔧 Trying additional fixes...")
    
    # Remove trailing commas
    fixed_result = re.sub(r',\s*}', '}', cleaned)
    fixed_result = re.sub(r',\s*]', ']', fixed_result)
    
    # Remove the problematic "Tapi" line more aggressively
    lines = fixed_result.split('\n')
    clean_lines = []
    for line in lines:
        # Skip lines that are just random text
        if line.strip() and not any(char in line for char in '{}[]":,'):
            if len(line.strip()) < 10 and line.strip().isalpha():
                print(f"Removing problematic line: '{line.strip()}'")
                continue
        clean_lines.append(line)
    
    fixed_result = '\n'.join(clean_lines)
    
    try:
        parsed = json.loads(fixed_result)
        print(f"✅ Fixed! Successfully parsed {len(parsed)} segments")
    except json.JSONDecodeError as e2:
        print(f"❌ Still failed after fixes: {e2}")
        print("Final cleaned text:")
        print(fixed_result[:300])
