-- Add subscription history table
CREATE TABLE subscription_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subscriber_id INT NOT NULL,
    action ENUM('subscribed', 'unsubscribed', 'updated', 'reactivated') NOT NULL,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id) ON DELETE CASCADE,
    INDEX idx_subscriber_action (subscriber_id, action),
    INDEX idx_action_date (action_date)
);

-- Add some sample history for existing subscribers
INSERT INTO subscription_history (subscriber_id, action, notes) VALUES
(1, 'subscribed', 'Initial subscription'),
(2, 'subscribed', 'Initial subscription'),
(3, 'subscribed', 'Initial subscription'); 