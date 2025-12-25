"""
Clean up orphaned requirements (requirements that don't belong to real members)
These are old dummy/test data that should be deleted
"""
from app.database import connection

def cleanup_orphaned_requirements():
    conn, cursor = connection.cursorInstance()
    
    print("=" * 60)
    print("CLEANING UP ORPHANED REQUIREMENTS")
    print("=" * 60)
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Find requirements that don't belong to real members
        print("\n1. Finding orphaned requirements...")
        cursor.execute("""
            SELECT r.id, r.email 
            FROM requirements r
            WHERE r.accepted = 1 
              AND r.email NOT IN (
                  SELECT email FROM membership WHERE accepted = 1 AND active = 1
              )
        """)
        orphaned_reqs = cursor.fetchall()
        orphaned_req_ids = [row[0] for row in orphaned_reqs]
        orphaned_emails = list(set([row[1] for row in orphaned_reqs if row[1]]))
        
        print(f"   Found {len(orphaned_req_ids)} orphaned requirements")
        print(f"   Unique orphaned emails: {len(orphaned_emails)}")
        
        if len(orphaned_req_ids) > 0:
            # Delete evaluations for orphaned requirements first
            print("\n2. Deleting evaluations for orphaned requirements...")
            req_placeholders = ','.join(['?' for _ in orphaned_req_ids])
            cursor.execute(f"""
                DELETE FROM evaluation 
                WHERE requirementId IN ({req_placeholders})
            """, orphaned_req_ids)
            deleted_evals = cursor.rowcount
            print(f"   Deleted {deleted_evals} evaluations")
            
            # Delete orphaned requirements
            print("\n3. Deleting orphaned requirements...")
            cursor.execute(f"""
                DELETE FROM requirements 
                WHERE id IN ({req_placeholders})
            """, orphaned_req_ids)
            deleted_reqs = cursor.rowcount
            print(f"   Deleted {deleted_reqs} requirements")
            
            # Commit transaction
            conn.commit()
            print("\n✅ Successfully cleaned up orphaned requirements!")
            print(f"   Total deleted: {deleted_reqs} requirements, {deleted_evals} evaluations")
        else:
            conn.commit()
            print("\n✅ No orphaned requirements found. Database is clean!")
        
        conn.close()
        return {
            'success': True,
            'deleted_requirements': deleted_reqs if len(orphaned_req_ids) > 0 else 0,
            'deleted_evaluations': deleted_evals if len(orphaned_req_ids) > 0 else 0
        }
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {str(e)}")
        conn.close()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    cleanup_orphaned_requirements()





