"""
Test script for Fraud Recovery Assistant
"""
import sys
import json
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fraud_recovery_assistant import FraudRecoveryAssistant


def test_recovery_assistant():
    """Test fraud recovery assistant functionality"""
    
    print("=" * 60)
    print("Testing Fraud Recovery Assistant")
    print("=" * 60)
    
    # Initialize assistant
    assistant = FraudRecoveryAssistant()
    print("✓ Assistant initialized successfully\n")
    
    # Test 1: Generate recovery plan for phishing threat
    print("\n--- Test 1: Generate Recovery Plan for Phishing ---")
    threat_data = {
        "scan_id": "test123",
        "scan_type": "email",
        "detection": {
            "is_threat": True,
            "confidence": 85.5,
            "label": "phishing"
        },
        "redteam_analysis": {
            "attack_goal": "Credential theft via fake bank verification",
            "victim_profile": "Online banking users",
            "psychological_tactics": ["urgency", "authority", "fear"],
            "severity": 8
        }
    }
    
    recovery_plan = assistant.generate_recovery_plan(threat_data)
    
    print(f"Session ID: {recovery_plan['session_id']}")
    print(f"Threat Type: {recovery_plan['threat_summary']['type']}")
    print(f"Urgency Level: {recovery_plan['threat_summary']['urgency_level']}")
    print(f"Total Recovery Steps: {recovery_plan['progress_tracker']['total_steps']}")
    print(f"\nImmediate Actions:")
    for action in recovery_plan['immediate_actions']:
        print(f"  {action['step_number']}. [{action['priority']}] {action['description']}")
    
    print(f"\nPersonalized Advice (first 200 chars):")
    advice = recovery_plan['personalized_advice']
    print(f"  {advice[:200] if advice else 'N/A (requires HF API token)'}...")
    
    print("\n✓ Recovery plan generated successfully")
    
    # Test 2: Update progress
    print("\n--- Test 2: Update Progress ---")
    session_id = recovery_plan['session_id']
    progress = assistant.update_progress(session_id, 1, "completed")
    print(f"Step {progress['step_number']} marked as {progress['status']}")
    print(f"Updated at: {progress['updated_at']}")
    print("✓ Progress updated successfully")
    
    # Test 3: Generate report
    print("\n--- Test 3: Generate Recovery Report ---")
    completed_steps = [1, 2, 3]
    report = assistant.generate_report(recovery_plan, completed_steps)
    print(f"Report ID: {report['report_id']}")
    print(f"Incident Type: {report['incident_details']['incident_type']}")
    print(f"Completion Rate: {report['completion_rate']}")
    print(f"Total Actions Documented: {len(report['actions_taken'])}")
    print("✓ Report generated successfully")
    
    # Test 4: Get guidance for threat type
    print("\n--- Test 4: Get Threat-Specific Guidance ---")
    guidance = assistant.get_guidance_for_threat("scam")
    print(f"Threat Type: {guidance['threat_type']}")
    print(f"Category: {guidance['category']}")
    print(f"Recovery Steps: {len(guidance['recovery_steps'])}")
    print(f"Prevention Tips: {len(guidance['prevention_tips'])}")
    print(f"\nFirst 3 Prevention Tips:")
    for i, tip in enumerate(guidance['prevention_tips'][:3], 1):
        print(f"  {i}. {tip}")
    print("✓ Guidance retrieved successfully")
    
    # Test 5: Different threat types
    print("\n--- Test 5: Test Different Threat Types ---")
    threat_types = ["phishing", "scam", "malware", "financial_fraud"]
    for threat_type in threat_types:
        test_threat = {
            "scan_id": f"test_{threat_type}",
            "detection": {
                "is_threat": True,
                "confidence": 70,
                "label": threat_type
            },
            "redteam_analysis": {
                "attack_goal": f"Test {threat_type} attack",
                "severity": 6
            }
        }
        plan = assistant.generate_recovery_plan(test_threat)
        print(f"  {threat_type}: {len(plan['recovery_steps'])} steps, urgency: {plan['threat_summary']['urgency_level']}")
    print("✓ All threat types handled successfully")
    
    print("\n" + "=" * 60)
    print("All Tests Passed! ✓")
    print("=" * 60)
    
    # Print sample recovery plan JSON
    print("\n--- Sample Recovery Plan (JSON) ---")
    sample_plan = {
        "session_id": recovery_plan["session_id"],
        "threat_summary": recovery_plan["threat_summary"],
        "immediate_actions": recovery_plan["immediate_actions"],
        "total_steps": len(recovery_plan["recovery_steps"]),
        "resources": {
            "emergency_contacts": len(recovery_plan["resources"].get("emergency_contacts", [])),
            "credit_bureaus": len(recovery_plan["resources"].get("credit_bureaus", []))
        }
    }
    print(json.dumps(sample_plan, indent=2))


if __name__ == "__main__":
    try:
        test_recovery_assistant()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
