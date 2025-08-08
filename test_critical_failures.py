#!/usr/bin/env python3
"""
Test script for critical scoring failures identified in ISEE analysis.

This script tests the enhanced scoring system against the specific template 
responses and buzzword-heavy content that previously dominated findings.
"""

from evaluation_scoring import create_default_framework, score_text_with_quality_gates

# CRITICAL FAILURE EXAMPLES (Based on actual ISEE failures)

# Example 1: Gemini template failure with placeholders
gemini_template_failure = """
Idea 1: A solution involving n

This is a simulated response that demonstrates placeholder text. The implementation would involve {solution} and {details} that need to be filled in.

Idea 2: A solution involving m

Another template response with [insert specific details here] and [content].

These ideas would revolutionize the paradigm through synergistic approaches.
"""

# Example 2: Grok's buzzword-heavy response (actual failure)
grok_buzzword_response = """
Empathy Ecosystems: Simulating Emotional User Narratives

We need to leverage quantum feedback loops and temporal weavers to create diversity mirrors that transcend traditional paradigms. Through meta-cognitive fusion and emergent consciousness, we can orchestrate comprehensive frameworks that revolutionize the ecosystem.

The holistic approach involves:
- Algorithmic empathy through neural synthesis
- Quantum entanglement methodologies 
- Morphic resonance integration
- Bio-digital convergence strategies

This transformative journey will unlock unprecedented levels of optimization through innovative thinking and cutting-edge solutions that provide world-class results.
"""

# Example 3: Template response with "This is a simulated response"
template_simulation = """
This is a simulated response for testing purposes.

The solution would involve various approaches and methodologies that could potentially address the problem through comprehensive analysis and strategic implementation.

Some ideas include:
1. A solution involving approach A
2. A solution involving approach B  
3. A solution involving approach C

These concepts would need further development and specific implementation details.
"""

# Example 4: Good response (Claude 4 Sonnet style - should score well)
claude_good_response = """
Phase 1: Capability Building (Months 1-6)

Implement a systematic approach to developer productivity optimization:

1. Infrastructure Setup (Weeks 1-4)
   - Deploy Kubernetes clusters (3-node minimum for high availability)
   - Configure Terraform for infrastructure as code
   - Setup monitoring with Prometheus/Grafana stack

2. Development Process Enhancement (Weeks 5-12)
   - Implement CI/CD pipeline with GitHub Actions
   - Deploy API gateway with rate limiting (1000 req/sec capacity)
   - Configure automated testing framework (target 80% code coverage)

3. Team Scaling Preparation (Weeks 13-26)
   - Establish microservices architecture (8-12 bounded contexts)
   - Implement service mesh with Istio for traffic management
   - Deploy centralized logging with ELK stack

Expected outcomes: 40% reduction in deployment time, 60% improvement in system reliability, 25% increase in developer velocity. Resource requirements: 4 senior engineers, 1 DevOps specialist, $75K infrastructure budget.

Success metrics: 99.9% uptime SLA, sub-200ms API response times, zero-downtime deployments.
"""

# Example 5: DeepSeek's "PD3" framework (should score well)
deepseek_good_response = """
Preemptive Documentation-Driven Development (PD3)

A systematic methodology for technical debt reduction and code quality improvement:

Technical Implementation:
1. Documentation-First Development
   - Write API specifications before code (OpenAPI 3.0 standard)
   - Create architectural decision records (ADRs) for all major changes
   - Implement automated documentation generation with Sphinx

2. Preemptive Quality Gates
   - Static code analysis with SonarQube (quality gate: >90% coverage)
   - Automated dependency vulnerability scanning
   - Performance regression testing (benchmark: <100ms latency increase)

3. Continuous Integration Pipeline
   - Multi-stage Docker builds with layer caching
   - Parallel test execution across 4 environments
   - Automated database migration testing

Resource allocation: 6-week implementation timeline, 3 senior developers, $40K tooling budget.

Measurable benefits: 70% reduction in production bugs, 50% faster onboarding time, 30% improvement in code review efficiency.
"""

