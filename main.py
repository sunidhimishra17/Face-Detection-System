import os
import cv2
import dlib
import sqlite3
import bcrypt
import numpy as np
import face_recognition
import tkinter as tk
from tkinter import messagebox
from flask import Flask, render_template, Response, request, redirect, session, url_for, jsonify
from flask_restful import Api, Resource
from cryptography.fernet import Fernet
from tkinter import simpledialog
import pickle
from PIL import Image
from win10toast import ToastNotifier


app = Flask(__name__)
api = Api(app)

KNOWN_FACES_DIR = os.path.join(os.getcwd(), "known_faces")

file_path = "C:\\Users\\hp\\Documents\\Human Face Detection System\\known_faces\\known_person.jpg"
print("File exists:", os.path.exists(file_path))

# Generate a Fernet key and save it securely
KEY_FILE = "fernet_key.key"

def generate_key():
    """Generate and save a new encryption key if not already saved."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key():
    """Load the Fernet encryption key from file."""
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()
    
# Ensure the key exists
generate_key()
fernet = Fernet(load_key())

# Encrypt and decrypt functions
def encrypt_data(data):
    """Encrypts data using Fernet."""
    return fernet.encrypt(data)

def decrypt_data(data):
    """Decrypts data using Fernet."""
    return fernet.decrypt(data)

# Database setup
def init_db():
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        face_encoding BLOB
    )
    """)
    conn.commit()
    conn.close()
    
def create_database():
    """Initialize the SQLite database for storing face data."""
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    
    # Create admin table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        face_encoding BLOB
    )
    """)
    
    # Create faces table if it doesn't exist
    cursor.execute("""
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_username TEXT,
    name TEXT UNIQUE,
    encoding BLOB,
    FOREIGN KEY (admin_username) REFERENCES admin(username)
)
""")

    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")  # Debugging log

    
    # Store admin details
"""def register_admin(username, password, face_encoding):
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    
    cursor.execute("SELECT face_encoding FROM admin")
    existing_faces = cursor.fetchall()
    
    for stored_face in existing_faces:
        stored_encoding = np.frombuffer(stored_face[0], dtype=np.float64)
        if face_recognition.compare_faces([stored_encoding], face_encoding)[0]:
            return {"status": "error", "message": "Face already registered!"}
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    cursor.execute("INSERT INTO admin (username, password, face_encoding) VALUES (?, ?, ?)",
                   (username, hashed_pw, face_encoding.tobytes()))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Admin registered successfully!"}"""
    
def register_admin(username, password, face_encoding):
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM admin WHERE username = ?", (username,))
    if cursor.fetchone():
        return {"status": "error", "message": "Username already exists!"}

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO admin (username, password, face_encoding) VALUES (?, ?, ?)",
                   (username, hashed_pw, face_encoding.tobytes()))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Admin registered successfully!"}

@app.route('/register', methods=['POST'])
def register_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    face_encoding = np.array(data.get('face_encoding'))
    if not username or not password or face_encoding is None:
        return jsonify({"status": "error", "message": "Missing fields!"})
    return jsonify(register_admin(username, password, face_encoding))

