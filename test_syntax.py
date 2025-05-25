# Test the exact structure from the command wizard
def test_domain_selection():
    step_num = 3
    params = {}
    
    # Domain selection (skip if purpose already set domain)
    if not params.get("domain"):  # Only show domain selection if not set by purpose
        if True:  # RICH_AVAILABLE
            print(f"Step {step_num}: Domain Selection (RICH)")
        else:
            print(f"Step {step_num}: Domain Selection")
            
            try:
                domain_choice = int(input("Select a domain by number (or 0 for default) [0]: ") or "0")
                
                if domain_choice > 0 and domain_choice <= 5:
                    print("Selected domain")
                else:
                    print("Using default domain.")
            except ValueError:
                print("Invalid selection. Using default domain.")
    else:
        # Domain already set by purpose selection
        print(f"Domain already set by purpose: {params['domain']}")
    
    print("Continuing...")

if __name__ == "__main__":
    test_domain_selection()