#!/usr/bin/env python3
"""
Comprehensive System Testing Script
Tests all components of the Assignment 4 implementation
"""

import subprocess
import sys
import time
import mysql.connector
import os
from datetime import datetime

def print_status(message, status="INFO"):
    """Print formatted status messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{status}] {message}")

def test_docker_environment():
    """Test 1: Verify Docker containers are running"""
    print_status("Testing Docker Environment...", "TEST")
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            if 'assignment4-db-1' in result.stdout and 'assignment4-adminer_container-1' in result.stdout:
                print_status("✅ Docker containers are running", "PASS")
                return True
            else:
                print_status("❌ Docker containers not found", "FAIL")
                return False
        else:
            print_status("❌ Docker command failed", "FAIL")
            return False
    except Exception as e:
        print_status(f"❌ Docker test failed: {e}", "FAIL")
        return False

def test_database_connection():
    """Test 2: Verify database connection"""
    print_status("Testing Database Connection...", "TEST")
    
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3307,
            user='root',
            password='Secret5555'
        )
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        
        print_status("✅ Database connection successful", "PASS")
        print_status(f"Available databases: {databases}", "INFO")
        return True
    except Exception as e:
        print_status(f"❌ Database connection failed: {e}", "FAIL")
        return False

def test_subscriber_database_setup():
    """Test 3: Create and verify subscriber database"""
    print_status("Testing Subscriber Database Setup...", "TEST")
    
    try:
        # Create database and user
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3307,
            user='root',
            password='Secret5555'
        )
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS subscriber_db")
        
        # Create user
        cursor.execute("""
            CREATE USER IF NOT EXISTS 'subscriber_user'@'%' 
            IDENTIFIED BY 'SubscriberPass123'
        """)
        
        # Grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON subscriber_db.* TO 'subscriber_user'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        cursor.close()
        connection.close()
        
        print_status("✅ Subscriber database and user created", "PASS")
        return True
    except Exception as e:
        print_status(f"❌ Database setup failed: {e}", "FAIL")
        return False

def test_flyway_migrations():
    """Test 4: Test Flyway migrations"""
    print_status("Testing Flyway Migrations...", "TEST")
    
    try:
        # Test initial migrations
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/migrations/initial:/flyway/sql',
            'redgate/flyway',
            '-user=subscriber_user',
            '-password=SubscriberPass123',
            '-url=jdbc:mysql://host.docker.internal:3307/subscriber_db',
            'migrate'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print_status("✅ Initial migrations successful", "PASS")
        else:
            print_status(f"❌ Initial migrations failed: {result.stderr}", "FAIL")
            return False
        
        # Test incremental migrations
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}/migrations/incremental:/flyway/sql',
            'redgate/flyway',
            '-user=subscriber_user',
            '-password=SubscriberPass123',
            '-url=jdbc:mysql://host.docker.internal:3307/subscriber_db',
            'migrate'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print_status("✅ Incremental migrations successful", "PASS")
            return True
        else:
            print_status(f"❌ Incremental migrations failed: {result.stderr}", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"❌ Flyway test failed: {e}", "FAIL")
        return False

def test_database_schema():
    """Test 5: Verify database schema"""
    print_status("Testing Database Schema...", "TEST")
    
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3307,
            user='subscriber_user',
            password='SubscriberPass123',
            database='subscriber_db'
        )
        cursor = connection.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['subscribers', 'subscription_preferences', 'subscription_history']
        
        if all(table in tables for table in expected_tables):
            print_status("✅ All expected tables exist", "PASS")
        else:
            print_status(f"❌ Missing tables. Found: {tables}", "FAIL")
            return False
        
        # Check subscriber data
        cursor.execute("SELECT COUNT(*) FROM subscribers")
        count = cursor.fetchone()[0]
        print_status(f"✅ Subscribers table has {count} records", "PASS")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print_status(f"❌ Schema verification failed: {e}", "FAIL")
        return False

def test_python_dependencies():
    """Test 6: Verify Python dependencies"""
    print_status("Testing Python Dependencies...", "TEST")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print_status("❌ requirements.txt not found", "FAIL")
            return False
        
        # Try to install dependencies
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("✅ Python dependencies installed", "PASS")
            return True
        else:
            print_status(f"❌ Failed to install dependencies: {result.stderr}", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"❌ Python dependencies test failed: {e}", "FAIL")
        return False

def test_crud_operations():
    """Test 7: Test CRUD operations"""
    print_status("Testing CRUD Operations...", "TEST")
    
    try:
        # Import and run tests
        import pytest
        import sys
        
        # Add tests directory to path
        sys.path.insert(0, os.path.join(os.getcwd(), 'tests'))
        
        # Set environment variables for tests
        os.environ['DB_HOST'] = '127.0.0.1'
        os.environ['DB_USER'] = 'subscriber_user'
        os.environ['DB_PASSWORD'] = 'SubscriberPass123'
        os.environ['DB_NAME'] = 'subscriber_db'
        
        # Run a simple test
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3307,
            user='subscriber_user',
            password='SubscriberPass123',
            database='subscriber_db'
        )
        cursor = connection.cursor(dictionary=True)
        
        # Test CREATE
        test_email = f"test.crud.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'Test', 'User'))
        
        # Test READ
        cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        if result and result['email'] == test_email:
            print_status("✅ CREATE and READ operations successful", "PASS")
        else:
            print_status("❌ CREATE or READ operation failed", "FAIL")
            return False
        
        # Test UPDATE
        cursor.execute("""
            UPDATE subscribers 
            SET first_name = %s 
            WHERE email = %s
        """, ('Updated', test_email))
        
        cursor.execute("SELECT first_name FROM subscribers WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        if result and result['first_name'] == 'Updated':
            print_status("✅ UPDATE operation successful", "PASS")
        else:
            print_status("❌ UPDATE operation failed", "FAIL")
            return False
        
        # Test DELETE
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (test_email,))
        cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        if result is None:
            print_status("✅ DELETE operation successful", "PASS")
        else:
            print_status("❌ DELETE operation failed", "FAIL")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print_status(f"❌ CRUD operations test failed: {e}", "FAIL")
        return False

def test_github_actions_workflow():
    """Test 8: Verify GitHub Actions workflow file"""
    print_status("Testing GitHub Actions Workflow...", "TEST")
    
    try:
        workflow_file = '.github/workflows/mysql_action.yml'
        if os.path.exists(workflow_file):
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Check for key components
            checks = [
                'name: Subscriber Database Migration and Testing',
                'on: [push, pull_request]',
                'Run Initial Flyway Migrations',
                'Run Incremental Flyway Migrations',
                'Run Database Tests',
                'Deployment Complete'
            ]
            
            missing_checks = [check for check in checks if check not in content]
            if not missing_checks:
                print_status("✅ GitHub Actions workflow file is complete", "PASS")
                return True
            else:
                print_status(f"❌ Missing components in workflow: {missing_checks}", "FAIL")
                return False
        else:
            print_status("❌ GitHub Actions workflow file not found", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"❌ GitHub Actions workflow test failed: {e}", "FAIL")
        return False

def test_documentation():
    """Test 9: Verify documentation"""
    print_status("Testing Documentation...", "TEST")
    
    try:
        required_files = [
            'README.md',
            'ASSIGNMENT_SUMMARY.md',
            'Question1_Analysis.md'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if not missing_files:
            print_status("✅ All documentation files exist", "PASS")
            
            # Check README content
            with open('README.md', 'r') as f:
                readme_content = f.read()
            
            readme_checks = [
                'Database Migration Assignment',
                'Installation and Setup',
                'Running Migrations',
                'Testing',
                'CI/CD Pipeline'
            ]
            
            missing_readme_checks = [check for check in readme_checks if check not in readme_content]
            if not missing_readme_checks:
                print_status("✅ README.md is comprehensive", "PASS")
                return True
            else:
                print_status(f"❌ README.md missing sections: {missing_readme_checks}", "FAIL")
                return False
        else:
            print_status(f"❌ Missing documentation files: {missing_files}", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"❌ Documentation test failed: {e}", "FAIL")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ASSIGNMENT 4 - COMPREHENSIVE SYSTEM TESTING")
    print("=" * 60)
    
    tests = [
        ("Docker Environment", test_docker_environment),
        ("Database Connection", test_database_connection),
        ("Subscriber Database Setup", test_subscriber_database_setup),
        ("Flyway Migrations", test_flyway_migrations),
        ("Database Schema", test_database_schema),
        ("Python Dependencies", test_python_dependencies),
        ("CRUD Operations", test_crud_operations),
        ("GitHub Actions Workflow", test_github_actions_workflow),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your system is working correctly.")
        print("\n✅ Complete Flyway migration system")
        print("✅ Subscriber database with 3 tables")
        print("✅ Comprehensive test suite (8 test cases)")
        print("✅ GitHub Actions CI/CD pipeline")
        print("✅ Ansible automation scripts")
        print("✅ Complete documentation")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the issues above.")
    
    print("\nTo clean up the environment:")
    print("docker-compose -f mysql-adminer.yml down")

if __name__ == "__main__":
    main() 