from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash, Response
from threading import Thread
import cv2
import numpy as np
import MySQLdb
import secrets
from roboflow import Roboflow
import os

# Initialize Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secret key

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'wildlife_detection'

# Initialize MySQL
mysql = MySQLdb.connect(host='localhost', user='root', password='', db='wildlife_detection')

# Initialize Roboflow with your API key
rf = Roboflow(api_key="JEhrwMUHZ23ZD3L5Mind") 
project = rf.workspace().project("wildlife-detection-gtwwn")
model = project.version(1).model  

# Define a dictionary for animal classes and their corresponding colors
colors = {
    "fox": (0, 255, 0),  # Green
    "Panda": (255, 0, 0),  # Blue
    "Tiger": (0, 0, 255),  # Red
    "bear": (0, 255, 255),  # Yellow
    "elephant": (255, 0, 255),  # Magenta
    "Lion": (155, 78, 135),
    "Wolf": (200, 100, 200)
}

# HTML templates
home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <title>Home</title>
</head>
<body>
    <div class="header">
        <p class="greeting">Hello, {{ session['username'] }}!</p>
        <h1>Welcome to Wildlife Detection</h1>
    </div>
    <div class="content">
        {% if logged_in %}
            <a class="logout" href="{{ url_for('logout') }}">Logout</a>
            <div class="menu">
                <a href="{{ url_for('upload') }}">
                    <div class="card card1">
                        <img src="{{ url_for('static', filename='upload.png') }}" alt="Upload">
                        <span>Upload an Image</span>
                    </div>
                </a>
                <a href="{{ url_for('realtime') }}">
                    <div class="card card2">
                        <img src="{{ url_for('static', filename='face_scan.png') }}" alt="Real-time Detection">
                        <span>Real-time Detection</span>
                    </div>
                </a>
            </div>
        {% else %}
            <div class="menu">
                <a href="{{ url_for('login') }}">
                    <div class="card card3">
                        <img src="{{ url_for('static', filename='login.png') }}" alt="Login">
                        <span>Login</span>
                    </div>
                </a>
                <a href="{{ url_for('signup') }}">
                    <div class="card card4">
                        <img src="{{ url_for('static', filename='account.png') }}" alt="Signup">
                        <span>Signup</span>
                    </div>
                </a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

signup_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='style1.css') }}">
    <title>Signup</title>
</head>
<body>
<div class="header">
        <h1>Welcome to Wildlife Detection</h1>
    </div>
    <div class="signup-container">
        <h1>Signup</h1>
        <form action="{{ url_for('signup') }}" method="post">
            <div class="input-group">
                <label for="username"><i class="fa fa-user"></i> Username</label>
                <input type="text" id="username" name="username" placeholder="Enter Username" required>
            </div>
            <div class="input-group">
                <label for="password"><i class="fa fa-lock"></i> Password</label>
                <input type="password" id="password" name="password" placeholder="Enter Password" required>
            </div>
            <input type="submit" class="submit-btn" value="Signup">
        </form>
        <div class="login-link">
            <a href="{{ url_for('login') }}">Already have an account? Login here</a>
        </div>
    </div>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Form</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style2.css') }}">
</head>
<body>
<div class="header">
        <h1>Welcome to Wildlife Detection</h1>
    </div>
    <div class="login-container">
        <h1>Login</h1>
        <form action="{{ url_for('login') }}" method="post">
            <div class="input-group">
                <label for="username"><i class="fa fa-user"></i> Username</label>
                <input type="text" id="username" name="username" placeholder="Enter Username" required>
            </div>
            <div class="input-group">
                <label for="password"><i class="fa fa-lock"></i> Password</label>
                <input type="password" id="password" name="password" placeholder="Enter Password" required>
            </div>
            <input type="submit" class="submit-btn" value="Login">
        </form>
        <div class="signup-link">
            <a href="{{ url_for('signup') }}">Don't have an account? Sign up</a>
        </div>
    </div>
