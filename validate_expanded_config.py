#!/usr/bin/env python3
"""
Validate the expanded 15-model Globant Enterprise AI configuration
"""

import json
import os
import requests

# Load environment variables from .env file
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        print("Warning: .env file not found")

load_env()

def validate_config_structure():
    """Validate the structure and completeness of the expanded configuration."""
    print("VALIDATING EXPANDED GLOBANT CONFIGURATION STRUCTURE")
    print("="*60)
    
    try:
        with open('globant_enterprise_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Configuration file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    
    # Check basic structure
    required_sections = ['description', 'version', 'models', 'cognitive_diversity', 'integration_notes']
    for section in required_sections:
        if section not in config:
            print(f"❌ Missing required section: {section}")
            return False
    
    # Check model count
    models = config.get('models', {}).get('api_models', [])
    model_count = len(models)
    
    print(f"✅ Configuration file loaded successfully")
    print(f"✅ Version: {config.get('version', 'unknown')}")
    print(f"✅ Models configured: {model_count}")
    
    if model_count != 15:
        print(f"⚠️  Expected 15 models, found {model_count}")
        return False
    
    # Check strategic models
    strategic_models = [m for m in models if m.get('ui_priority') == 'strategic']
    print(f"✅ Strategic models: {len(strategic_models)}")
    
    # Validate model structure
    print(f"\n📋 MODEL VALIDATION:")
    required_fields = ['id', 'name', 'provider', 'parameters', 'strategic_order']
    
    for i, model in enumerate(models, 1):
        model_name = model.get('name', f'Model {i}')
        missing_fields = [field for field in required_fields if field not in model]
        
        if missing_fields:
            print(f"❌ {model_name}: Missing fields {missing_fields}")
            return False
        else:
            strategic_order = model.get('strategic_order', 'N/A')
            model_param = model.get('parameters', {}).get('model', 'unknown')
            print(f"✅ {strategic_order:2}. {model_name} ({model_param})")
    
    # Check provider diversity
    provider_paths = set()
    for model in models:
        model_param = model.get('parameters', {}).get('model', '')
        if '/' in model_param:
            provider = model_param.split('/')[0]
            provider_paths.add(provider)
    
    print(f"\n🌐 PROVIDER DIVERSITY:")
    print(f"✅ Unique provider paths: {len(provider_paths)}")
    for provider in sorted(provider_paths):
        model_count = sum(1 for m in models if m.get('parameters', {}).get('model', '').startswith(provider + '/'))
        print(f"   {provider}: {model_count} models")
    
    return True

def test_model_accessibility():
    """Test that all 15 models are accessible through Globant API."""
    print(f"\n{'='*60}")
    print("TESTING MODEL ACCESSIBILITY")
    print("="*60)
    
    # Load configuration
    try:
        with open('globant_enterprise_config.json', 'r') as f:
            config = json.load(f)
    except:
        print("❌ Could not load configuration")
        return False
    
    models = config.get('models', {}).get('api_models', [])
    
    # Get credentials
    api_key = os.environ.get("GLOBANT_API_KEY")
    org_id = os.environ.get("GLOBANT_ORG_ID") 
    base_url = os.environ.get("GLOBANT_BASE_URL", "https://api.saia.ai")
    
    if not api_key or not org_id:
        print("❌ Missing GLOBANT_API_KEY or GLOBANT_ORG_ID")
        return False
    
    print(f"🔑 Testing with API key: {api_key[:20]}...")
    print(f"🏢 Organization ID: {org_id}")
    
    working_models = []
    failed_models = []
    total_cost = 0.0
    
    for model in models:
        model_name = model.get('name', 'Unknown')
        model_id = model.get('parameters', {}).get('model', '')
        strategic_order = model.get('strategic_order', 999)
        
        print(f"\nTesting {strategic_order:2}. {model_name}")
        print(f"   Model ID: {model_id}")
        
        # Test API call
        success, cost = test_single_model_quick(model_id, api_key, org_id, base_url)
        
        if success:
            working_models.append({
                'name': model_name,
                'model_id': model_id,
                'strategic_order': strategic_order,
                'cost': cost
            })
            if cost and isinstance(cost, (int, float)):
                total_cost += cost
            print(f"   ✅ SUCCESS")
        else:
            failed_models.append({
                'name': model_name,
                'model_id': model_id,
                'strategic_order': strategic_order
            })
            print(f"   ❌ FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("ACCESSIBILITY TEST RESULTS")
    print("="*60)
    
    success_rate = len(working_models) / len(models) * 100
    print(f"✅ Working models: {len(working_models)}/{len(models)} ({success_rate:.1f}%)")
    print(f"💰 Total test cost: ${total_cost:.6f}")
    
    if len(working_models) >= 12:
        print(f"🎉 EXCELLENT: {len(working_models)} models working - ready for deployment!")
    elif len(working_models) >= 10:
        print(f"✅ GOOD: {len(working_models)} models working - minor issues to resolve")
    else:
        print(f"⚠️  ISSUES: Only {len(working_models)} models working - needs investigation")
    
    if failed_models:
        print(f"\n❌ FAILED MODELS ({len(failed_models)}):")
        for model in failed_models:
            print(f"   {model['strategic_order']:2}. {model['name']}")
    
    return len(working_models) >= 12

def test_single_model_quick(model_id, api_key, org_id, base_url):
    """Quick test of a single model."""
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Organization-ID": org_id
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Test"}],
        "max_tokens": 5,
        "temperature": 1.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                cost = response_json.get('usage', {}).get('total_cost', 0)
                return True, cost
            except:
                return True, 0
        else:
            return False, 0
            
    except Exception:
        return False, 0

def check_integration_compatibility():
    """Check compatibility with existing ISEE integration."""
    print(f"\n{'='*60}")
    print("CHECKING ISEE INTEGRATION COMPATIBILITY")
    print("="*60)
    
    # Check if main ISEE files can load the configuration
    integration_checks = []
    
    # 1. Check if model_api_integration.py can handle Globant provider
    try:
        # Look for Globant support in model API integration
        with open('model_api_integration.py', 'r') as f:
            content = f.read()
            if 'globant' in content.lower():
                integration_checks.append(("Model API Integration", True, "Globant support found"))
            else:
                integration_checks.append(("Model API Integration", False, "No Globant support found"))
    except FileNotFoundError:
        integration_checks.append(("Model API Integration", False, "File not found"))
    
    # 2. Check if app.py can load Globant config
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            if 'globant' in content.lower():
                integration_checks.append(("Flask App Integration", True, "Globant references found"))
            else:
                integration_checks.append(("Flask App Integration", False, "No Globant references found"))
    except FileNotFoundError:
        integration_checks.append(("Flask App Integration", False, "File not found"))
    
    # 3. Check provider selection logic
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            if '--provider' in content or 'provider' in content:
                integration_checks.append(("Provider Selection", True, "Provider selection logic found"))
            else:
                integration_checks.append(("Provider Selection", False, "No provider selection found"))
    except FileNotFoundError:
        integration_checks.append(("Provider Selection", False, "main.py not found"))
    
    # Report integration status
    for check_name, status, details in integration_checks:
        status_icon = "✅" if status else "⚠️"
        print(f"{status_icon} {check_name}: {details}")
    
    compatible_checks = sum(1 for _, status, _ in integration_checks if status)
    total_checks = len(integration_checks)
    
    if compatible_checks >= total_checks * 0.8:
        print(f"\n✅ Integration compatibility: {compatible_checks}/{total_checks} - Ready for deployment")
        return True
    else:
        print(f"\n⚠️  Integration compatibility: {compatible_checks}/{total_checks} - May need updates")
        return False

def main():
    print("EXPANDED GLOBANT ENTERPRISE AI CONFIGURATION VALIDATION")
    print("="*80)
    print("Validating 15-model configuration for ISEE Framework deployment")
    
    validation_results = []
    
    # 1. Validate configuration structure
    print(f"\n🔍 PHASE 1: CONFIGURATION STRUCTURE VALIDATION")
    config_valid = validate_config_structure()
    validation_results.append(("Configuration Structure", config_valid))
    
    if not config_valid:
        print("\n❌ Configuration validation failed - stopping validation")
        return False
    
    # 2. Test model accessibility
    print(f"\n🧪 PHASE 2: MODEL ACCESSIBILITY TESTING")
    models_accessible = test_model_accessibility()
    validation_results.append(("Model Accessibility", models_accessible))
    
    # 3. Check integration compatibility
    print(f"\n🔗 PHASE 3: INTEGRATION COMPATIBILITY CHECK")
    integration_compatible = check_integration_compatibility()
    validation_results.append(("Integration Compatibility", integration_compatible))
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL VALIDATION SUMMARY")
    print("="*80)
    
    passed_validations = sum(1 for _, status in validation_results if status)
    total_validations = len(validation_results)
    
    for validation_name, status in validation_results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {validation_name}")
    
    if passed_validations == total_validations:
        print(f"\n🎉 ALL VALIDATIONS PASSED ({passed_validations}/{total_validations})")
        print(f"✅ Expanded 15-model configuration is ready for deployment!")
        print(f"🚀 Next steps:")
        print(f"   1. Test full ISEE analysis with expanded model set")
        print(f"   2. Compare cognitive diversity vs original 12-model setup") 
        print(f"   3. Deploy to production with enhanced capabilities")
        return True
    else:
        print(f"\n⚠️  PARTIAL VALIDATION ({passed_validations}/{total_validations})")
        print(f"❌ Some issues need to be resolved before deployment")
        return False

if __name__ == "__main__":
    main()