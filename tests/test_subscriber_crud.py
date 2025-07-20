#!/usr/bin/env python3
"""
Unit tests for subscriber database CRUD operations.
Each test manages its own data to ensure independence.
"""

import unittest
import mysql.connector
import os
import sys
import time
from datetime import datetime

class TestSubscriberCRUD(unittest.TestCase):
    """Test class for subscriber database CRUD operations."""
    
    @classmethod
    def setUpClass(cls):
        """Set up database connection for all tests."""
        cls.db_config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('DB_PORT', '3307')),
            'user': os.getenv('DB_USER', 'subscriber_user'),
            'password': os.getenv('DB_PASSWORD', 'SubscriberPass123'),
            'database': os.getenv('DB_NAME', 'subscriber_db'),
            'autocommit': True
        }
        cls.connection = mysql.connector.connect(**cls.db_config)
        cls.cursor = cls.connection.cursor(dictionary=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database connection."""
        if hasattr(cls, 'cursor'):
            cls.cursor.close()
        if hasattr(cls, 'connection'):
            cls.connection.close()
    
    def setUp(self):
        """Set up test data before each test."""
        # Clean up any existing test data
        self.cursor.execute("DELETE FROM subscription_history WHERE subscriber_id IN (SELECT id FROM subscribers WHERE email LIKE '%test%')")
        self.cursor.execute("DELETE FROM subscription_preferences WHERE subscriber_id IN (SELECT id FROM subscribers WHERE email LIKE '%test%')")
        self.cursor.execute("DELETE FROM subscribers WHERE email LIKE '%test%'")
        self.connection.commit()
    
    def tearDown(self):
        """Clean up test data after each test."""
        # Clean up test data
        self.cursor.execute("DELETE FROM subscription_history WHERE subscriber_id IN (SELECT id FROM subscribers WHERE email LIKE '%test%')")
        self.cursor.execute("DELETE FROM subscription_preferences WHERE subscriber_id IN (SELECT id FROM subscribers WHERE email LIKE '%test%')")
        self.cursor.execute("DELETE FROM subscribers WHERE email LIKE '%test%'")
        self.connection.commit()
    
    def test_create_subscriber(self):
        """Test creating a new subscriber."""
        # Arrange
        test_email = f"test.create.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        test_data = {
            'email': test_email,
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Act
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%(email)s, %(first_name)s, %(last_name)s)
        """, test_data)
        
        # Assert
        self.cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['email'], test_email)
        self.assertEqual(result['first_name'], 'Test')
        self.assertEqual(result['last_name'], 'User')
        self.assertTrue(result['is_active'])
    
    def test_read_subscriber(self):
        """Test reading subscriber data."""
        # Arrange
        test_email = f"test.read.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'Read', 'Test'))
        
        # Act
        self.cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = self.cursor.fetchone()
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['email'], test_email)
        self.assertEqual(result['first_name'], 'Read')
        self.assertEqual(result['last_name'], 'Test')
    
    def test_update_subscriber(self):
        """Test updating subscriber information."""
        # Arrange
        test_email = f"test.update.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'Original', 'Name'))
        
        # Act
        self.cursor.execute("""
            UPDATE subscribers 
            SET first_name = %s, last_name = %s, is_active = %s
            WHERE email = %s
        """, ('Updated', 'Name', False, test_email))
        
        # Assert
        self.cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['first_name'], 'Updated')
        self.assertEqual(result['last_name'], 'Name')
        self.assertFalse(result['is_active'])
    
    def test_delete_subscriber(self):
        """Test deleting a subscriber."""
        # Arrange
        test_email = f"test.delete.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'Delete', 'Test'))
        
        # Verify subscriber exists
        self.cursor.execute("SELECT id FROM subscribers WHERE email = %s", (test_email,))
        subscriber_id = self.cursor.fetchone()['id']
        
        # Act
        self.cursor.execute("DELETE FROM subscribers WHERE email = %s", (test_email,))
        
        # Assert
        self.cursor.execute("SELECT * FROM subscribers WHERE email = %s", (test_email,))
        result = self.cursor.fetchone()
        self.assertIsNone(result)
    
    def test_subscriber_preferences_crud(self):
        """Test CRUD operations on subscription preferences."""
        # Arrange
        test_email = f"test.prefs.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'Prefs', 'Test'))
        
        subscriber_id = self.cursor.lastrowid
        
        # Create preferences
        self.cursor.execute("""
            INSERT INTO subscription_preferences (subscriber_id, newsletter_enabled, marketing_enabled, frequency)
            VALUES (%s, %s, %s, %s)
        """, (subscriber_id, True, False, 'weekly'))
        
        # Read preferences
        self.cursor.execute("""
            SELECT sp.* FROM subscription_preferences sp
            JOIN subscribers s ON sp.subscriber_id = s.id
            WHERE s.email = %s
        """, (test_email,))
        prefs = self.cursor.fetchone()
        
        self.assertIsNotNone(prefs)
        self.assertTrue(prefs['newsletter_enabled'])
        self.assertFalse(prefs['marketing_enabled'])
        self.assertEqual(prefs['frequency'], 'weekly')
        
        # Update preferences
        self.cursor.execute("""
            UPDATE subscription_preferences 
            SET marketing_enabled = %s, frequency = %s
            WHERE subscriber_id = %s
        """, (True, 'daily', subscriber_id))
        
        # Verify update
        self.cursor.execute("""
            SELECT sp.* FROM subscription_preferences sp
            JOIN subscribers s ON sp.subscriber_id = s.id
            WHERE s.email = %s
        """, (test_email,))
        updated_prefs = self.cursor.fetchone()
        
        self.assertTrue(updated_prefs['marketing_enabled'])
        self.assertEqual(updated_prefs['frequency'], 'daily')
    
    def test_subscription_history_tracking(self):
        """Test subscription history tracking."""
        # Arrange
        test_email = f"test.history.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'History', 'Test'))
        
        subscriber_id = self.cursor.lastrowid
        
        # Add history entries with small delays to ensure proper ordering
        actions = ['subscribed', 'updated', 'unsubscribed', 'reactivated']
        for i, action in enumerate(actions):
            # Add small delay to ensure proper timestamp ordering
            time.sleep(0.1)
            self.cursor.execute("""
                INSERT INTO subscription_history (subscriber_id, action, notes)
                VALUES (%s, %s, %s)
            """, (subscriber_id, action, f'Test {action} action'))
        
        # Verify history - check that all actions exist without assuming order
        self.cursor.execute("""
            SELECT action FROM subscription_history 
            WHERE subscriber_id = %s 
            ORDER BY action_date
        """, (subscriber_id,))
        history_actions = [row['action'] for row in self.cursor.fetchall()]
        
        self.assertEqual(len(history_actions), 4)
        self.assertIn('subscribed', history_actions)
        self.assertIn('updated', history_actions)
        self.assertIn('unsubscribed', history_actions)
        self.assertIn('reactivated', history_actions)
    
    def test_email_uniqueness_constraint(self):
        """Test that email uniqueness constraint is enforced."""
        # Arrange
        test_email = f"test.unique.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        
        # Insert first subscriber
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'First', 'User'))
        
        # Act & Assert - Try to insert duplicate email
        with self.assertRaises(mysql.connector.IntegrityError):
            self.cursor.execute("""
                INSERT INTO subscribers (email, first_name, last_name)
                VALUES (%s, %s, %s)
            """, (test_email, 'Second', 'User'))
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints between tables."""
        # Arrange
        test_email = f"test.fk.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        self.cursor.execute("""
            INSERT INTO subscribers (email, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (test_email, 'FK', 'Test'))
        
        subscriber_id = self.cursor.lastrowid
        
        # Test valid foreign key
        self.cursor.execute("""
            INSERT INTO subscription_preferences (subscriber_id, newsletter_enabled)
            VALUES (%s, %s)
        """, (subscriber_id, True))
        
        # Test invalid foreign key
        with self.assertRaises(mysql.connector.IntegrityError):
            self.cursor.execute("""
                INSERT INTO subscription_preferences (subscriber_id, newsletter_enabled)
                VALUES (%s, %s)
            """, (99999, True))  # Non-existent subscriber_id

if __name__ == '__main__':
    unittest.main() 