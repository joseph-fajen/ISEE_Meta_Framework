#!/usr/bin/env python3
"""
Test script for ISEE Report Generation functionality
"""

import os
import sys
from pathlib import Path
from report_generator import ISEEReportGenerator

def test_report_generation():
    """Test report generation with an existing ISEE result file"""
    
    # Find a recent ISEE result file for testing
    test_files = [
        "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/demo_results_exec_1750460894.md",
        "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/run_20250612_152533/isee_result.md",
        "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/run_20250612_144401/isee_result.md"
    ]
    
    # Find the first existing test file
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test ISEE result files found")
        return False
    
    print(f"📄 Using test file: {test_file}")
    
    # Get API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("💡 Set it with: export OPENROUTER_API_KEY='your-key-here'")
        return False
    
    # Create report generator
    generator = ISEEReportGenerator(api_key)
    
    # Generate output path
    test_file_path = Path(test_file)
    output_path = test_file_path.parent / "test_generated_report.html"
    
    print("🔄 Generating HTML report...")
    print(f"   Input: {test_file}")
    print(f"   Output: {output_path}")
    
    # Test the report generation
    result = generator.generate_report(test_file, str(output_path))
    
    if result["success"]:
        print("✅ Report generation successful!")
        print(f"   📊 Report size: {result['report_size']:,} characters")
        print(f"   🤖 Model used: {result.get('successful_model', 'Unknown')}")
        print(f"   📍 Report saved: {result['report_path']}")
        
        # Check if file actually exists and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"   ✅ File verified: {os.path.getsize(output_path):,} bytes")
            print(f"   🌐 View report: file://{os.path.abspath(output_path)}")
            return True
        else:
            print("   ❌ Generated file is missing or empty")
            return False
    else:
        print(f"❌ Report generation failed: {result.get('error')}")
        
        # Try fallback generation
        if result.get("fallback_available"):
            print("🔄 Trying fallback generation...")
            fallback_path = test_file_path.parent / "test_fallback_report.html"
            fallback_result = generator.generate_fallback_report(test_file, str(fallback_path))
            
            if fallback_result["success"]:
                print("✅ Fallback report generation successful!")
                print(f"   📍 Fallback report: {fallback_result['report_path']}")
                print(f"   🌐 View report: file://{os.path.abspath(fallback_path)}")
                return True
            else:
                print(f"❌ Fallback generation also failed: {fallback_result.get('error')}")
        
        return False

def test_fallback_only():
    """Test just the fallback generation (no API key required)"""
    
    test_files = [
        "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/demo_results_exec_1750460894.md",
        "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/run_20250612_152533/isee_result.md"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test ISEE result files found")
        return False
    
    print(f"📄 Testing fallback generation with: {test_file}")
    
    generator = ISEEReportGenerator()  # No API key
    output_path = Path(test_file).parent / "test_fallback_only_report.html"
    
    result = generator.generate_fallback_report(test_file, str(output_path))
    
    if result["success"]:
        print("✅ Fallback generation successful!")
        print(f"   📍 Report saved: {result['report_path']}")
        print(f"   🌐 View report: file://{os.path.abspath(output_path)}")
        return True
    else:
        print(f"❌ Fallback generation failed: {result.get('error')}")
        return False

if __name__ == "__main__":
    print("🧪 ISEE Report Generation Test")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--fallback-only":
        success = test_fallback_only()
    else:
        success = test_report_generation()
        
        # If main test failed, try fallback
        if not success:
            print("\n🔄 Trying fallback-only test...")
            success = test_fallback_only()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed")
        sys.exit(1)