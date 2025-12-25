import os
import sys
sys.path.append('.')

# Set environment variable
os.environ['DB_PATH'] = 'app/database/database.db'

print("=== Debug Evaluation Endpoint ===")

try:
    print("1. Testing database connection...")
    from app.database.connection import cursorInstance
    conn, cursor = cursorInstance()
    print("✓ Database connection successful")
    
    print("2. Testing RequirementsModel...")
    from app.models.RequirementsModel import RequirementsModel
    req_db = RequirementsModel()
    print("✓ RequirementsModel imported")
    
    print("3. Testing get method with test123...")
    result = req_db.get("test123")
    print(f"Result: {result}")
    print("✓ get method completed")
    
    print("4. Testing EvaluationModel...")
    from app.models.EvaluationModel import EvaluationModel
    eval_db = EvaluationModel()
    print("✓ EvaluationModel imported")
    
    print("5. Testing getAndSearch method...")
    eval_result = eval_db.getAndSearch(["requirementId"], ["test123"])
    print(f"Evaluation result: {eval_result}")
    print("✓ getAndSearch method completed")
    
    conn.close()
    print("=== All tests completed successfully ===")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

































































