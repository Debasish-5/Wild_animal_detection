
# Wild Animal Detection System

This project is a **Wild Animal Detection System** built using **Flask**, **OpenCV**, **Roboflow**, and **MySQL**. It provides a web interface for users to upload images or use real-time camera feed to detect and identify different wild animals using a trained machine learning model.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Routes](#routes)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Wild Animal Detection System allows users to:

- Sign up and log in to access detection features.
- Upload images for animal detection.
- Use a real-time camera feed to detect animals in live video.
- View the results with bounding boxes and labels drawn on detected animals.

The backend is built with **Flask**, utilizing **OpenCV** for image processing and **Roboflow** for object detection. **MySQL** is used for storing user details.

## Features

- **User Authentication**: Secure login and signup features using MySQL for storing user credentials.
- **Image Upload Detection**: Users can upload images to detect animals, with the results displayed on the same page.
- **Real-Time Detection**: Opens the camera feed to detect animals live, displaying bounding boxes and labels for each detected animal.
- **Animal Classes**: Detects a range of animals including fox, panda, tiger, bear, elephant, lion, and wolf.
- **Custom Styling**: Each detected animal class is highlighted in a unique color for better visualization.

## Technologies Used

- **Flask**: For creating the web application.
- **OpenCV**: For image and video processing.
- **Roboflow**: Pre-trained model for animal detection.
- **MySQL**: For storing user data.
- **HTML/CSS/JavaScript**: For building the frontend user interface.
- **Python**: Main programming language used in the backend.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/wild-animal-detection.git
   cd wild-animal-detection
   ```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Ensure you have OpenCV installed:

   ```bash
   pip install opencv-python
   ```

4. **MySQL Database Setup:**

   - Create a database named `wildlife_detection`.
   - Create a table named `users` with columns `id`, `username`, and `password`.

   ```sql
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(100) NOT NULL,
       password VARCHAR(100) NOT NULL
   );
   ```

5. **Set up Roboflow API Key:**

   - Sign up on [Roboflow](https://roboflow.com/).
   - Create a project and get the API key.
   - Replace `"JEhrwMUHZ23ZD3L5Mind"` in the code with your Roboflow API key.

## Setup

1. **Add Secret Key:**

   Replace the `app.secret_key` with a unique value:

   ```python
   app.secret_key = 'your_secret_key'
   ```

2. **Configure MySQL Connection:**

   Update `app.config` to match your MySQL configuration:

   ```python
   app.config['MYSQL_USER'] = 'your_mysql_user'
   app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
   ```

3. **Static Files and Templates:**

   - Add your CSS files in the `static` folder.
   - Customize the HTML templates as per your design preferences.

## Usage

1. **Start the Flask Server:**

   ```bash
   python app.py
   ```

2. **Access the Web Application:**

   Open a browser and navigate to `http://localhost:5000`.

3. **Sign Up and Log In:**

   - Create a new account using the Signup page.
   - Log in to access the detection features.

4. **Upload Image for Detection:**

   - Use the "Upload Image" feature to detect animals in an uploaded image.
   - View detection results and annotated images.

5. **Real-Time Detection:**

   - Click on "Real-time Detection" to open the camera feed.
   - Press 'q' or 'Q' to stop the camera feed.

## Project Structure

```
wild-animal-detection/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── templates/               # HTML templates (home, signup, login, etc.)
├── static/
│   ├── style.css            # Custom CSS styles for the web app
│   ├── upload.png           # Image icons for the UI
│   └── ...                  # Other static files (images, JS files)
├── uploads/                 # Directory to store uploaded images
└── README.md                # Project documentation
```

## Routes

- `/`: Home page with options for login/signup or access to detection features.
- `/signup`: Signup page for new users.
- `/login`: Login page for existing users.
- `/logout`: Logs out the user.
- `/upload`: Upload page for image detection.
- `/realtime`: Starts the real-time detection using the camera feed.
- `/camera_feed`: Handles the video stream and detection process.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