# Authenticate admin
def login_admin(username, password, captured_face_encoding):
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    
    cursor.execute("SELECT password, face_encoding FROM admin WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hashed_pw, stored_face_encoding = result
        stored_face_encoding = np.frombuffer(stored_face_encoding, dtype=np.float64)
        
        if bcrypt.checkpw(password.encode(), stored_hashed_pw):
            if face_recognition.compare_faces([stored_face_encoding], captured_face_encoding)[0]:
                return {"status": "success", "message": "Login successful!"}
            else:
                return {"status": "error", "message": "Face authentication failed!"}
        else:
            return {"status": "error", "message": "Incorrect password!"}
    else:
        return {"status": "error", "message": "Username not found!"}
    
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    captured_face_encoding = np.array(data.get('face_encoding'))

    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT username, face_encoding FROM admin")
    admins = cursor.fetchall()
    conn.close()

    for username, stored_face_encoding in admins:
        stored_face_encoding = np.frombuffer(stored_face_encoding, dtype=np.float64)
        if face_recognition.compare_faces([stored_face_encoding], captured_face_encoding)[0]:
            session['username'] = username
            return jsonify({"status": "success", "message": f"Login successful for {username}"})

    return jsonify({"status": "error", "message": "Face not recognized"})

"""@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    face_encoding = np.array(data.get('face_encoding'))
    return jsonify(login_admin(username, password, face_encoding))"""

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

"""@app.route('/register', methods=['POST'])
def register_api():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    face_encoding = np.array(data.get('face_encoding'))
    
    if not username or not password or face_encoding is None:
        return jsonify({"status": "error", "message": "Missing fields!"})
    
    return jsonify(register_admin(username, password, face_encoding))"""
    
image_path = "C:\\Users\\hp\\Documents\\Human Face Detection System\\known_faces\\known_person.jpg"
try:
    img = Image.open(image_path)
    img = img.convert("RGB")  # Convert to standard format
    img.save(image_path, "JPEG")
    print("Image converted and saved successfully!")
except Exception as e:
    print("Error:", e)

# Initialize known face encodings and names
known_face_encodings = []
known_face_names = []

# Create a face detector
detector = dlib.get_frontal_face_detector()

# Settings
settings = {
    "recognitionThreshold": 1.0,
    "maxLogs": 100
}

DATABASE = "admin_db.sqlite"

try:
    img = face_recognition.load_image_file(image_path)
    print("✅ Image loaded successfully!")
except Exception as e:
    print("❌ Error loading image:", e)

def add_face_to_database(name, encoding):
    """Add a new face encoding to the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    encrypted_encoding = encrypt_data(pickle.dumps(encoding))
    cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, encrypted_encoding))
    conn.commit()
    conn.close()

def fetch_faces_from_database():
    """Fetch faces from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, encoding FROM faces")
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], pickle.loads(decrypt_data(row[1]))) for row in rows]

def load_known_faces():
    """Load known faces from the database."""
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    faces = fetch_faces_from_database()
    for name, encoding in faces:
        known_face_names.append(name)
        known_face_encodings.append(encoding)
        
@app.route('/get_known_faces')
def get_known_faces():
    """Get the list of known faces."""
    load_known_faces()
    return jsonify({"known_faces": known_face_names})

@app.route('/update_faces', methods=['POST'])
def update_faces():
    """Update the list of known faces."""
    load_known_faces()
    return jsonify({"status": "Faces updated successfully!"})

@app.route('/dashboard')
def dashboard():
    """Render the dashboard for managing known faces."""
    load_known_faces()
    return render_template('dashboard.html', known_faces=known_face_names, settings=settings)

def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/base')
def base():
    """Render the base for managing logo and app name."""
    return "Welcome to the Human Face Detection System!"

# RESTful API to retrieve face information
class FaceAPI(Resource):
    def get(self, name):
        """Retrieve information about a face by name."""
        load_known_faces()
        if name in known_face_names:
            index = known_face_names.index(name)
            return {"name": known_face_names[index], "encoding": known_face_encodings[index].tolist()}
        else:
            return {"message": "Face not found."}, 404

api.add_resource(FaceAPI, "/api/face/<string:name>")

# Function to calculate EAR (Eye Aspect Ratio)
def calculate_ear(left_eye, right_eye):
    """Calculate the Eye Aspect Ratio (EAR)."""
    def eye_aspect_ratio(eye):
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    return (left_ear + right_ear) / 2.0

def is_liveness_detected(frame, face_landmarks):
    """Detect liveness by checking if EAR is below a threshold."""
    left_eye = np.array(face_landmarks['left_eye'])
    right_eye = np.array(face_landmarks['right_eye'])
    ear = calculate_ear(left_eye, right_eye)
    return ear < EAR_THRESHOLD
EAR_THRESHOLD = 0.2 

