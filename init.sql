CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_ip VARCHAR(50) NOT NULL,
    request_type VARCHAR(10) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time FLOAT NOT NULL,
    user_agent TEXT,
    content_length INT,
    status_code INT,
    referrer TEXT,
    query_parameters TEXT,
    headers TEXT,
    error_message TEXT,
    api_version VARCHAR(50),
    client_id VARCHAR(255),
    request_id VARCHAR(255)
);