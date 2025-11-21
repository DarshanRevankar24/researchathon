# 🚀 **DEEPFAKE IMAGE AND VIDEO DETECTION**

A complete end-to-end system to detect whether an image or video is **AI-generated or real**, providing **confidence scores** and **explainable heatmaps**. Built using **PyTorch + FastAPI + Vanilla JS**, with a modern ChatGPT-style UI.

---

## 🧠 **What This Project Does**

- 🔍 Detects if an image or video is **REAL** or **AI-GENERATED**  
- 📊 Returns a **confidence score**  
- 🔥 Generates a **Grad-CAM heatmap** showing suspicious regions  
- 🖥️ Includes an interactive **chat-style frontend**  
- ⚡ Fast inference via **FastAPI backend**  
- 🎥 **Video detection**: Analyzes frames and averages results for final prediction

---

## 🏗️ **Tech Stack Used**

### 🟦 **Backend**
- Python  
- FastAPI  
- PyTorch  
- torchvision  
- PIL  
- OpenCV  
- NumPy  
 

### 🔥 **Machine Learning**
- CNN model trained in PyTorch  
- Softmax classification  
- Grad-CAM for explainability  
- Custom preprocessing pipeline  

---

## ⚙️ **How the System Works**

### 📌 **Image Detection Pipeline**

1. **Image Upload**: User drags or selects an image → Frontend sends it to the backend using `multipart/form-data`.
2. **Preprocessing**:
   - Convert to RGB  
   - Resize to **224×224**  
   - Normalize using ImageNet stats  
   - Convert to PyTorch tensor  
3. **Model Inference**:
   - CNN model runs a forward pass and outputs:
     - `REAL` or `FAKE`  
     - Confidence value  
     - Feature activations  
4. **Explainability via Heatmap**:
   - Grad-CAM identifies **where** the model looked while making the prediction.
   - Highlights suspicious areas like eyes, skin, background, and edges.
5. **Reason Generation (Rule-Based)**:
   - Based on heatmap regions, generate human-readable reasons:
     - Eyes highlighted → “Symmetry or reflection anomaly”
     - Skin region → “Over-smooth texture suggests synthetic origin”
     - Background → “Melted or repeating patterns”

### 📌 **Video Detection Pipeline**

1. **Frame Extraction**:
   - Extract one frame out of every 30 frames using OpenCV.
2. **Frame-Level Inference**:
   - Run each extracted frame through the same image detection pipeline.
3. **Temporal Aggregation**:
   - Compute the average confidence across all sampled frames.
   - Use majority voting to decide the final prediction (REAL or FAKE).
4. **Explainability for Video**:
   - Generate heatmaps for each analyzed frame.
   - Highlight suspicious frames and regions over time.

---

## 🎥 **How This Can Work for Videos**

By analyzing frames at intervals (e.g., one frame every 30 frames), the system effectively captures temporal inconsistencies and averages out the results for a robust final prediction. This method ensures that fleeting artifacts or inconsistencies in a single frame do not mislead the detection, providing a reliable assessment of the entire video.

---

## 🚀 **Why This Project Is Useful**

Just like phones detect spam calls and spam messages, this system can be integrated into apps to **warn users** when they interact with AI-generated or manipulated media. This is invaluable for:

- **Security apps**  
- **Verification systems**  
- **Social media filters**  
- **Identity protection**  
- **Digital forensics**

---

## 🔧 **How to Run**

```bash
git clone https://github.com/DarshanRevankar24/researchathon.git
cd researchathon

pip install -r requirements.txt
uvicorn main:app --reload