</body>
</html>
"""

upload_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='style3.css') }}">
    <title>Image Upload and Detection Result</title>
</head>
<body>
    <div class="container">
        <!-- Left Side: Upload Section -->
        <div class="upload-section">
            <h2>Upload Image for Detection</h2>
            <form id="uploadForm" action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data">
                <input type="file" name="file" id="fileInput" required>
                <div class="upload-container" id="imagePreview">
                    <p>No image uploaded</p>
                </div>
                <button type="submit" class="btn upload-btn">Upload</button>
            </form>
        </div>

        <!-- Right Side: Result Section -->
        <div class="result-section">
            <h2>Detection Results</h2>
            <div class="result-container" id="animalResult">
                <ul>
                    {% if detections %}
                        {% for detection in detections %}
                            <li>{{ detection }}</li>
                        {% endfor %}
                    {% else %}
                        <p>No results yet</p>
                    {% endif %}
                </ul>
            </div>
            <div class="result-container" id="outputImageContainer">
                {% if output_image %}
                    <img src="{{ url_for('static', filename=output_image) }}" alt="Detected Output">
                {% else %}
                    <p>No output image yet</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- New Buttons Section: Back to Home and Reset -->
    <div class="buttons">
        <button id="backBtn" class="btn" onclick="window.location.href='/'">Back to Home</button>
        <button id="resetBtn" class="btn" onclick="resetResults()">Reset</button>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const imagePreview = document.getElementById('imagePreview');

        // Preview uploaded image in the left container
        fileInput.onchange = function(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
            };
            reader.readAsDataURL(file);
        };

        // Function to reset the result section
        function resetResults() {
            document.getElementById('animalResult').innerHTML = '<p>No results yet</p>';
            document.getElementById('outputImageContainer').innerHTML = '<p>No output image yet</p>';
            imagePreview.innerHTML = '<p>No image uploaded</p>';
        }
    </script>
</body>
</html>
"""

# Route for home page
@app.route('/')
def home():
    logged_in = 'username' in session
    return render_template_string(home_html, logged_in=logged_in)

# Route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.commit()
        cursor.close()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template_string(signup_html)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Login failed! Please check your username and password.', 'danger')
    return render_template_string(login_html)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Route for image upload and processing
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload'))

        # Save the uploaded image
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Perform detection
        response = model.predict(file_path).json()
        detections = [f"{pred['class']} with confidence {pred['confidence']:.2f}" for pred in response['predictions']]
        
        # Save output image with detections
        output_image = f"output_{file.filename}"
        output_image_path = os.path.join('static', output_image)

        # Draw the detections on the image
        image = cv2.imread(file_path)
        for prediction in response['predictions']:
            x = int(prediction['x'])
            y = int(prediction['y'])
            width = int(prediction['width'])
            height = int(prediction['height'])

            x1 = x - width // 2
            y1 = y - height // 2
            x2 = x + width // 2
            y2 = y + height // 2

            # Draw rectangle and label
            color = colors.get(prediction['class'], (255, 255, 255))
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image, prediction['class'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Save the processed image
        cv2.imwrite(output_image_path, image)

        return render_template_string(upload_html, detections=detections, output_image=output_image)
    return render_template_string(upload_html)

# Route for real-time detection (camera opens directly, no HTML page)
@app.route('/realtime')
def realtime():
    return redirect(url_for('camera_feed'))

class VideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

# Route to handle the real-time camera feed and object detection
@app.route('/camera_feed')
def camera_feed():
    # Start the video stream
    video_stream = VideoStream().start()

    # Open the camera feed in full-screen mode
    cv2.namedWindow("Real-time Animal Detection", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Real-time Animal Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        frame = video_stream.read()

        if frame is None:
            break

        # Perform detection on each frame
        response = model.predict(frame).json()

        # Draw the predictions on the frame
        for prediction in response['predictions']:
            x = int(prediction['x'])
            y = int(prediction['y'])
            width = int(prediction['width'])
            height = int(prediction['height'])

            x1 = x - width // 2
            y1 = y - height // 2
            x2 = x + width // 2
            y2 = y + height // 2

            # Draw rectangle and label
            color = colors.get(prediction['class'], (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, prediction['class'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Show the frame with detections
        cv2.imshow("Real-time Animal Detection", frame)

        # Close the window when 'q' or 'Q' is pressed
        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
            break

    video_stream.stop()  # Stop the video stream
    cv2.destroyAllWindows()  # Close all OpenCV windows
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)