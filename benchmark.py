import requests
import time
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote
from collections import Counter  # Import Counter for counting class distributions

def decode_and_extract_query(url_or_string):
    try:
        # Decode the URL
        decoded_url = unquote(url_or_string)
        
        # Parse the URL
        parsed_url = urlparse(decoded_url)
        
        # Check if the input is a valid URL (has a scheme and netloc)
        if not parsed_url.scheme or not parsed_url.netloc:
            return decoded_url  # Return the original string if it's not a valid URL
        
        # Check if the URL has a query part
        if parsed_url.query:
            # Extract the query part
            query_params = parsed_url.query
            return query_params
        else:
            # Return 'no query part' if the URL has no query
            return 'no query part'
    except Exception:
        # Return the original string if something goes wrong
        return url_or_string


# Define the API endpoint
url = "http://localhost:5000/predict"

# Read sentences from the text file
input_file = "SQLi_Task_Evaluation_File.txt"
output_file = "SQLi_Task_Predictions_with_Avg_Confidence.csv"

# Read the file with the correct encoding
with open(input_file, "r", encoding="utf-8") as file:  # Use "utf-8-sig" if needed
    test_sentences = [line.strip() for line in file.readlines()]

decoded_sentences = [decode_and_extract_query(sentence) for sentence in test_sentences]

# Measure the time taken to process the sentences
start_time = time.time()

# Send sentences to the API for prediction
response = requests.post(url, json={"sentences": decoded_sentences})

# Ensure the API call was successful
if response.status_code == 200:
    response_data = response.json()  # Get the entire response
    predictions = response_data["predictions"]  # Predicted class labels
    average_confidence = response_data["average_confidence"]  # Average confidence level from the API
else:
    print(f"Error: Failed to fetch predictions. Status code: {response.status_code}")
    print(response.text)
    exit()

end_time = time.time()

# Calculate throughput (sentences per minute)
total_sentences = len(test_sentences)
time_taken = end_time - start_time
throughput = (total_sentences / time_taken) * 60

# Calculate class distribution
class_distribution = Counter(predictions)  # Count occurrences of each class
clean_count = class_distribution.get(0, 0)  # Number of sentences predicted as clean (0)
sql_injection_count = class_distribution.get(1, 0)  # Number of sentences predicted as SQL injection (1)

# Print statistics
print(f"Total sentences processed: {total_sentences}")
print(f"Time taken: {time_taken:.2f} seconds")
print(f"Throughput: {throughput:.2f} sentences per minute")
print(f"Average Confidence Level: {average_confidence:.2f}")
print(f"Sentences predicted as clean (0): {clean_count}")
print(f"Sentences predicted as SQL injection (1): {sql_injection_count}")

# Save the results to a CSV file
results = pd.DataFrame({
    "Sentence": test_sentences,
    "Prediction": predictions
})
results.to_csv(output_file, index=False)

print(f"Predictions saved to {output_file}")