# Globant Enterprise AI Models Reference

Comprehensive reference of available models through Globant's Enterprise AI platform, based on the proven 15-model configuration from ISEE Meta Framework.

## 🎯 Quick Reference

All Globant models must use the `provider/model` format. Here are the most popular and reliable options:

| Model | Provider Format | Use Case | Cost Tier |
|-------|----------------|----------|-----------|
| Claude Sonnet 4 | `anthropic/claude-sonnet-4-20250514` | Advanced reasoning, complex problems | Premium+ |
| Claude 3.5 Haiku | `anthropic/claude-3-5-haiku-20241022` | Fast, cost-efficient responses | Standard |
| GPT-4o Mini | `openai/gpt-4o-mini` | Quick reasoning, high quality | Standard |
| GPT-4 Turbo | `azure/gpt-4.1` | Reliable performance, Azure-hosted | Premium |
| Gemini 2.5 Pro | `vertex_ai/gemini-2.5-pro` | Verification, multimodal tasks | Premium |

## 📋 Complete Model List

### 🧠 Claude Models (Anthropic)

#### **Claude Sonnet 4** - Frontier Reasoning
```python
model = "anthropic/claude-sonnet-4-20250514"
```
- **Capabilities**: Highest quality reasoning, complex problem solving
- **Best For**: Research, analysis, sophisticated tasks
- **Cost**: Premium+ 
- **Max Tokens**: 4096
- **Notes**: Latest frontier model with advanced capabilities

#### **Claude 3.5 Haiku** - Speed Champion  
```python
model = "anthropic/claude-3-5-haiku-20241022"
```
- **Capabilities**: Ultra-fast processing, cost-efficient
- **Best For**: Quick responses, high-volume tasks
- **Cost**: Standard
- **Max Tokens**: 4096
- **Notes**: Optimal balance of speed and quality

### 🤖 OpenAI Models

#### **GPT-4o Mini** - Efficiency Leader
```python
model = "openai/gpt-4o-mini"
```
- **Capabilities**: Fast reasoning, cost-optimized
- **Best For**: General tasks, development, testing  
- **Cost**: Standard
- **Max Tokens**: 4096
- **Notes**: Most cost-effective GPT-4 class model

#### **OpenAI o1** - Multi-Step Reasoning
```python
model = "openai/o1"
```
- **Capabilities**: Advanced multi-step thinking, complex reasoning
- **Best For**: Mathematical problems, logical analysis
- **Cost**: Premium+
- **Max Tokens**: 4096 (use `max_completion_tokens`)
- **Reasoning Control**: `reasoning_effort` parameter ("low", "medium", "high")
- **Notes**: No temperature control, optimizes internal reasoning process

#### **OpenAI o3** - Research Synthesis
```python
model = "openai/o3"
```
- **Capabilities**: Research synthesis, information integration
- **Best For**: Academic research, comprehensive analysis
- **Cost**: Premium+
- **Max Tokens**: 4096 (use `max_completion_tokens`)
- **Reasoning Control**: `reasoning_effort` parameter ("low", "medium", "high")
- **Notes**: Latest o-series model with advanced reasoning capabilities

#### **OpenAI o3-mini** - Analytical Precision
```python
model = "openai/o3-mini"
```
- **Capabilities**: Technical competence, analytical excellence
- **Best For**: Problem-solving, technical analysis
- **Cost**: Premium+
- **Max Tokens**: 4096 (use `max_completion_tokens`)
- **Reasoning Control**: `reasoning_effort` parameter ("low", "medium", "high")
- **Notes**: Compact o-series with focused reasoning capabilities

### 🌐 Google Models

#### **Gemini 2.5 Pro** - Verification Master
```python
model = "vertex_ai/gemini-2.5-pro"
```
- **Capabilities**: Fact-checking, multimodal, verification
- **Best For**: Data validation, alternate perspectives
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: Excellent for verification tasks

### 🏢 Microsoft Azure Models

#### **GPT-4 Turbo (Azure)** - Reliable Workhorse
```python
model = "azure/gpt-4.1"
```
- **Capabilities**: Dependable performance, enterprise-grade
- **Best For**: Business applications, reliable workflows
- **Cost**: Premium  
- **Max Tokens**: 4000
- **Notes**: Azure-hosted for enterprise compliance

#### **Grok 3 Mini (Azure AI Foundry)** - Contrarian Thinking
```python
model = "azure_ai_foundry/grok-3-mini"
```
- **Capabilities**: Unconventional thinking, contrarian perspectives
- **Best For**: Challenging assumptions, alternative viewpoints
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: Experimental platform access

### 🚀 AWS Bedrock Models

#### **Claude 3.5 Haiku (Bedrock)** - AWS Speed Demon
```python
model = "awsbedrock/anthropic.claude-3.5-haiku"
```
- **Capabilities**: Ultra-fast, AWS-hosted
- **Best For**: High-throughput applications
- **Cost**: Standard
- **Max Tokens**: 4096
- **Notes**: AWS-hosted Anthropic model

#### **DeepSeek Chat V3** - Mathematical Reasoning
```python
model = "awsbedrock/us.deepseek.r1-v1:0"
```
- **Capabilities**: Mathematical reasoning, logical analysis
- **Best For**: STEM problems, analytical tasks
- **Cost**: Budget
- **Max Tokens**: 4096
- **Notes**: Chinese AI with strong mathematical capabilities

#### **Llama 3.1 405B** - Massive Scale Reasoning
```python
model = "awsbedrock/meta.llama3-1-405b"
```
- **Capabilities**: Massive parameter processing, commercial logic
- **Best For**: Complex business reasoning, large-scale problems
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: Open-source architecture, commercial-focused

