from flask import Flask, request, jsonify
import joblib
import time
import mysql.connector

app = Flask(__name__)

# Load the model and vectorizer
model = joblib.load('sql_injection_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Database configuration
db_config = {
    'host': 'mysql_db',  # Use the service name from docker-compose
    'user': 'flask_user',
    'password': 'flaskpassword',
    'database': 'flask_db'
}

# Function to log request metadata to the database
def log_request_to_db(source_ip, request_type, endpoint, response_time, user_agent, content_length, status_code, referrer, query_parameters, headers, error_message, api_version, client_id, request_id):
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert the request metadata into the database
        query = """
        INSERT INTO requests (
            source_ip, request_type, endpoint, response_time, user_agent, content_length,
            status_code, referrer, query_parameters, headers, error_message, api_version,
            client_id, request_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            source_ip, request_type, endpoint, response_time, user_agent, content_length,
            status_code, referrer, query_parameters, headers, error_message, api_version,
            client_id, request_id
        ))

        # Commit the transaction
        connection.commit()

        # Close the connection
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error logging request to database: {e}")

# API endpoint for predictions
@app.route('/predict', methods=['POST'])
def predict():
    # Capture the start time
    start_time = time.time()

    try:
        # Get the request data
        data = request.json
        sentences = data['sentences']

        # Capture request metadata
        source_ip = request.remote_addr
        request_type = request.method
        endpoint = request.path
        user_agent = request.headers.get('User-Agent')
        content_length = request.content_length
        referrer = request.headers.get('Referer')
        query_parameters = request.query_string.decode('utf-8')
        headers = str(request.headers)
        api_version = "v1"  # Example: Hardcoded API version
        client_id = request.headers.get('X-Client-ID')  # Example: Custom header for client ID
        request_id = request.headers.get('X-Request-ID')  # Example: Custom header for request ID

        # Process the sentences
        sentence_tfidf = vectorizer.transform(sentences)
        predictions = model.predict(sentence_tfidf)
        probabilities = model.predict_proba(sentence_tfidf)
        avg_confidence = probabilities.max(axis=1).mean()

        # Calculate the response time
        response_time = time.time() - start_time

        # Log the request metadata to the database
        log_request_to_db(
            source_ip, request_type, endpoint, response_time, user_agent, content_length,
            200, referrer, query_parameters, headers, None, api_version, client_id, request_id
        )

        # Return the results
        return jsonify({
            "predictions": predictions.tolist(),
            "average_confidence": avg_confidence
        })

    except Exception as e:
        # Log the error and return an error response
        response_time = time.time() - start_time
        log_request_to_db(
            source_ip, request_type, endpoint, response_time, user_agent, content_length,
            500, referrer, query_parameters, headers, str(e), api_version, client_id, request_id
        )
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)