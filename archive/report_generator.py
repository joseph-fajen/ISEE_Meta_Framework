"""
ISEE Report Generator

Transforms raw ISEE results into polished, professional HTML reports for web display.
Takes isee_result.md files and generates comprehensive web-ready analysis reports.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import re

class ISEEReportGenerator:
    """Service for generating polished HTML reports from ISEE results"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        """Initialize the report generator
        
        Args:
            openrouter_api_key: OpenRouter API key for Claude access. If None, will look for env var.
        """
        self.api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        self.logger = logging.getLogger(__name__)
        
        # Load report generation prompt from external file
        self.report_prompt = self._load_report_prompt()

    def _load_report_prompt(self) -> str:
        """Load the report generation prompt from external file
        
        Returns:
            str: The prompt content, or a fallback prompt if file loading fails
        """
        # Define paths to check for prompt files
        current_dir = Path(__file__).parent
        prompt_paths = [
            current_dir / "prompts" / "report_generation.txt",  # New simplified prompt
            current_dir / "prompts" / "report_generation_original.txt",  # Original backup
        ]
        
        # Try to load from files in order of preference
        for prompt_path in prompt_paths:
            try:
                if prompt_path.exists():
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            self.logger.info(f"Loaded report generation prompt from: {prompt_path}")
                            return content
            except Exception as e:
                self.logger.warning(f"Failed to load prompt from {prompt_path}: {e}")
                continue
        
        # Fallback prompt if all file loading fails
        self.logger.warning("Could not load prompt from any external file, using minimal fallback")
        return """Transform the ISEE results into a professional HTML report.

Structure the report with:
1. Executive Summary
2. Key Findings
3. Strategic Recommendations  
4. Implementation Roadmap
5. Methodology Notes

