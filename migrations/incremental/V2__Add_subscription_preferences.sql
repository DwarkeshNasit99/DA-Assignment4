-- Add subscription preferences table
CREATE TABLE subscription_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subscriber_id INT NOT NULL,
    newsletter_enabled BOOLEAN DEFAULT TRUE,
    marketing_enabled BOOLEAN DEFAULT FALSE,
    frequency ENUM('daily', 'weekly', 'monthly') DEFAULT 'weekly',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_subscriber_pref (subscriber_id)
);

-- Add some sample preferences for existing subscribers
INSERT INTO subscription_preferences (subscriber_id, newsletter_enabled, marketing_enabled, frequency) VALUES
(1, TRUE, FALSE, 'weekly'),
(2, TRUE, TRUE, 'daily'),
(3, FALSE, TRUE, 'monthly'); 