def run_critical_failure_tests():
    """Run tests against critical failures identified in ISEE analysis."""
    
    framework = create_default_framework()
    
    test_cases = [
        ("Gemini Template Failure", gemini_template_failure, "Gemini Pro"),
        ("Grok Buzzword Response", grok_buzzword_response, "Grok - The Contrarian Maverick"),  
        ("Template Simulation", template_simulation, "Unknown Model"),
        ("Claude Good Response", claude_good_response, "Claude 4 Sonnet"),
        ("DeepSeek PD3 Framework", deepseek_good_response, "DeepSeek R1")
    ]
    
    print("🚨 CRITICAL FAILURE TESTING - Enhanced Scoring System")
    print("=" * 80)
    
    results = []
    
    for name, text, model in test_cases:
        print(f"\n🧪 Testing: {name} ({model})")
        print("-" * 60)
        
        result = score_text_with_quality_gates(framework, text, model)
        
        # Check if it's a template failure
        if result.get('template_failure', False):
            print(f"🚫 TEMPLATE FAILURE DETECTED")
            print(f"   Reasons: {', '.join(result['failure_reasons'])}")
            print(f"   Final Score: {result['final_weighted_score']:.3f}")
        else:
            print(f"✅ Valid Response")
            print(f"   Final Score: {result['final_weighted_score']:.3f}")
            print(f"   Quality Gates: {'PASSED' if result['quality_gates']['passes_all_gates'] else 'FAILED'}")
            
            if result['quality_gates']['failed_gates']:
                print(f"   Failed Gates: {', '.join(result['quality_gates']['failed_gates'])}")
            
            analysis = result['detailed_analysis']
            buzzwords = analysis['buzzword_counts']
            print(f"   Buzzwords: {buzzwords.get('total_buzzwords', 0)} (penalty: -{buzzwords.get('buzzword_penalty', 0):.2f})")
            print(f"   Actionability: {analysis['actionability_score']:.3f}")
            print(f"   Implementation Reward: {analysis['implementation_reward']:.3f}")
            
        results.append((name, result['final_weighted_score'], result.get('template_failure', False)))
    
    # Summary Analysis
    print("\n" + "=" * 80)
    print("🎯 CRITICAL ANALYSIS SUMMARY")
    print("=" * 80)
    
    template_failures = [r for r in results if r[2]]  # Template failures
    valid_responses = [r for r in results if not r[2]]  # Valid responses
    
    print(f"\nTemplate Failures Detected: {len(template_failures)}/{len(results)}")
    for name, score, _ in template_failures:
        print(f"  🚫 {name}: {score:.3f}")
    
    print(f"\nValid Responses Ranked:")
    valid_responses.sort(key=lambda x: x[1], reverse=True)  # Sort by score descending
    for i, (name, score, _) in enumerate(valid_responses, 1):
        print(f"  {i}. {name}: {score:.3f}")
    
    # Check if the system fixed the original problems
    print(f"\n🔍 SYSTEM EFFECTIVENESS:")
    
    # Were template responses properly detected?
    expected_failures = ["Gemini Template Failure", "Template Simulation"]
    detected_failures = [name for name, _, is_failure in results if is_failure]
    
    if all(expected in detected_failures for expected in expected_failures):
        print("✅ Template failure detection: WORKING")
    else:
        print("❌ Template failure detection: FAILED")
    
    # Were buzzword responses properly penalized?
    buzzword_test = next((score for name, score, failure in results if name == "Grok Buzzword Response" and not failure), None)
    if buzzword_test is not None and buzzword_test < 0.1:
        print("✅ Buzzword penalty system: WORKING") 
    else:
        print("❌ Buzzword penalty system: FAILED")
    
    # Were good responses properly rewarded?
    good_responses = [score for name, score, failure in results if name in ["Claude Good Response", "DeepSeek PD3 Framework"] and not failure]
    if good_responses and max(good_responses) > 0.4:
        print("✅ Technical content rewards: WORKING")
    else:
        print("❌ Technical content rewards: NEEDS IMPROVEMENT")
    
    print(f"\n📊 Score Distribution:")
    all_scores = [score for _, score, failure in results if not failure]
    if all_scores:
        print(f"   Highest: {max(all_scores):.3f}")
        print(f"   Lowest: {min(all_scores):.3f}")
        print(f"   Average: {sum(all_scores)/len(all_scores):.3f}")

if __name__ == "__main__":
    run_critical_failure_tests()