#### **Amazon Nova Pro** - AWS Proprietary
```python
model = "awsbedrock/amazon.nova-pro-v1:0"
```
- **Capabilities**: AWS proprietary reasoning, novel architecture
- **Best For**: AWS ecosystem integration, specialized tasks
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: Amazon's proprietary model

### 🔄 Other Providers

#### **Grok 4** - Advanced Contrarian
```python
model = "xai/grok-4"
```
- **Capabilities**: Advanced contrarian perspectives, latest generation
- **Best For**: Challenging orthodoxy, alternative analysis
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: X.AI's latest model

#### **Cohere Command-A 2025** - Ensemble Reasoning
```python
model = "cohere/command-a-03-2025"
```
- **Capabilities**: Ensemble reasoning, business logic, multi-perspective
- **Best For**: Business strategy, comprehensive analysis
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: Enterprise-focused reasoning

#### **Mistral Large** - European Strategy
```python
model = "vertex_ai/mistral-large-2411"
```
- **Capabilities**: European reasoning, commercial strategy, multilingual
- **Best For**: International business, European perspectives
- **Cost**: Premium
- **Max Tokens**: 4096
- **Notes**: European AI with business focus

## 🎛️ Model Selection Guide

### For Speed & Cost Efficiency
1. `openai/gpt-4o-mini` - Best overall value
2. `anthropic/claude-3-5-haiku-20241022` - Anthropic speed
3. `awsbedrock/us.deepseek.r1-v1:0` - Budget option

### For Advanced Reasoning
1. `anthropic/claude-sonnet-4-20250514` - Frontier capabilities
2. `openai/o1` - Multi-step reasoning
3. `openai/o3` - Research synthesis

### For Business Applications
1. `azure/gpt-4.1` - Reliable enterprise
2. `cohere/command-a-03-2025` - Business strategy
3. `awsbedrock/meta.llama3-1-405b` - Commercial logic

### For Creative & Alternative Thinking
1. `xai/grok-4` - Advanced contrarian
2. `azure_ai_foundry/grok-3-mini` - Unconventional
3. `vertex_ai/gemini-2.5-pro` - Alternative perspectives

## ⚙️ Special Parameter Requirements

### Reasoning Models (o1, o3, o3-mini, o4 series)
```python
# Standard models
payload = {
    "model": "openai/gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1024
}

# Reasoning models (different parameters)
payload = {
    "model": "openai/o1",
    "max_completion_tokens": 1024,  # Not max_tokens
    "reasoning_effort": "high"       # Controls internal reasoning depth
    # No temperature parameter supported
}
```

### Reasoning Effort Parameter (New Discovery)
Based on latest Globant documentation, reasoning models support explicit control:

```python
# Reasoning effort levels
"reasoning_effort": "low"     # Fastest, minimal reasoning
"reasoning_effort": "medium"  # Balanced reasoning (recommended default)  
"reasoning_effort": "high"    # Maximum reasoning depth, slowest but most thorough
```

**Impact**: 
- **Low**: Quick responses, basic reasoning
- **Medium**: Good balance of speed and reasoning quality  
- **High**: Deep analysis, slower but more comprehensive reasoning

**Cost**: Higher reasoning effort uses more tokens and increases cost

### Provider-Specific Notes

**AWS Bedrock Models:**
- Use full model ARN format (e.g., `awsbedrock/us.deepseek.r1-v1:0`)
- May have different parameter requirements

**Azure Models:**
- Azure-hosted for compliance and reliability
- May have enhanced enterprise features

**Vertex AI Models:**
- Google Cloud hosted
- Enhanced integration with Google services

## 🔍 Model Testing Script

```python
#!/usr/bin/env python3
"""Test different Globant models to find the best fit for your use case."""

import os
import requests
import time

def test_model(model_name, prompt="What is artificial intelligence?"):
    """Test a specific model with a sample prompt."""
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GLOBANT_API_KEY')}",
        "Content-Type": "application/json",
        "X-Organization-ID": os.getenv('GLOBANT_ORG_ID')
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # Special handling for reasoning models (o1, o3, o4 series)
    if any(series in model_name for series in ["o1", "o3", "o4"]):
        payload.pop("temperature")  # Not supported
        payload["max_completion_tokens"] = payload.pop("max_tokens")
        payload["reasoning_effort"] = "medium"  # Default reasoning level
    
    try:
        start_time = time.time()
        response = requests.post(
            "https://api.saia.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            response_time = end_time - start_time
            
            print(f"✅ {model_name}")
            print(f"   Response time: {response_time:.2f}s")
            print(f"   Preview: {content[:100]}...")
            print()
            return True
        else:
            print(f"❌ {model_name}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {model_name}: {str(e)}")
        return False

# Test popular models
test_models = [
    "anthropic/claude-3-5-haiku-20241022",
    "openai/gpt-4o-mini", 
    "vertex_ai/gemini-2.5-pro",
    "anthropic/claude-sonnet-4-20250514",
    "openai/o1"
]

if __name__ == "__main__":
    print("Testing Globant Models...")
    print("=" * 30)
    
    for model in test_models:
        test_model(model)
        time.sleep(1)  # Rate limiting
```

## 📚 Additional Resources

- **Official Documentation**: https://wiki.genexus.com/enterprise-ai/wiki?200,Supported+Chat+Models
- **Model Capabilities**: Each model's specific strengths and use cases
- **Cost Information**: Contact Globant for detailed pricing
- **Rate Limits**: Vary by model and organization tier

Choose models based on your specific needs: speed, cost, reasoning capability, or specialized features like multimodal support or contrarian thinking.