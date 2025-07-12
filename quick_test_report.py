#!/usr/bin/env python3
"""
Quick test for ISEE report generation using the most recent run
"""

import os
import sys
from pathlib import Path
from report_generator import ISEEReportGenerator

def main():
    # Use the specific file you mentioned
    input_file = "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/run_20250711_171914/isee_result.md"
    output_file = "/Users/josephfajen/git/ISEE_Meta_Framework/data/output/run_20250711_171914/isee_report.html"
    
    print("🚀 Quick ISEE Report Generation Test")
    print("=" * 60)
    print(f"📄 Input:  {input_file}")
    print(f"📄 Output: {output_file}")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Check file size
    file_size = os.path.getsize(input_file)
    print(f"📊 Input file size: {file_size:,} bytes")
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("\n⚠️  No OPENROUTER_API_KEY found in environment")
        print("🔄 Will test fallback generation only...")
        
        # Test fallback generation
        generator = ISEEReportGenerator()
        result = generator.generate_fallback_report(input_file, output_file.replace('.html', '_fallback.html'))
        
        if result["success"]:
            print("✅ Fallback generation successful!")
            print(f"   📍 Report: {result['report_path']}")
            print(f"   🌐 Open: file://{os.path.abspath(result['report_path'])}")
            return True
        else:
            print(f"❌ Fallback generation failed: {result.get('error')}")
            return False
    
    # Test full LLM generation
    print(f"🤖 Testing LLM report generation with fallback chain...")
    print("   📋 Chain: Claude 3.5 Sonnet → GPT-4o → Claude 3.5 Haiku")
    
    generator = ISEEReportGenerator(api_key)
    
    # Generate the report
    result = generator.generate_report(input_file, output_file)
    
    if result["success"]:
        print("\n🎉 Report generation successful!")
        print(f"   🤖 Model used: {result.get('successful_model', 'Unknown')}")
        print(f"   📊 Report size: {result['report_size']:,} characters")
        print(f"   ⏱️  Generated: {result['generation_time']}")
        print(f"   📍 Report saved: {result['report_path']}")
        print(f"   🌐 Open in browser: file://{os.path.abspath(result['report_path'])}")
        
        # Verify the file
        if os.path.exists(output_file):
            actual_size = os.path.getsize(output_file)
            print(f"   ✅ File verified: {actual_size:,} bytes on disk")
            
            # Quick content check
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read(500)  # First 500 chars
                if '<html' in content.lower() and '<head>' in content.lower():
                    print("   ✅ HTML structure verified")
                else:
                    print("   ⚠️  Warning: Content doesn't look like proper HTML")
        
        return True
    else:
        print(f"\n❌ Report generation failed: {result.get('error')}")
        
        # Try fallback if available
        if result.get("fallback_available"):
            print("🔄 Attempting fallback generation...")
            fallback_path = output_file.replace('.html', '_fallback.html')
            fallback_result = generator.generate_fallback_report(input_file, fallback_path)
            
            if fallback_result["success"]:
                print("✅ Fallback generation successful!")
                print(f"   📍 Fallback report: {fallback_result['report_path']}")
                print(f"   🌐 Open: file://{os.path.abspath(fallback_result['report_path'])}")
                return True
            else:
                print(f"❌ Fallback also failed: {fallback_result.get('error')}")
        
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("\n💡 Next steps:")
        print("   • Open the generated HTML file in your browser")
        print("   • Review the report quality and structure")
        print("   • Check that all sections are properly formatted")
    else:
        print("💥 Test failed")
        print("\n💡 Troubleshooting:")
        print("   • Check OPENROUTER_API_KEY environment variable")
        print("   • Verify internet connection for API calls")
        print("   • Review error messages above")
        
    sys.exit(0 if success else 1)