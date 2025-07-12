#!/usr/bin/env python3
"""
Simple test script for ISEE report generation

This script tests the report generation system by taking an existing isee_result.md file
and generating a new HTML report using the updated prompt, without requiring a full ISEE run.

Usage:
    python test_report_generation.py <path_to_isee_result.md> [output_path]

Example:
    python test_report_generation.py data/output/run_20250711_231747/isee_result.md
    python test_report_generation.py data/output/run_20250711_231747/isee_result.md my_test_report.html
"""

import sys
import os
from pathlib import Path
from report_generator import ISEEReportGenerator

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the project root
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("⚠️  python-dotenv not installed, skipping .env file loading")
    pass

def test_report_generation(input_file: str, output_file: str = None, api_key: str = None):
    """Test report generation with existing ISEE results
    
    Args:
        input_file: Path to isee_result.md file
        output_file: Optional output path (defaults to input_dir/test_report.html)
        api_key: Optional API key (will prompt if not provided and not in env)
    """
    
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file does not exist: {input_file}")
        return False
    
    # Set default output file
    if output_file is None:
        output_path = input_path.parent / "test_report.html"
    else:
        # If output_file is a relative path, make it relative to current working directory
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
    
    # Get API key
    if api_key is None:
        api_key = os.getenv('OPENROUTER_API_KEY')
    
    if api_key is None:
        print("🔑 OpenRouter API key required for report generation.")
        print("Options:")
        print("1. Set OPENROUTER_API_KEY environment variable")
        print("2. Pass API key as argument")
        print("3. Enter it now (will not be saved)")
        print()
        
        # Check if we're in an interactive terminal
        try:
            if sys.stdin.isatty():
                api_key = input("Enter OpenRouter API key (or press Enter to test fallback): ").strip()
            else:
                print("⚠️  Non-interactive mode detected - using fallback generation only")
                api_key = ""
        except (EOFError, KeyboardInterrupt):
            print("⚠️  Input interrupted - using fallback generation only")
            api_key = ""
            
        if not api_key:
            print("⚠️  No API key provided - testing fallback generation only")
    
    # Create report generator
    generator = ISEEReportGenerator(api_key if api_key else None)
    
    print(f"📖 Input file: {input_path}")
    print(f"📄 Output file: {output_path}")
    print(f"🔧 Prompt length: {len(generator.report_prompt)} characters")
    print(f"🔑 API key: {'✅ Provided' if api_key else '❌ Missing (will use fallback)'}")
    print()
    
    if api_key:
        print("🚀 Starting enhanced report generation...")
        
        # Test the main report generation
        result = generator.generate_report(
            str(input_path), 
            str(output_path)
        )
        
        if result["success"]:
            print(f"✅ Enhanced report generated successfully!")
            print(f"   📁 Output: {result['report_path']}")
            print(f"   📊 Report size: {result['report_size']} characters")
            print(f"   🤖 Model used: {result.get('successful_model', 'Unknown')}")
            print(f"   🕒 Generated: {result['generation_time']}")
            
            # Verify the file exists and has content
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   💾 File size: {file_size} bytes")
                
                # Quick validation
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "<!DOCTYPE html" in content and "</html>" in content:
                        print("   ✅ HTML structure validated")
                    else:
                        print("   ⚠️  HTML structure may be incomplete")
            
            return True
            
        else:
            print(f"❌ Enhanced report generation failed: {result['error']}")
            
            if result.get("fallback_available"):
                print("🔄 Attempting fallback generation...")
                fallback_result = generator.generate_fallback_report(str(input_path), str(output_path))
                
                if fallback_result["success"]:
                    print(f"✅ Fallback report generated successfully!")
                    print(f"   📁 Output: {fallback_result['report_path']}")
                    print(f"   ⚠️  Note: This is a basic HTML conversion, not the enhanced report")
                    return True
                else:
                    print(f"❌ Fallback generation also failed: {fallback_result['error']}")
                    return False
            else:
                return False
    
    else:
        print("🔄 Testing fallback generation (no API key provided)...")
        
        # Test fallback generation
        fallback_result = generator.generate_fallback_report(str(input_path), str(output_path))
        
        if fallback_result["success"]:
            print(f"✅ Fallback report generated successfully!")
            print(f"   📁 Output: {fallback_result['report_path']}")
            print(f"   📊 File type: Basic HTML conversion")
            print(f"   ⚠️  Note: This is not the enhanced report (requires API key)")
            return True
        else:
            print(f"❌ Fallback generation failed: {fallback_result['error']}")
            return False

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python test_report_generation.py <path_to_isee_result.md> [output_path] [api_key]")
        print()
        print("Examples:")
        print("  python test_report_generation.py data/output/run_20250711_231747/isee_result.md")
        print("  python test_report_generation.py data/output/run_20250711_231747/isee_result.md my_test_report.html")
        print()
        print("API Key Options:")
        print("  1. Set OPENROUTER_API_KEY environment variable")
        print("  2. Pass as third argument")
        print("  3. Enter when prompted")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    
    print("🧪 ISEE Report Generation Test")
    print("=" * 50)
    
    success = test_report_generation(input_file, output_file, api_key)
    
    print()
    if success:
        print("🎉 Test completed successfully!")
        if output_file:
            print(f"🌐 Open {output_file} in your browser to view the generated report")
    else:
        print("💥 Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()