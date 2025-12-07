#!/usr/bin/env python3
"""
Test script to verify all Phase 2 APIs
"""
import requests
import json

BASE_URL = "http://localhost:8001/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health_check():
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_register():
    print_section("Testing User Registration")
    data = {
        "email": "testuser@demo.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "organization_name": "Test Organization"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✓ Registration successful")
        return response.json()["access_token"]
    elif "Email already registered" in response.json().get("detail", ""):
        print("⚠ User already exists, trying login...")
        return test_login()
    else:
        raise Exception("Registration failed")

def test_login():
    print_section("Testing User Login")
    data = {
        "email": "testuser@demo.com",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Login successful")
    return response.json()["access_token"]

def test_get_current_user(token):
    print_section("Testing Get Current User")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Get current user successful")

def test_get_tenant(token):
    print_section("Testing Get Tenant Info")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tenants/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Get tenant info successful")

def test_get_usage(token):
    print_section("Testing Get Usage Stats")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tenants/me/usage", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Get usage stats successful")

def test_list_roles(token):
    print_section("Testing List Roles")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/roles/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ List roles successful")

def test_list_users(token):
    print_section("Testing List Users")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ List users successful")

def main():
    print("\n" + "="*60)
    print("  PHASE 2 API TESTING")
    print("="*60)
    
    try:
        # Test health check
        test_health_check()
        
        # Test registration (or login if already exists)
        token = test_register()
        
        # Test authenticated endpoints
        test_get_current_user(token)
        test_get_tenant(token)
        test_get_usage(token)
        test_list_roles(token)
        test_list_users(token)
        
        print_section("ALL TESTS PASSED ✓")
        print("\nPhase 2 Backend Core is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
