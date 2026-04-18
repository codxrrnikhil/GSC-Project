from PIL import Image
import imagehash
import torch
from transformers import CLIPModel, CLIPProcessor


_CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
_device = "cuda" if torch.cuda.is_available() else "cpu"
_clip_model = CLIPModel.from_pretrained(_CLIP_MODEL_NAME).to(_device)
_clip_model.eval()
_clip_processor = CLIPProcessor.from_pretrained(_CLIP_MODEL_NAME)


def generate_image_fingerprint(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:
        raise ValueError("Invalid image") from exc
    phash_value = imagehash.phash(image)

    inputs = _clip_processor(images=image, return_tensors="pt")
    inputs = {key: value.to(_device) for key, value in inputs.items()}
    with torch.no_grad():
        vision_outputs = _clip_model.vision_model(pixel_values=inputs["pixel_values"])
        pooled_output = vision_outputs.pooler_output
        image_features = _clip_model.visual_projection(pooled_output)
        image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
    embedding = image_features.squeeze(0).detach().cpu().tolist()

    return {"hash": str(phash_value), "embedding": embedding}
