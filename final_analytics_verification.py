#!/usr/bin/env python3
"""Final verification that analytics data is ready"""

import sqlite3
import os

backend_dir = os.path.join("Technology Transfer _ Sulambi VMS", "Source Code", "sulambi-backend-main", "sulambi-backend-main")
DB_PATH = os.path.join(backend_dir, "app", "database", "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("FINAL ANALYTICS VERIFICATION")
print("=" * 60)

# Check members
cursor.execute("SELECT COUNT(*) FROM membership WHERE active = 1 AND accepted = 1")
members = cursor.fetchone()[0]
print(f"\n✓ Active & accepted members: {members}")

# Check requirements
cursor.execute("SELECT COUNT(*) FROM requirements WHERE accepted = 1")
reqs = cursor.fetchone()[0]
print(f"✓ Accepted requirements: {reqs}")

# Check evaluations
cursor.execute("SELECT COUNT(*) FROM evaluation WHERE finalized = 1")
evals = cursor.fetchone()[0]
print(f"✓ Finalized evaluations: {evals}")

# Test getAnalytics query
cursor.execute("""
    SELECT COUNT(DISTINCT m.id)
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email
    WHERE m.active = 1 AND m.accepted = 1 AND r.accepted = 1
    AND m.age IS NOT NULL AND m.sex IS NOT NULL
""")
analytics_ready = cursor.fetchone()[0]
print(f"✓ Members ready for analytics: {analytics_ready}")

# Test getActiveMemberData query (for dropout risk)
cursor.execute("""
    SELECT 
        m.fullname,
        COUNT(r.id) as total_regs,
        COUNT(CASE WHEN e.finalized = 1 AND e.recommendations != '' THEN 1 END) as attended
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    LEFT JOIN evaluation e ON r.id = e.requirementId AND e.finalized = 1
    WHERE m.active = 1 AND m.accepted = 1
    GROUP BY m.id, m.fullname
    LIMIT 5
""")
sample_members = cursor.fetchall()
print(f"\n✓ Sample members for dropout risk (first 5):")
for name, regs, attended in sample_members:
    print(f"  - {name}: {regs} registrations, {attended} attended")

# Age distribution
cursor.execute("""
    SELECT m.age, COUNT(*) as count
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    WHERE m.active = 1 AND m.accepted = 1 AND m.age IS NOT NULL
    GROUP BY m.age
    ORDER BY CAST(m.age AS INTEGER)
""")
age_dist = cursor.fetchall()
print(f"\n✓ Age distribution:")
for age, count in age_dist:
    print(f"  - Age {age}: {count} members")

# Sex distribution
cursor.execute("""
    SELECT m.sex, COUNT(*) as count
    FROM membership m
    INNER JOIN requirements r ON m.email = r.email AND r.accepted = 1
    WHERE m.active = 1 AND m.accepted = 1 AND m.sex IS NOT NULL
    GROUP BY m.sex
""")
sex_dist = cursor.fetchall()
print(f"\n✓ Sex distribution:")
for sex, count in sex_dist:
    print(f"  - {sex}: {count} members")

conn.close()

print("\n" + "=" * 60)
if analytics_ready >= 100:
    print("✅ ALL DATA READY FOR ANALYTICS!")
    print(f"   - {members} members")
    print(f"   - {reqs} requirements")
    print(f"   - {evals} evaluations")
    print(f"   - {analytics_ready} members ready for analytics")
    print("\n⚠️  IMPORTANT: Restart the backend server to see the data!")
    print("   The backend code has been fixed (accepted = 1 instead of True)")
    print("   After restart, refresh the dashboard to see analytics")
else:
    print("❌ DATA NOT READY")
print("=" * 60)

















