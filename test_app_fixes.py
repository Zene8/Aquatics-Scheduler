# test_app_fixes.py - Test script to verify all fixes are working

import sys
import os

def test_imports():
    """Test that all imports work without errors"""
    try:
        import streamlit as st
        print("✅ Streamlit import successful")
        
        import pandas as pd
        print("✅ Pandas import successful")
        
        import firebase_admin
        print("✅ Firebase Admin import successful")
        
        import pyrebase
        print("✅ Pyrebase import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_firebase_config():
    """Test Firebase configuration"""
    try:
        from firebase_config import firebase_manager
        print("✅ Firebase manager import successful")
        return True
    except Exception as e:
        print(f"❌ Firebase config error: {e}")
        return False

def test_app_structure():
    """Test that app.py can be imported without errors"""
    try:
        # Test that the main function exists and can be called
        import app
        print("✅ App.py import successful")
        
        # Test that the main function exists
        if hasattr(app, 'main'):
            print("✅ Main function exists")
        else:
            print("❌ Main function not found")
            return False
            
        return True
    except Exception as e:
        print(f"❌ App structure error: {e}")
        return False

def test_variable_conflicts():
    """Test that there are no variable name conflicts"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        # Check for the specific variable conflict that was causing the AttributeError
        if 'for instructor_data in firebase_instructors.values():' in content:
            print("❌ Variable conflict still exists - instructor_data loop variable")
            return False
        else:
            print("✅ Variable conflict fixed")
            
        return True
    except Exception as e:
        print(f"❌ Variable conflict test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing App Fixes...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Firebase Config", test_firebase_config),
        ("App Structure", test_app_structure),
        ("Variable Conflicts", test_variable_conflicts),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app should work correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
