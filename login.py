import cv2
import sqlite3
import bcrypt
import numpy as np
import face_recognition

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

# Store admin details
def register_admin(username, password, face_encoding):
    conn = sqlite3.connect("admin_db.sqlite")
    cursor = conn.cursor()
    
    # Check for duplicate face encoding
    cursor.execute("SELECT face_encoding FROM admin")
    existing_faces = cursor.fetchall()
    
    for stored_face in existing_faces:
        stored_encoding = np.frombuffer(stored_face[0], dtype=np.float64)
        if face_recognition.compare_faces([stored_encoding], face_encoding)[0]:
            print("Error: Face already registered.")
            conn.close()
            return False
    
    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Store in DB
    cursor.execute("INSERT INTO admin (username, password, face_encoding) VALUES (?, ?, ?)",
                   (username, hashed_pw, face_encoding.tobytes()))
    conn.commit()
    conn.close()
    print("Admin registered successfully!")
    return True

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
        
        # Verify password
        if bcrypt.checkpw(password.encode(), stored_hashed_pw):
            
            # Verify face
            if face_recognition.compare_faces([stored_face_encoding], captured_face_encoding)[0]:
                print("Login successful!")
                return True
            else:
                print("Face authentication failed!")
        else:
            print("Incorrect password!")
    else:
        print("Username not found!")
    
    return False

# Capture face
def capture_face():
    cam = cv2.VideoCapture(0)
    print("Capturing face... Look at the camera.")
    
    while True:
        ret, frame = cam.read()
        if not ret:
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            cam.release()
            cv2.destroyAllWindows()
            return face_encoding
        
        cv2.imshow("Face Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()
    return None

# Main
if __name__ == "__main__":
    init_db()
    
    choice = input("Do you want to (R)egister or (L)ogin? ").strip().lower()
    
    if choice == 'r':
        username = input("Enter username: ")
        password = input("Enter password: ")
        face_encoding = capture_face()
        
        if face_encoding is not None:
            register_admin(username, password, face_encoding)
        else:
            print("Face capture failed!")
    
    elif choice == 'l':
        username = input("Enter username: ")
        password = input("Enter password: ")
        face_encoding = capture_face()
        
        if face_encoding is not None:
            login_admin(username, password, face_encoding)
        else:
            print("Face capture failed!")
    else:
        print("Invalid option!")
