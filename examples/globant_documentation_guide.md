# Globant Enterprise AI Documentation Guide

Complete reference to documentation sources and technical discoveries that enabled successful Globant API integration in the ISEE Meta Framework.

## 📚 Official Documentation Sources

### Primary Resources (Discovered During ISEE Development)

#### **1. GenexusLabs SAIA Ingest Repository**
- **URL**: https://github.com/genexuslabs/saia-ingest
- **Type**: Official GitHub repository
- **Content**: 
  - Complete API implementation examples
  - Authentication patterns and headers
  - Model format specifications
  - Request/response structures
- **Key Insights**: 
  - Confirmed `https://api.saia.ai` as correct base URL
  - Showed `X-Organization-ID` header requirement
  - Demonstrated `provider/model` format requirement

#### **2. Official Enterprise AI Wiki** 
- **URL**: https://wiki.genexus.com/enterprise-ai/wiki?20
- **Type**: Comprehensive technical documentation
- **Content**:
  - API endpoints and authentication
  - Model capabilities and limitations
  - Enterprise features and compliance
  - Billing and quota information
- **Key Insights**:
  - Enterprise vs consumer API differences
  - Organization-level access controls
  - Advanced model configurations

#### **3. Supported Models Documentation**
- **URL**: https://wiki.genexus.com/enterprise-ai/wiki?200,Supported+Chat+Models
- **Type**: Complete model catalog
- **Content**:
  - All available model identifiers
  - Provider-specific model formats
  - Capability descriptions
  - Cost tiers and performance metrics
- **Key Insights**:
  - Exact model naming conventions
  - Provider prefix requirements
  - Model availability by organization

#### **4. Reasoning Models Guide (🆕 New Resource)**
- **URL**: https://docs.globant.ai/en/wiki?1168,LLMs+with+Reasoning+Capabilities
- **Type**: Specialized reasoning models documentation
- **Content**:
  - `reasoning_effort` parameter specifications
  - Reasoning effort levels: "low", "medium", "high"
  - Performance and cost implications
  - Usage examples for o-series models
- **Key Insights**:
  - Explicit control over internal reasoning depth
  - Cost optimization through reasoning effort selection
  - Available since version 2025-04

## 🔍 Critical Technical Discoveries

### API Endpoint Configuration (Learned Through Testing)

```python
# ✅ CORRECT Configuration (discovered through debugging)
base_url = "https://api.saia.ai"
endpoint = "/chat/completions"  # NOT /v1/chat/completions
full_url = "https://api.saia.ai/chat/completions"

# ❌ INCORRECT (initial assumptions that failed)
# base_url = "https://console.saia.ai/tokens"  # Wrong - this is console UI
# endpoint = "/v1/chat/completions"            # Wrong - missing v1
# endpoint = "/api/v1/chat/completions"        # Wrong - extra api prefix
```

### Authentication Headers (Critical Discovery)

```python
# ✅ REQUIRED Headers (both are mandatory!)
headers = {
    "Authorization": f"Bearer {api_key}",        # Standard OAuth-style auth
    "Content-Type": "application/json",          # Standard for JSON APIs
    "X-Organization-ID": organization_id         # CRITICAL: Globant-specific requirement
}

# ❌ INSUFFICIENT (missing org header causes 400/401 errors)
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    # Missing X-Organization-ID will cause failure
}
```

### Model Format Requirements (Major Discovery)

```python
# ✅ REQUIRED Format: provider/model 
"anthropic/claude-3-5-haiku-20241022"  # Correct
"openai/gpt-4o-mini"                   # Correct
"vertex_ai/gemini-2.5-pro"            # Correct
"azure/gpt-4.1"                       # Correct

# ❌ FAILS: Bare model names return 400 error
"claude-3-5-haiku-20241022"            # Missing provider prefix
"gpt-4o-mini"                          # Missing provider prefix
"gemini-2.5-pro"                       # Missing provider prefix

# Error message for incorrect format:
# "Invalid 'model' name. Must follow pattern {provider}/{modelName}"
```

## 🛠️ Implementation Patterns from ISEE

### Basic API Call Structure

```python
import requests
import os

def make_globant_call(prompt: str, model: str) -> str:
    """
    Proven working pattern from ISEE implementation.
    """
    # Credentials from environment
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID")
    
    # Correct endpoint and headers
    url = "https://api.saia.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Organization-ID": org_id
    }
    
    # OpenAI-compatible payload
    payload = {
        "model": model,  # Must be in provider/model format
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")
```

### Environment Variable Configuration

Based on successful ISEE deployment:

```bash
# Required for Globant API access
GLOBANT_API_KEY=your_globant_api_key_here
GLOBANT_ORG_ID=your_organization_id_here
GLOBANT_BASE_URL=https://api.saia.ai  # Use this exact URL

# Optional but recommended
GLOBANT_TIMEOUT=120
GLOBANT_MAX_RETRIES=3
```

## 📋 Debugging Methodology (From ISEE Experience)

### Common Error Patterns and Solutions

#### 1. **HTTP 400 - Invalid Model Name**
```
Error: "Invalid 'model' name. Must follow pattern {provider}/{modelName}"

❌ Problem: Using bare model name
   model = "claude-3-5-haiku-20241022"

✅ Solution: Add provider prefix  
   model = "anthropic/claude-3-5-haiku-20241022"
```

#### 2. **HTTP 401/403 - Authentication Issues**
```
❌ Problem: Missing or incorrect credentials
   - Wrong API key
   - Missing X-Organization-ID header
   - Incorrect organization ID

✅ Solution: Verify both credentials
   headers = {
       "Authorization": f"Bearer {correct_api_key}",
       "X-Organization-ID": correct_org_id
   }
```

