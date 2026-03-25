# Face-Detection-System
A high-performance, real-time face detection application built using Python and OpenCV. This project demonstrates the implementation of computer vision algorithms to identify and locate human faces in both static images and live video streams.

# Key Features
Real-time detection: Processes live video feed from a webcam with minimal latency.

Image Processing: Capable of detecting multiple faces within a single static image.

Haar Cascade Implementation: Utilizes pre-trained XML classifiers for robust feature extraction.

Visual Feedback: Draws bounding boxes around detected faces with real-time coordinate tracking.
   
# Tech Stack
Language: Python 3.x

Library: OpenCV (Open Source Computer Vision Library)

Tools: NumPy (for array manipulation)

# Project Structure
├── data/               # Pre-trained Haar Cascade XML files

├── images/             # Sample images for testing

├── src/                # Main source code files

│   └── face_detect.py  # Primary detection script

└── requirements.txt    # List of dependencies

# How to Run
Clone the repository: 
git clone https://github.com/sunidhimishra17/Face-Detection-System.git

Install dependencies:
pip install opencv-python numpy

Run the application:
python src/face_detect.py

# Future Enhancements
​Integration of Deep Learning (CNN) models for higher accuracy in low-light conditions.

​Adding Face Recognition capabilities to identify specific individuals.

​Developing a web-based interface using Streamlit or Flask.
