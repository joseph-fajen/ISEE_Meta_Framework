# Globant Enterprise AI Setup Guide

Complete setup guide for getting started with Globant's Enterprise AI API, based on the proven ISEE Meta Framework implementation.

## 🎯 Quick Start

1. **Get your Globant credentials**
2. **Set up environment variables** 
3. **Install dependencies**
4. **Run your first API call**

## 📋 Prerequisites

- Python 3.7 or higher
- Valid Globant Enterprise AI account
- `requests` library (`pip install requests`)

## 🔑 Step 1: Obtain Globant Credentials

You'll need two pieces of information from Globant:

1. **API Key** - Your unique authentication token
2. **Organization ID** - Your organization's unique identifier

Contact your Globant representative or check your Enterprise AI dashboard for these credentials.

## ⚙️ Step 2: Environment Setup

### Option A: Using .env File (Recommended)

Create a `.env` file in your project root:

```bash
# Globant Enterprise AI Credentials
GLOBANT_API_KEY=your_globant_api_key_here
GLOBANT_ORG_ID=your_organization_id_here
GLOBANT_BASE_URL=https://api.saia.ai

# Optional: Python-dotenv for loading .env files
# pip install python-dotenv
```

### Option B: System Environment Variables

**Linux/Mac:**
```bash
export GLOBANT_API_KEY="your_globant_api_key_here"
export GLOBANT_ORG_ID="your_organization_id_here" 
export GLOBANT_BASE_URL="https://api.saia.ai"
```

**Windows:**
```cmd
set GLOBANT_API_KEY=your_globant_api_key_here
set GLOBANT_ORG_ID=your_organization_id_here
set GLOBANT_BASE_URL=https://api.saia.ai
```

## 📦 Step 3: Install Dependencies

### Basic Setup
```bash
pip install requests
```

### With Environment File Support
```bash
pip install requests python-dotenv
```

### For Development
```bash
pip install requests python-dotenv pytest
```

## 🧪 Step 4: Test Your Setup

Create a simple test file `test_globant.py`:

```python
#!/usr/bin/env python3
import os
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed

def test_globant_connection():
    """Test basic Globant API connectivity."""
    
    # Get credentials
    api_key = os.getenv("GLOBANT_API_KEY")
    org_id = os.getenv("GLOBANT_ORG_ID")
    base_url = os.getenv("GLOBANT_BASE_URL", "https://api.saia.ai")
    
    if not api_key or not org_id:
        print("❌ Missing credentials. Check GLOBANT_API_KEY and GLOBANT_ORG_ID")
        return False
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Organization-ID": org_id
    }
    
    payload = {
        "model": "anthropic/claude-3-5-haiku-20241022",
        "messages": [{"role": "user", "content": "Hello! This is a test."}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            print(f"✅ Connection successful!")
            print(f"✅ Response: {message}")
            return True
        else:
            print(f"❌ API call failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_globant_connection()
```

Run the test:
```bash
python test_globant.py
```

## 🔧 Critical Configuration Notes

### ✅ Correct API Endpoint
- **Base URL**: `https://api.saia.ai` 
- **Chat Endpoint**: `/chat/completions` (NOT `/v1/chat/completions`)
- **Full URL**: `https://api.saia.ai/chat/completions`

### ✅ Required Headers
```python
headers = {
    "Authorization": f"Bearer {your_api_key}",
    "Content-Type": "application/json",
    "X-Organization-ID": your_org_id  # CRITICAL: This header is required!
}
```

### ✅ Model Format Requirements
Models MUST be in `provider/model` format:

```python
# ✅ Correct formats:
"anthropic/claude-3-5-haiku-20241022"
"openai/gpt-4o-mini"
"vertex_ai/gemini-2.5-pro"
"azure/gpt-4.1"

# ❌ Incorrect formats (will fail):
"claude-3-5-haiku-20241022"
"gpt-4o-mini" 
"gemini-2.5-pro"
```

## 🚨 Common Issues & Solutions

### Issue: "Invalid model name" Error (HTTP 400)
**Cause**: Model not in `provider/model` format  
**Solution**: Use format like `"anthropic/claude-3-5-haiku-20241022"`

### Issue: Authentication Failed (HTTP 401/403) 
**Cause**: Missing or incorrect credentials  
**Solution**: Verify `GLOBANT_API_KEY` and `GLOBANT_ORG_ID`

### Issue: "X-Organization-ID header is required"
**Cause**: Missing organization header  
**Solution**: Include `"X-Organization-ID": org_id` in headers

### Issue: Connection Timeout
**Cause**: Network issues or wrong base URL  
**Solution**: Verify `GLOBANT_BASE_URL=https://api.saia.ai`

## 📊 Environment Template

Complete `.env` template for your project:

```bash
# ===========================================
# Globant Enterprise AI Configuration
# ===========================================

# Required Credentials (get these from Globant)
GLOBANT_API_KEY=your_globant_api_key_here
GLOBANT_ORG_ID=your_organization_id_here

# API Configuration (use these exact values)
GLOBANT_BASE_URL=https://api.saia.ai

# Optional Settings
GLOBANT_TIMEOUT=120
GLOBANT_MAX_RETRIES=3
GLOBANT_DEFAULT_MAX_TOKENS=1024
GLOBANT_DEFAULT_TEMPERATURE=0.7

# ===========================================
# Development Settings
# ===========================================

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Rate Limiting (requests per second)
GLOBANT_RATE_LIMIT=10
```

## 🔗 Documentation References

Based on the ISEE implementation, these sources were invaluable:

- **Official Wiki**: https://wiki.genexus.com/enterprise-ai/wiki?20
- **GitHub Repository**: https://github.com/genexuslabs/saia-ingest
- **Supported Models**: https://wiki.genexus.com/enterprise-ai/wiki?200,Supported+Chat+Models
- **🆕 Reasoning Models Guide**: https://docs.globant.ai/en/wiki?1168,LLMs+with+Reasoning+Capabilities

## ✅ Next Steps

1. **Test your setup** with the provided test script
2. **Review the model reference** for available models
3. **Check out the example scripts** for implementation patterns
4. **Set up error handling** following the troubleshooting guide

Your setup should now be ready for production use with Globant's Enterprise AI platform!