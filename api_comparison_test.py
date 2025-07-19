#!/usr/bin/env python3
"""
API Comparison Test: OpenRouter vs Direct OpenAI API
Test to identify if OpenRouter is causing performance issues with premium models
"""

import os
import json
import time
import requests
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIComparisonTest:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    def test_openrouter_call(self, model: str, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Test OpenRouter API call"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://isee-meta-framework.local",
            "X-Title": "ISEE Meta Framework API Test"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                metadata = {
                    'success': True,
                    'execution_time': execution_time,
                    'response_length': len(content),
                    'status_code': response.status_code,
                    'usage': result.get('usage', {}),
                    'model': result.get('model', model)
                }
                return content, metadata
            else:
                error_content = f"Error {response.status_code}: {response.text}"
                metadata = {
                    'success': False,
                    'execution_time': execution_time,
                    'response_length': len(error_content),
                    'status_code': response.status_code,
                    'error': response.text
                }
                return error_content, metadata
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_content = f"Exception: {str(e)}"
            metadata = {
                'success': False,
                'execution_time': execution_time,
                'response_length': len(error_content),
                'error': str(e)
            }
            return error_content, metadata
    
    def test_openai_direct_call(self, model: str, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Test direct OpenAI API call"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                metadata = {
                    'success': True,
                    'execution_time': execution_time,
                    'response_length': len(content),
                    'status_code': response.status_code,
                    'usage': result.get('usage', {}),
                    'model': result.get('model', model)
                }
                return content, metadata
            else:
                error_content = f"Error {response.status_code}: {response.text}"
                metadata = {
                    'success': False,
                    'execution_time': execution_time,
                    'response_length': len(error_content),
                    'status_code': response.status_code,
                    'error': response.text
                }
                return error_content, metadata
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_content = f"Exception: {str(e)}"
            metadata = {
                'success': False,
                'execution_time': execution_time,
                'response_length': len(error_content),
                'error': str(e)
            }
            return error_content, metadata
    
    def run_comparison_test(self, test_prompt: str = None) -> Dict[str, Any]:
        """Run comparison test between OpenRouter and direct OpenAI API"""
        
        if test_prompt is None:
            test_prompt = """Analyze the potential impact of quantum computing on blockchain security. 
            Consider both the threats quantum computers pose to current cryptographic methods 
            and potential quantum-resistant solutions. Provide a detailed analysis with specific 
            technical recommendations."""
        
        results = {
            'test_prompt': test_prompt,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {}
        }
        
        # Test configurations
        test_configs = [
            {
                'name': 'OpenAI o3 FULL via OpenRouter (After Key Added)',
                'method': 'openrouter',
                'model': 'openai/o3'
            },
            {
                'name': 'OpenAI o3-mini via OpenRouter',
                'method': 'openrouter',
                'model': 'openai/o3-mini'
            },
            {
                'name': 'GPT-4o via OpenRouter',
                'method': 'openrouter', 
                'model': 'openai/gpt-4o'
            }
        ]
        
        for config in test_configs:
            print(f"\nTesting: {config['name']}")
            
            if config['method'] == 'openrouter':
                if not self.openrouter_api_key:
                    print("  ❌ OpenRouter API key not found")
                    continue
                content, metadata = self.test_openrouter_call(config['model'], test_prompt)
                
            elif config['method'] == 'direct':
                if not self.openai_api_key:
                    print("  ❌ OpenAI API key not found")
                    continue
                content, metadata = self.test_openai_direct_call(config['model'], test_prompt)
            
            results['tests'][config['name']] = {
                'config': config,
                'content': content,
                'metadata': metadata
            }
            
            # Print summary
            if metadata['success']:
                print(f"  ✅ Success: {metadata['response_length']} chars in {metadata['execution_time']:.2f}s")
            else:
                print(f"  ❌ Failed: {metadata.get('error', 'Unknown error')}")
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"api_comparison_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {filename}")
        return filename

def main():
    """Main test function"""
    print("🔬 API Comparison Test: OpenRouter vs Direct OpenAI")
    print("=" * 60)
    
    # Check for API keys
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"OpenRouter API Key: {'✅ Found' if openrouter_key else '❌ Missing'}")
    print(f"OpenAI API Key: {'✅ Found' if openai_key else '❌ Missing'}")
    
    if not openrouter_key and not openai_key:
        print("\n❌ No API keys found. Please set OPENROUTER_API_KEY and/or OPENAI_API_KEY environment variables.")
        return
    
    # Run test
    tester = APIComparisonTest()
    results = tester.run_comparison_test()
    
    # Save results
    filename = tester.save_results(results)
    
    # Print analysis
    print("\n📊 Analysis Summary:")
    print("-" * 40)
    
    for test_name, test_data in results['tests'].items():
        metadata = test_data['metadata']
        if metadata['success']:
            print(f"{test_name:30} | {metadata['response_length']:5d} chars | {metadata['execution_time']:6.2f}s")
        else:
            print(f"{test_name:30} | ❌ FAILED")

if __name__ == "__main__":
    main()