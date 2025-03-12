import requests
import time

# Define the API endpoint
url = "http://localhost:5000/predict"

# Generate test sentences
test_sentences = [
    "SELECT * FROM users WHERE id = 1;",  # Clean (0)
    "' OR '1'='1",  # SQL Injection (1)
    "INSERT INTO products (name, price) VALUES ('Laptop', 1000);",  # Clean (0)
    "' UNION SELECT null, username, password FROM users--",  # SQL Injection (1)
    "UPDATE orders SET status = 'shipped' WHERE order_id = 123;",  # Clean (0)
    "'; DROP TABLE users--"  # SQL Injection (1)
]   # Repeat to create a large number of sentences

# Define the ground truth labels (0 = Clean, 1 = SQL Injection)
ground_truth_labels = [1, 1, 0, 1, 1, 0] 


# Measure the time taken to process the sentences
start_time = time.time()
response = requests.post(url, json={"sentences": test_sentences})
end_time = time.time()

# Get the predictions from the API response
predictions = response.json()["predictions"]
print(predictions)

# Calculate accuracy
correct_predictions = sum(1 for true, pred in zip(ground_truth_labels, predictions) if true == pred)
total_predictions = len(ground_truth_labels)
accuracy = correct_predictions / total_predictions

# Calculate the throughput (sentences per minute)
total_sentences = len(test_sentences)
time_taken = end_time - start_time
throughput = (total_sentences / time_taken) * 60

# Print the results
print(f"Total sentences processed: {total_sentences}")
print(f"Time taken: {time_taken:.2f} seconds")
print(f"Throughput: {throughput:.2f} sentences per minute")
print(f"Accuracy: {accuracy * 100:.2f}%")