Use clean HTML with professional typography and clear section headings.
Focus on actionable insights and practical value for users."""

    def generate_report(self, isee_result_path: str, output_path: str, 
                       execution_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a polished HTML report from ISEE results
        
        Args:
            isee_result_path: Path to the isee_result.md file
            output_path: Path where the HTML report should be saved
            execution_metadata: Optional metadata about the execution (timing, parameters, etc.)
            
        Returns:
            Dict with generation status and details
        """
        try:
            # Read the ISEE results file
            if not os.path.exists(isee_result_path):
                raise FileNotFoundError(f"ISEE results file not found: {isee_result_path}")
                
            with open(isee_result_path, 'r', encoding='utf-8') as f:
                isee_content = f.read()
            
            # Validate we have an API key
            if not self.api_key:
                self.logger.error("No OpenRouter API key available for report generation")
                return {
                    "success": False,
                    "error": "API key not configured",
                    "fallback_available": True
                }
            
            # Extract query from the content if possible
            query = self._extract_query_from_content(isee_content)
            
            # Build the complete prompt with the ISEE content
            full_prompt = f"""{self.report_prompt}

---

## ISEE Results to Transform

The following is the raw ISEE results markdown file that needs to be transformed into a polished HTML report:

```markdown
{isee_content}
```

---

**Task**: Transform the above ISEE results into a comprehensive, professional HTML report following all the guidelines and requirements specified above. The report should be ready for direct display in the ISEE web UI."""

            # Generate the report using fallback chain
            html_report, successful_model = self._generate_with_fallback_chain(full_prompt)
            
            if html_report:
                # Save the generated report
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_report)
                
                self.logger.info(f"Successfully generated HTML report: {output_path}")
                
                return {
                    "success": True,
                    "report_path": output_path,
                    "report_size": len(html_report),
                    "query_detected": query,
                    "generation_time": datetime.now().isoformat(),
                    "generation_method": "llm_fallback_chain",
                    "successful_model": successful_model
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate report content",
                    "fallback_available": True
                }
                
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_available": True
            }
    
    def _extract_query_from_content(self, content: str) -> Optional[str]:
        """Extract the original query from ISEE results content"""
        # Look for common patterns where the query appears
        patterns = [
            r"The query was: (.+?)(?:\n|$)",
            r"Query: (.+?)(?:\n|$)",
            r"Original Query: (.+?)(?:\n|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _generate_with_fallback_chain(self, prompt: str) -> tuple[Optional[str], Optional[str]]:
        """Generate report using fallback chain: Claude 3.5 Sonnet → GPT-4o → Claude 3.5 Haiku
        
        Returns:
            tuple: (generated_content, successful_model_name)
        """
        
        # Define the fallback chain with model configs
        fallback_models = [
            {
                "name": "Claude 3.5 Sonnet",
                "model": "anthropic/claude-3-5-sonnet",
                "max_tokens": 8000,
                "temperature": 0.7,
                "timeout": 90
            },
            {
                "name": "GPT-4o", 
                "model": "openai/gpt-4o",
                "max_tokens": 8000,
                "temperature": 0.7,
                "timeout": 60
            },
            {
                "name": "Claude 3.5 Haiku",
                "model": "anthropic/claude-3-5-haiku",
                "max_tokens": 8000,
                "temperature": 0.7,
                "timeout": 45
            }
        ]
        
        for i, model_config in enumerate(fallback_models):
            try:
                self.logger.info(f"Attempting report generation with {model_config['name']} (attempt {i+1}/{len(fallback_models)})")
                
                result = self._call_openrouter_model(prompt, model_config)
                
                if result:
                    self.logger.info(f"Successfully generated report with {model_config['name']}")
                    return result, model_config['name']
                else:
                    self.logger.warning(f"Report generation failed with {model_config['name']}, trying next model...")
                    
            except Exception as e:
                self.logger.error(f"Error with {model_config['name']}: {e}")
                if i < len(fallback_models) - 1:
                    self.logger.info(f"Falling back to next model...")
                continue
        
        self.logger.error("All models in fallback chain failed")
        return None, None
    
    def _call_openrouter_model(self, prompt: str, model_config: Dict[str, Any]) -> Optional[str]:
        """Call a specific OpenRouter model with given configuration"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://isee-meta-framework.local",
                "X-Title": "ISEE Meta Framework"
            }
            
            data = {
                "model": model_config["model"],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": model_config["max_tokens"],
                "temperature": model_config["temperature"]
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=model_config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract HTML from markdown code blocks if present
                content = self._extract_html_from_response(content)
                
                # Basic validation that we got HTML content
                if "<html" in content.lower() and "</html>" in content.lower():
                    return content
                else:
                    self.logger.warning(f"Model {model_config['name']} returned content that doesn't appear to be HTML")
                    return content  # Return anyway, might still be usable
            else:
                self.logger.error(f"OpenRouter API error for {model_config['name']}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling {model_config['name']}: {e}")
            return None
    
    def _extract_html_from_response(self, content: str) -> str:
        """Extract HTML content from LLM response, handling markdown code blocks"""
        # Check if content is wrapped in markdown code blocks
        html_block_patterns = [
            r'```html\n(.*?)```',
            r'```\n(.*?)```',
            r'`html\n(.*?)`',
        ]
        
        for pattern in html_block_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                extracted_html = match.group(1).strip()
                # Validate it looks like HTML
                if "<html" in extracted_html.lower() and "</html>" in extracted_html.lower():
                    self.logger.info("Successfully extracted HTML from markdown code block")
                    return extracted_html
        
        # If no code blocks found, check if the content itself is HTML
        if "<html" in content.lower() and "</html>" in content.lower():
            return content
        
        # If content starts with conversational text but has HTML, try to extract just the HTML
        html_start = content.lower().find('<!doctype html')
        if html_start == -1:
            html_start = content.lower().find('<html')
        
        if html_start != -1:
            html_end = content.lower().rfind('</html>') + 7
            if html_end > html_start:
                extracted_html = content[html_start:html_end]
                self.logger.info("Successfully extracted HTML from conversational response")
                return extracted_html
        
        # Return original content if no extraction possible
        return content
    
    def generate_fallback_report(self, isee_result_path: str, output_path: str) -> Dict[str, Any]:
        """Generate a basic HTML version of the markdown for fallback"""
        try:
            with open(isee_result_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic markdown to HTML conversion
            html_content = self._basic_markdown_to_html(content)
            
            # Wrap in basic HTML structure
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISEE Analysis Results</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #5d6d7e; }}
        .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .fallback-notice {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="fallback-notice">
        <strong>Note:</strong> This is a basic rendering of the ISEE results. Enhanced report generation was not available.
    </div>
    {html_content}
</body>
</html>"""
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            return {
                "success": True,
                "report_path": output_path,
                "is_fallback": True,
                "generation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating fallback report: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_fallback": True
            }
    
    def _basic_markdown_to_html(self, markdown_content: str) -> str:
        """Basic markdown to HTML conversion for fallback"""
        html = markdown_content
        
        # Convert headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Convert bold text
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert paragraphs
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for i, p in enumerate(paragraphs):
            p = p.strip()
            if p and not p.startswith('<h') and not p.startswith('---'):
                if p.startswith('- '):
                    # Simple list handling
                    if not html_paragraphs or not html_paragraphs[-1].endswith('</ul>'):
                        html_paragraphs.append('<ul>')
                    html_paragraphs.append(f'<li>{p[2:]}</li>')
                    # Check if next paragraph is also a list item
                    is_last_item = (i == len(paragraphs) - 1) or (i + 1 < len(paragraphs) and not paragraphs[i + 1].strip().startswith('- '))
                    if is_last_item:
                        html_paragraphs.append('</ul>')
                else:
                    html_paragraphs.append(f'<p>{p}</p>')
            elif p.startswith('---'):
                html_paragraphs.append('<hr>')
            else:
                html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)


def create_report_generator(api_key: Optional[str] = None) -> ISEEReportGenerator:
    """Factory function to create report generator instance"""
    return ISEEReportGenerator(api_key)


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python report_generator.py <isee_result.md> <output.html> [api_key]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    
    generator = ISEEReportGenerator(api_key)
    result = generator.generate_report(input_file, output_file)
    
    if result["success"]:
        print(f"✅ Report generated successfully: {result['report_path']}")
    else:
        print(f"❌ Report generation failed: {result['error']}")
        if result.get("fallback_available"):
            print("🔄 Attempting fallback generation...")
            fallback_result = generator.generate_fallback_report(input_file, output_file)
            if fallback_result["success"]:
                print(f"✅ Fallback report generated: {fallback_result['report_path']}")
            else:
                print(f"❌ Fallback generation also failed: {fallback_result['error']}")