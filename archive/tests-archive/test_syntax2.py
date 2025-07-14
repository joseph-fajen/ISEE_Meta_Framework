# Test the exact structure causing the issue
def test_models_selection():
    step_num = 3
    selected_purpose = None
    RICH_AVAILABLE = True
    params = {}
    api_status = {"ollama": True, "ollama_models": ["model1", "model2"]}
    
    # Models selection
    if not selected_purpose or not getattr(selected_purpose, 'recommended_params', {}).get("models"):
        if RICH_AVAILABLE:
            print("RICH model selection")
            
            if api_status["ollama"]:
                print("Ollama available")
                if True:  # use_ollama
                    print("Available Ollama models:")
                    for model in api_status["ollama_models"]:
                        print(f"  • {model}")
        else:
            print(f"Step {step_num}: Model Selection")
            
            # Model selection logic
            models_count = 2
            params["models"] = models_count
            
            if models_count > 3:
                print(f"Note: Using {models_count} models will result in {models_count} times more API calls")
            
            if models_count > 1:
                print("Balance models")
                params["balanced_models"] = True
            
            if api_status["ollama"]:
                print("Ollama available")
                params["use_ollama"] = False
                
                if False:  # use_ollama
                    print("Available Ollama models:")
                    for model in api_status["ollama_models"]:
                        print(f"  • {model}")
    else:
        # Models already set by purpose selection
        print("Models count set by purpose")
    
    print("Continuing...")

if __name__ == "__main__":
    test_models_selection()