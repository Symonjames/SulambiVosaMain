#!/usr/bin/env python3
"""
Email System Test Script
Tests both signup and approval email flows
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "your-test-email@gmail.com")
API_BASE = f"{BACKEND_URL}/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_email_configuration():
    """Test if email system is configured"""
    print_section("Testing Email Configuration")
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/test-email",
            params={"email": TEST_EMAIL},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Configured: {data.get('configured', False)}")
            print(f"✅ Provider: {data.get('provider', 'Unknown')}")
            print(f"✅ Message: {data.get('message', 'No message')}")
            
            if data.get('test_email_sent'):
                print(f"✅ Test email sent to: {TEST_EMAIL}")
                print("   Check your inbox (and spam folder)!")
            else:
                print(f"⚠️  Test email NOT sent")
            
            return data.get('configured', False)
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        print(f"   Make sure backend is running at: {BACKEND_URL}")
        return False

def test_signup_email():
    """Test signup email by registering a test user"""
    print_section("Testing Signup Email Flow")
    
    # Generate unique test data
    import random
    test_id = random.randint(1000, 9999)
    test_username = f"testuser{test_id}"
    test_email = f"test{test_id}@example.com"
    
    registration_data = {
        "username": test_username,
        "email": test_email,
        "fullname": f"Test User {test_id}",
        "password": "testpass123",
        "applyingAs": "student",
        "srcode": f"TEST{test_id}",
        "age": 20,
        "sex": "male",
        "campus": "Main",
        "collegeDept": "CS",
        "yrlevelprogram": "BS CS 3",
        "address": "Test Address",
        "contactNum": "1234567890",
        "birthday": "2000-01-01",
        "volunterismExperience": "none",
        "weekdaysTimeDevotion": "2-4 hours",
        "weekendsTimeDevotion": "4-6 hours",
        "paymentOption": "cash",
        "bloodType": "O+",
        "bloodDonation": False,
        "affiliation": "Student"
    }
    
    try:
        print(f"📧 Registering test user: {test_email}")
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration successful!")
            print(f"   Member ID: {data.get('member', {}).get('id', 'N/A')}")
            print(f"   Email should be sent to: {test_email}")
            print(f"   Check backend logs for: [EMAIL SUCCESS] or [EMAIL ERROR]")
            return data.get('member', {}).get('id')
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def check_environment_variables():
    """Check if required environment variables are set"""
    print_section("Checking Environment Variables")
    
    required_vars = {
        "RESEND_API_KEY": "Resend API key (starts with 're_')",
        "RESEND_FROM_EMAIL": "Resend sender email",
        "FRONTEND_APP_URL": "Frontend URL (for approval email login link)",
    }
    
    optional_vars = {
        "AUTOMAILER_EMAIL": "SMTP email (fallback)",
        "AUTOMAILER_PASSW": "SMTP password (fallback)",
    }
    
    all_set = True
    
    print("Required Variables:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSW" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value} ({desc})")
        else:
            print(f"  ❌ {var}: NOT SET ({desc})")
            all_set = False
    
    print("\nOptional Variables (SMTP fallback):")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = "***" if "PASSW" in var else value
            print(f"  ✅ {var}: {display_value} ({desc})")
        else:
            print(f"  ⚠️  {var}: NOT SET ({desc})")
    
    return all_set

def check_template_files():
    """Check if email template files exist"""
    print_section("Checking Email Template Files")
    
    templates = {
        "templates/application-under-review.html": "Signup email template",
        "templates/we-are-pleased-to-inform-membership.html": "Approval email template",
    }
    
    all_exist = True
    
    for template_path, desc in templates.items():
        if os.path.exists(template_path):
            print(f"  ✅ {template_path} exists ({desc})")
        else:
            print(f"  ❌ {template_path} NOT FOUND ({desc})")
            all_exist = False
    
    return all_exist

def main():
    print("\n" + "="*60)
    print("  EMAIL SYSTEM DEBUGGING TEST")
    print("="*60)
    
    # Step 1: Check environment variables
    env_ok = check_environment_variables()
    
    # Step 2: Check template files
    templates_ok = check_template_files()
    
    # Step 3: Test email configuration
    config_ok = test_email_configuration()
    
    # Step 4: Test signup email (optional)
    if config_ok and env_ok and templates_ok:
        print("\n" + "-"*60)
        response = input("Test signup email flow? (y/n): ").strip().lower()
        if response == 'y':
            member_id = test_signup_email()
            if member_id:
                print(f"\n✅ Test user created with ID: {member_id}")
                print("   Check your email inbox for the 'Application Under Review' email")
                print("   Check backend logs for email sending status")
    
    # Summary
    print_section("Summary")
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ MISSING'}")
    print(f"Template Files: {'✅ OK' if templates_ok else '❌ MISSING'}")
    print(f"Email Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    
    if not env_ok:
        print("\n⚠️  Fix: Set missing environment variables in .env or Render dashboard")
    if not templates_ok:
        print("\n⚠️  Fix: Ensure template files exist in templates/ directory")
    if not config_ok:
        print("\n⚠️  Fix: Check email configuration (RESEND_API_KEY, RESEND_FROM_EMAIL)")
    
    if env_ok and templates_ok and config_ok:
        print("\n✅ All checks passed! Email system should be working.")
        print("   If emails still don't work, check:")
        print("   1. Backend logs for [EMAIL ERROR] messages")
        print("   2. Resend dashboard for email delivery status")
        print("   3. Spam/junk folder in email inbox")

if __name__ == "__main__":
    main()

