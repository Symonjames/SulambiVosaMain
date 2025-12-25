import os
import sys
import requests
import json

# Add the current directory to Python path
sys.path.append('.')

# Set environment variable for database
os.environ['DB_PATH'] = 'app/database/database.db'

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def test_database_connection():
    """Test database connection and evaluation table"""
    print("Testing database connection...")
    try:
        from app.database.connection import cursorInstance
        conn, cursor = cursorInstance()
        
        # Check if evaluation table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evaluation';")
        eval_table = cursor.fetchone()
        
        if eval_table:
            print("✓ Evaluation table exists")
            
            # Check evaluation table structure
            cursor.execute("PRAGMA table_info(evaluation);")
            columns = cursor.fetchall()
            print(f"Evaluation table columns: {[col[1] for col in columns]}")
            
            # Check if there are any evaluation records
            cursor.execute("SELECT COUNT(*) FROM evaluation;")
            eval_count = cursor.fetchone()[0]
            print(f"Evaluation records count: {eval_count}")
            
        else:
            print("✗ Evaluation table does not exist")
            
        conn.close()
        print("Database connection test completed")
        
    except Exception as e:
        print(f"Database connection error: {e}")
        import traceback
        traceback.print_exc()

def test_get_all_evaluations():
    """Test getting all evaluations"""
    print("\nTesting get all evaluations...")
    url = f"{BASE_URL}/evaluation/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✓ Get all evaluations successful")
        else:
            print(f"✗ Get all evaluations failed: {response.text}")
            
    except Exception as e:
        print(f"Error testing get all evaluations: {e}")

def test_get_personal_evaluation_status():
    """Test getting personal evaluation status (requires authentication)"""
    print("\nTesting get personal evaluation status...")
    url = f"{BASE_URL}/evaluation/personal"
    
    try:
        # First, try without authentication (should fail)
        response = requests.get(url)
        print(f"Status Code (no auth): {response.status_code}")
        
        if response.status_code == 401 or response.status_code == 403:
            print("✓ Correctly requires authentication")
        else:
            print(f"✗ Should require authentication: {response.text}")
            
    except Exception as e:
        print(f"Error testing personal evaluation status: {e}")

def test_evaluation_model():
    """Test the EvaluationModel directly"""
    print("\nTesting EvaluationModel...")
    try:
        from app.models.EvaluationModel import EvaluationModel
        
        eval_model = EvaluationModel()
        print("✓ EvaluationModel imported successfully")
        
        # Test getting all evaluations
        all_evaluations = eval_model.getAll()
        print(f"Found {len(all_evaluations)} evaluations in database")
        
        if all_evaluations:
            print("Sample evaluation record:")
            print(json.dumps(all_evaluations[0], indent=2, default=str))
        
    except Exception as e:
        print(f"Error testing EvaluationModel: {e}")
        import traceback
        traceback.print_exc()

def test_evaluation_controller():
    """Test evaluation controller functions"""
    print("\nTesting evaluation controller...")
    try:
        from app.controllers.evaluation import getAllEvaluation, getPersonalEvaluationStatus
        
        # Test getAllEvaluation
        result = getAllEvaluation()
        print(f"getAllEvaluation result: {json.dumps(result, indent=2, default=str)}")
        
        print("✓ Evaluation controller functions imported successfully")
        
    except Exception as e:
        print(f"Error testing evaluation controller: {e}")
        import traceback
        traceback.print_exc()

def test_requirements_connection():
    """Test connection between requirements and evaluations"""
    print("\nTesting requirements-evaluation connection...")
    try:
        from app.database.connection import cursorInstance
        conn, cursor = cursorInstance()
        
        # Check if requirements table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='requirements';")
        req_table = cursor.fetchone()
        
        if req_table:
            print("✓ Requirements table exists")
            
            # Check for requirements with evaluations
            cursor.execute("""
                SELECT r.id, r.email, r.eventId, r.type, e.id as eval_id, e.finalized
                FROM requirements r
                LEFT JOIN evaluation e ON r.id = e.requirementId
                LIMIT 5
            """)
            req_eval_data = cursor.fetchall()
            
            print(f"Requirements with evaluation data: {len(req_eval_data)}")
            for row in req_eval_data:
                print(f"  Req ID: {row[0]}, Email: {row[1]}, Event ID: {row[2]}, Type: {row[3]}, Eval ID: {row[4]}, Finalized: {row[5]}")
        else:
            print("✗ Requirements table does not exist")
            
        conn.close()
        
    except Exception as e:
        print(f"Error testing requirements connection: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all evaluation tests"""
    print("=" * 50)
    print("EVALUATION TESTING SUITE")
    print("=" * 50)
    
    test_database_connection()
    test_evaluation_model()
    test_evaluation_controller()
    test_requirements_connection()
    test_get_all_evaluations()
    test_get_personal_evaluation_status()
    
    print("\n" + "=" * 50)
    print("EVALUATION TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    main()