def draw_face_rectangle(img, face_location, name):
    """Draw rectangle and label around detected face."""
    top, right, bottom, left = face_location
    cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
    label = name
    cv2.putText(img, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def handle_unknown_face(img, face_encoding):
    """Prompt user for a name for the unknown face and save it to the database."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    name = simpledialog.askstring("New Face Detected", "Enter the name of the new person:")
    root.quit()

    if name:
        add_face_to_database(name, face_encoding)
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
        send_alert(ALERT_EMAIL, f"New face detected: {name}")  # Send alert when a new face is added
    return name

def gen_frames():
    """Capture frames from the webcam and process them for face recognition."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    while True:
        try:
            success, frame = cap.read()
            if not success:
                print("Error: Failed to capture frame.")
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_rgb)

            # Skip processing if no faces detected
            if not face_locations:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                continue

            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            face_landmarks_list = face_recognition.face_landmarks(img_rgb)

            for face_encoding, face_location, face_landmarks in zip(face_encodings, face_locations, face_landmarks_list):
                name = "Unknown"

                if known_face_encodings:  # Avoid empty sequence error
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

                    if best_match_index is not None and face_distances[best_match_index] < 0.6:
                        name = known_face_names[best_match_index]
                    else:
                        name = handle_unknown_face(frame, face_encoding)

                if is_liveness_detected(frame, face_landmarks):
                    name += " (Liveness Detected)"

                draw_face_rectangle(frame, face_location, name)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        except Exception as e:
            print(f"Error in gen_frames: {e}")

    cap.release()

# Flask routes
@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video feed route for real-time face recognition.""" 
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

import os

KNOWN_FACES_DIR = os.path.join(os.getcwd(), "known_faces")  # Adjust directory name

@app.route('/add_face', methods=['GET', 'POST'])
def add_face():
    """Page to manually add a new face."""
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']
        if image:
            image_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
            image.save(image_path)

            img = face_recognition.load_image_file(image_path)
            face_encoding = face_recognition.face_encodings(img)
            if face_encoding:
                add_face_to_database(name, face_encoding[0])

        return redirect(url_for('dashboard'))
    return render_template('add_face.html')

@app.route('/delete_face/<name>')
def delete_face(name):
    """Delete a known face from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faces WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    load_known_faces()  # Reload known faces after deletion
    return redirect(url_for('dashboard')) 

if __name__ == "__main__":
    # Create database and load known faces initially
    create_database()
    load_known_faces()
    """app.run(debug=True)"""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug= True)
    
# Test Face Recognition Function
def test_face_recognition():
    """Test the face recognition functionality with encryption."""
    
    KNOWN_FACES_DIR = os.path.join(os.getcwd(), "known_faces")

    known_face_image_path = os.path.join(KNOWN_FACES_DIR, "known_person.jpg")  
    test_face_image_path = os.path.join(KNOWN_FACES_DIR, "test_person.jpg")

    if not os.path.exists(known_face_image_path):
        print(f"Error: Known face file {known_face_image_path} not found.")
        return
    
    if not os.path.exists(test_face_image_path):
        print(f"Error: Test face file {test_face_image_path} not found.")
        return

    print("Loading images for face recognition test...")

    # Load and encode known face
    known_face_img = face_recognition.load_image_file(known_face_image_path)
    known_face_encoding = face_recognition.face_encodings(known_face_img)[0]
    
    # Encrypt known face encoding
    encrypted_face = encrypt_data(pickle.dumps(known_face_encoding))

    # Store encrypted face encoding in the database
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", ("Known Person", encrypted_face))
    conn.commit()
    conn.close()

    # Load and encode test face
    test_face_img = face_recognition.load_image_file(test_face_image_path)
    test_face_encoding = face_recognition.face_encodings(test_face_img)[0]

    # Retrieve and decrypt the stored face encoding
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT encoding FROM faces WHERE name = ?", ("Known Person",))
    stored_face_enc = cursor.fetchone()[0]
    conn.close()
    
    decrypted_face = pickle.loads(decrypt_data(stored_face_enc))

    # Perform face recognition
    result = face_recognition.compare_faces([decrypted_face], test_face_encoding)

    if result[0]:
        print("Test Passed: The test face was successfully recognized.")
    else:
        print("Test Failed: The test face was not recognized.")

# Run the test
test_face_recognition()