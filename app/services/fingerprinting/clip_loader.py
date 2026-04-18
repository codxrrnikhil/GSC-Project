import threading

import torch
from transformers import CLIPModel, CLIPProcessor

_CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = None
_processor = None
_lock = threading.Lock()


def get_clip_components():
    global _model, _processor
    if _model is not None and _processor is not None:
        return _model, _processor, _device

    with _lock:
        if _model is None or _processor is None:
            _model = CLIPModel.from_pretrained(_CLIP_MODEL_NAME).to(_device)
            _model.eval()
            _processor = CLIPProcessor.from_pretrained(_CLIP_MODEL_NAME)
    return _model, _processor, _device
