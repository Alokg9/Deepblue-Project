# 📏 Estimating Physical Attributes and Object Dimensions from Selfies  

## 🚀 Overview  
Accurately measuring human attributes (e.g., height, body proportions) and object dimensions often requires specialized tools like laser scanners or depth cameras.  
This project **leverages smartphone cameras and AI-powered computer vision** to estimate dimensions from **selfies and object images**—all without extra hardware!  

📸 Capture a selfie or an object image → 🧠 AI processes it → 📏 Get precise measurements  

## 🏆 Key Features  
✔ Human & Object Detection – Uses Detectron2/Faster R-CNN for classification.  
✔ Pixel-to-Physical Conversion – Advanced calibration algorithms ensure precision.  
✔ AI-Powered Preprocessing – GAN-enhanced lighting correction for better results.  
✔ Mobile & Cloud Integration – Seamless experience with Firebase and AWS.  
✔ Secure & Scalable – Built with FastAPI, Redis caching, and JWT authentication.  

## 🔧 Tech Stack  

### 📱 Frontend (Mobile App)  
- Flutter (Dart) – Cross-platform app for image capture and result visualization.  

### ⚙️ Backend (AI Processing & API)  
- FastAPI (Python) – High-performance REST API.  
- OpenCV – Image processing (Canny Edge Detection, Gaussian Blur).  
- Detectron2 / Faster-RCNN – AI-driven human/object detection.  
- PostgreSQL / Firebase – Secure storage of measurements and user history.  

### ☁️ Deployment & Infrastructure  
- AWS EC2, ALB & Redis – Cloud hosting and caching for fast performance.  
- JWT Authentication – Ensures secure user access.  
- AWS Shield – Protection against DDoS attacks.  

## 📜 How It Works  

1️⃣ Take a Selfie or Capture an Object using the Flutter app.  
2️⃣ Upload Image to the Backend (processed via FastAPI).  
3️⃣ AI Model Analyzes & Extracts Measurements from detected key points.  
4️⃣ Pixel-to-Physical Mapping converts dimensions to cm/inches.  
5️⃣ Results Displayed in the app & stored securely.  

## 🔥 Getting Started  

### 🛠 Prerequisites  
- Flutter SDK (for frontend development)  
- Python 3.8+ (for backend)  
- AWS Account (for cloud deployment)  

### 🚀 Installation  

```bash
# Clone the repo
git clone https://github.com/YourUsername/YourProject.git
cd YourProject

# Install backend dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
 ```
🎯 Why This Matters
With the growing demand for contactless and accessible measurement tools, this project brings AI-powered precision to everyday smartphone users, empowering applications in health, product design, and home improvement.

🤝 Contributing
Contributions are welcome! Fork this repo, make changes, and submit a PR.

📜 License
This project is licensed under the MIT License.

📩 Contact
📧 Email: alok.gupta.bnp@gmail.com
🔗 LinkedIn: https://www.linkedin.com/in/alok-gupta-333a72224/
