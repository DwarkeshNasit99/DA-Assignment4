-- Initialize database and user permissions
CREATE DATABASE IF NOT EXISTS subscriber_db;
USE subscriber_db;

-- Create user with restricted privileges
CREATE USER IF NOT EXISTS 'subscriber_user'@'%' IDENTIFIED BY 'SubscriberPass123';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER ON subscriber_db.* TO 'subscriber_user'@'%';
FLUSH PRIVILEGES; 