#### 3. **HTTP 404 - Wrong Endpoint**
```
❌ Problem: Using wrong base URL or endpoint
   "https://console.saia.ai/tokens/chat/completions"    # Wrong
   "https://api.saia.ai/v1/chat/completions"            # Wrong

✅ Solution: Use correct endpoint
   "https://api.saia.ai/chat/completions"               # Correct
```

#### 4. **Connection Timeouts**
```
❌ Problem: Network configuration or firewall blocking

✅ Solutions:
   - Verify internet connectivity to api.saia.ai
   - Check firewall/proxy settings
   - Increase timeout values (use 120+ seconds)
   - Test with curl: curl -I https://api.saia.ai
```

### Diagnostic Tools

#### Test API Connectivity
```bash
# Basic connectivity test
curl -I https://api.saia.ai

# Full API test (replace with your credentials)
curl -X POST https://api.saia.ai/chat/completions \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -H "X-Organization-ID: your_org_id" \
  -d '{
    "model": "anthropic/claude-3-5-haiku-20241022",
    "messages": [{"role": "user", "content": "Test"}],
    "max_tokens": 50
  }'
```

#### Python Diagnostic Script
```python
def diagnose_globant_setup():
    """Diagnostic tool based on ISEE debugging process."""
    
    import os
    import requests
    
    print("Globant API Diagnostic")
    print("=" * 22)
    
    # Check environment variables
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID")
    base_url = os.getenv("GLOBANT_BASE_URL", "https://api.saia.ai")
    
    # Environment check
    if not api_key:
        print("❌ GLOBANT_API_KEY not set")
        return False
    if not org_id:
        print("❌ GLOBANT_ORG_ID not set") 
        return False
    if base_url != "https://api.saia.ai":
        print(f"⚠️  Base URL is '{base_url}', should be 'https://api.saia.ai'")
    
    print("✅ Environment variables configured")
    
    # Test connectivity
    try:
        response = requests.get("https://api.saia.ai", timeout=10)
        print("✅ Can reach api.saia.ai")
    except Exception as e:
        print(f"❌ Cannot reach api.saia.ai: {e}")
        return False
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Organization-ID": org_id
    }
    
    payload = {
        "model": "anthropic/claude-3-5-haiku-20241022",
        "messages": [{"role": "user", "content": "Test"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://api.saia.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API call successful")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False

# Run diagnostic
diagnose_globant_setup()
```

## 🔧 Advanced Configuration (From ISEE Implementation)

### Reasoning Model Parameters (🆕 Enhanced)

Special handling for OpenAI reasoning models (o1, o3, o4 series):

```python
def call_reasoning_model(prompt: str, model: str):
    """
    Special parameter handling for reasoning models.
    Based on ISEE implementation + new Globant documentation.
    """
    payload = {
        "model": model,  # e.g., "openai/o1", "openai/o3", "openai/o4-mini"
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 1024,  # Not "max_tokens"
        "reasoning_effort": "medium"     # Controls reasoning depth: "low", "medium", "high"
    }
    # Notes: 
    # - temperature parameter is not supported by reasoning models
    # - reasoning_effort controls internal computational resources
    # - higher effort = slower but more thorough reasoning
```

### Reasoning Effort Levels (New Discovery)

Based on the latest Globant documentation:

```python
# Reasoning effort options
"reasoning_effort": "low"     # Fastest, minimal reasoning
"reasoning_effort": "medium"  # Balanced (recommended default)
"reasoning_effort": "high"    # Maximum depth, slowest but most thorough

# Usage example
response = client.generate(
    "Solve this complex math problem step by step...",
    "openai/o1",
    reasoning_effort="high",  # Use maximum reasoning for complex problems
    max_completion_tokens=500
)
```

### Rate Limiting and Retry Logic

```python
import time
from functools import wraps

def with_retry(max_attempts=3, delay=1):
    """
    Retry decorator with exponential backoff.
    Pattern from ISEE's robust error handling.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (2 ** attempt)
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

@with_retry(max_attempts=3)
def robust_api_call(prompt, model):
    # Your API call implementation
    pass
```

## 📖 Additional Resources

### Official Globant Support
- **Support Portal**: Contact through official Globant channels
- **Enterprise Support**: Available for organization administrators
- **Billing Questions**: Direct to Globant enterprise team

### Community Resources
- **GitHub Issues**: https://github.com/genexuslabs/saia-ingest/issues
- **Developer Forums**: Check GenexusLabs community resources

### ISEE Framework Integration
- **Complete Implementation**: See `model_api_integration.py:870-1065` in ISEE codebase
- **Working Configuration**: `globant_enterprise_config.json` for 15-model setup
- **Test Suite**: `tests/test_globant_integration.py` for comprehensive testing

## 🎯 Quick Reference Checklist

When implementing Globant API access, verify:

- [ ] **Base URL**: `https://api.saia.ai`
- [ ] **Endpoint**: `/chat/completions` (no `/v1/`)
- [ ] **API Key**: Valid `GLOBANT_API_KEY`
- [ ] **Organization**: Valid `GLOBANT_ORG_ID`
- [ ] **Headers**: Both `Authorization` and `X-Organization-ID`
- [ ] **Model Format**: `provider/model` (not bare model names)
- [ ] **Timeout**: At least 60 seconds for API calls
- [ ] **Error Handling**: Proper retry logic for transient errors
- [ ] **Special Cases**: Different parameters for reasoning models (o1, o3, o4)
- [ ] **Reasoning Control**: Use `reasoning_effort` parameter for reasoning models

Following this checklist and using the documented patterns should result in successful Globant API integration, as proven by the ISEE Meta Framework implementation.