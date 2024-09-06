from flask import Flask, render_template, jsonify
import os
import webbrowser
from threading import Timer
import threading

app = Flask(__name__)

# Flag to ensure browser opens only once
browser_opened = False

# Route for your AI assistant's interface
@app.route("/")
def index():
    # Pass any context data to your template (e.g., initial prompts)
    return render_template("main.html")

@app.route('/api/get_log')
def get_log_data():
    log_path = os.path.join(os.getcwd(), 'templates', 'log.txt')
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'log': log_content})

def open_browser():
    global browser_opened
    if not browser_opened:
        webbrowser.open_new_tab("http://127.0.0.1:4444")
        browser_opened = True

def UI():
    # Set the Timer to open the browser after the server starts
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=4444)  # Set debug=False for production
    
UI()