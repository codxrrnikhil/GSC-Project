import cv2
import numpy as np
import torch
from PIL import Image

from app.services.fingerprinting.clip_loader import get_clip_components


def generate_video_fingerprint(video_path):
    clip_model, clip_processor, device = get_clip_components()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 1

    frame_step = max(int(fps), 1)
    frame_index = 0
    embeddings = []
    max_frames = 30

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % frame_step == 0 and len(embeddings) < max_frames:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            inputs = clip_processor(images=pil_image, return_tensors="pt")
            inputs = {key: value.to(device) for key, value in inputs.items()}
            with torch.no_grad():
                vision_outputs = clip_model.vision_model(pixel_values=inputs["pixel_values"])
                pooled_output = vision_outputs.pooler_output
                image_features = clip_model.visual_projection(pooled_output)
                image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
            embeddings.append(image_features.squeeze(0).detach().cpu().numpy())

        frame_index += 1
        if len(embeddings) >= max_frames:
            break

    cap.release()

    if not embeddings:
        raise ValueError("No frames extracted")

    avg_embedding = np.mean(np.array(embeddings), axis=0)
    norm = np.linalg.norm(avg_embedding)
    if norm > 0:
        avg_embedding = avg_embedding / norm

    return {"hash": None, "embedding": avg_embedding.tolist()}
