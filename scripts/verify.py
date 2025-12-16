import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from app.models.config import FIBO_API_URL, FIBO_API_KEY
    from app.models.schemas import ProjectPlan
    from app.core import planner, client, validator, engine
    
    print("✅ Imports successful.")
    print(f"   Project Root: {project_root}")
    print(f"   API URL: {FIBO_API_URL}")
    print(f"   API Key Present: {bool(FIBO_API_KEY)}")

    # 1. Test Planner
    print("\nTesting Planner...")
    plan = planner.generate_project_plan("A cyberpunk city runner", "storyboard", 3)
    if isinstance(plan, ProjectPlan):
        print(f"✅ Plan generated: {plan.project_id}")
        print(f"   Shots: {len(plan.shots)}")
    else:
        print("❌ Plan generation failed.")

    # 2. Test Client Instantiation
    print("\nTesting Client...")
    fibo = client.FiboClient()
    print("✅ Client instantiated.")

    # 3. Test Validator Import
    print("\nTesting Validator...")
    # Just checking existence of function
    if hasattr(validator, 'validate_continuity'):
        print("✅ Validator function found.")
    else:
        print("❌ Validator function missing.")

    print("\n------------------------------------------------")
    print("Infrastructure verification complete.")
    print("To run the main app:")
    print("  streamlit run app/ui/main.py")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error during verification: {e}")
