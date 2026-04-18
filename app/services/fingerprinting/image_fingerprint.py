from PIL import Image
import imagehash
import torch

from app.services.fingerprinting.clip_loader import get_clip_components


def generate_image_fingerprint(image_path):
    clip_model, clip_processor, device = get_clip_components()
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:
        raise ValueError("Invalid image") from exc
    phash_value = imagehash.phash(image)

    inputs = clip_processor(images=image, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        vision_outputs = clip_model.vision_model(pixel_values=inputs["pixel_values"])
        pooled_output = vision_outputs.pooler_output
        image_features = clip_model.visual_projection(pooled_output)
        image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
    embedding = image_features.squeeze(0).detach().cpu().tolist()

    return {"hash": str(phash_value), "embedding": embedding}
