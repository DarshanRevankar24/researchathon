import torch
import torch.nn as nn
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image
import io
import tempfile

from processors.image_processor import SimpleCNN  # Reuse same image model


class VideoProcessor:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Same transform as image_processor
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        self.class_names = ['fake', 'real']

    # -----------------------------------------------------------
    # Load Model
    # -----------------------------------------------------------
    def load_model(self, model_path: str):
        """Load the trained SimpleCNN model."""
        self.model = SimpleCNN()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print(f"🎥 Video model loaded from {model_path}")

    # -----------------------------------------------------------
    # Extract frames
    # -----------------------------------------------------------
    def extract_frames(self, video_bytes, skip_frames=30):
        """
        Extract frames from uploaded video using a temporary file.
        OpenCV CANNOT read from BytesIO directly — must save to actual file.
        """
        # Save uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes)
            temp_path = tmp.name

        # Load video
        capture = cv2.VideoCapture(temp_path)

        if not capture.isOpened():
            raise ValueError("VideoCapture failed to open video")

        frames = []
        frame_index = 0

        while True:
            ret, frame = capture.read()
            if not ret:  # No more frames
                break

            # Extract 1 frame per N frames
            if frame_index % skip_frames == 0:
                frame = cv2.resize(frame, (224, 224))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)

            frame_index += 1

        capture.release()
        return frames

    # -----------------------------------------------------------
    # Predict each frame
    # -----------------------------------------------------------
    def predict_frames(self, frames):
        """
        Run the image model on extracted frames.
        Returns list of probabilities.
        """
        probabilities = []

        for frame in frames:
            pil_img = Image.fromarray(frame)
            tensor = self.transform(pil_img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                output = self.model(tensor)
                prob = torch.sigmoid(output).item()  # Probability of REAL class
                probabilities.append(prob)

        return np.array(probabilities)

    # -----------------------------------------------------------
    # Full video prediction pipeline
    # -----------------------------------------------------------
    def predict_video(self, video_bytes):
        """Extract frames → run model → combine results."""
        if self.model is None:
            self.load_model("D:/hackathonn/researchaton/backend/processors/best_model.pth")

        frames = self.extract_frames(video_bytes)

        if len(frames) == 0:
            raise ValueError("No frames extracted from video.")

        probs = self.predict_frames(frames)

        mean_prob = probs.mean()  # Average probability of REAL

        predicted_index = 1 if mean_prob > 0.5 else 0
        label = self.class_names[predicted_index]
        is_fake = (label == "fake")

        confidence = 1 - mean_prob if is_fake else mean_prob

        return {
            "prediction": label,
            "confidence": float(confidence),
            "is_fake": is_fake,
            "frame_scores": probs.tolist(),  # Optional
        }

    # -----------------------------------------------------------
    # Wrapper so your FastAPI route still works
    # -----------------------------------------------------------
    def process_video(self, video_bytes):
        return self.predict_video(video_bytes)


# Global instance
video_processor = VideoProcessor()
