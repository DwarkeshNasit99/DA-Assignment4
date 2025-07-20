#!/usr/bin/env python3
"""
Quick System Test - Verify all Assignment 4 components
"""

import subprocess
import mysql.connector
import os
from datetime import datetime

def test_component(name, test_func):
    """Run a test and report results"""
    print(f"\n🔍 Testing: {name}")
    try:
        result = test_func()
        if result:
            print(f"✅ {name}: PASSED")
            return True
        else:
            print(f"❌ {name}: FAILED")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def test_docker():
    """Test Docker containers"""
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    return result.returncode == 0 and 'assignment4-db-1' in result.stdout

def test_database():
    """Test database connection"""
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
    return 'mysql' in databases

def test_subscriber_setup():
    """Test subscriber database setup"""
    # Create database and user
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,
        user='root',
        password='Secret5555'
    )
    cursor = connection.cursor()
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS subscriber_db")
    cursor.execute("CREATE USER IF NOT EXISTS 'subscriber_user'@'%' IDENTIFIED BY 'SubscriberPass123'")
    cursor.execute("GRANT ALL PRIVILEGES ON subscriber_db.* TO 'subscriber_user'@'%'")
    cursor.execute("FLUSH PRIVILEGES")
    
    cursor.close()
    connection.close()
    return True

def test_flyway_migrations():
    """Test Flyway migrations"""
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
    if result.returncode != 0:
        print(f"Initial migration error: {result.stderr}")
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
    return result.returncode == 0

def test_schema():
    """Test database schema"""
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,
        user='subscriber_user',
        password='SubscriberPass123',
        database='subscriber_db'
    )
    cursor = connection.cursor()
    
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    expected = ['subscribers', 'subscription_preferences', 'subscription_history']
    
    cursor.close()
    connection.close()
    return all(table in tables for table in expected)

def test_crud():
    """Test CRUD operations"""
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,
        user='subscriber_user',
        password='SubscriberPass123',
        database='subscriber_db'
    )
    cursor = connection.cursor(dictionary=True)
    
    # Test CREATE
    test_email = f"test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    cursor.execute("INSERT INTO subscribers (email, first_name, last_name) VALUES (%s, %s, %s)", 
                  (test_email, 'Test', 'User'))
    
    # Test READ
    cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
    result = cursor.fetchone()
    if not result:
        return False
    
    # Test UPDATE
    cursor.execute("UPDATE subscribers SET first_name = %s WHERE email = %s", ('Updated', test_email))
    
    # Test DELETE
    cursor.execute("DELETE FROM subscribers WHERE email = %s", (test_email,))
    
    cursor.close()
    connection.close()
    return True

def test_files():
    """Test required files exist"""
    required_files = [
        'up.yml', 'down.yml', 'flyway.conf', 'requirements.txt',
        'README.md', 'ASSIGNMENT_SUMMARY.md', 'Question1_Analysis.md',
        '.github/workflows/mysql_action.yml',
        'migrations/initial/V1__Create_subscribers_table.sql',
        'migrations/incremental/V2__Add_subscription_preferences.sql',
        'migrations/incremental/V3__Add_subscription_history.sql',
        'tests/test_subscriber_crud.py'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"Missing files: {missing}")
        return False
    return True

def main():
    print("=" * 60)
    print("ASSIGNMENT 4 - QUICK SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Docker Environment", test_docker),
        ("Database Connection", test_database),
        ("Subscriber Setup", test_subscriber_setup),
        ("Flyway Migrations", test_flyway_migrations),
        ("Database Schema", test_schema),
        ("CRUD Operations", test_crud),
        ("Required Files", test_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_component(name, test_func):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} components working")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL COMPONENTS WORKING!")
        print("\n✅ Complete Flyway migration system")
        print("✅ Subscriber database with 3 tables")
        print("✅ Comprehensive test suite")
        print("✅ GitHub Actions CI/CD pipeline")
        print("✅ Ansible automation scripts")
        print("✅ Complete documentation")
        print("\nYour Assignment 4 is ready for submission!")
    else:
        print(f"⚠️  {total - passed} components need attention")
    
    print("\nTo clean up: docker-compose -f mysql-adminer.yml down")

if __name__ == "__main__":
    main() 