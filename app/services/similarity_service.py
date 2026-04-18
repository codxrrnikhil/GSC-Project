from typing import Iterable

import numpy as np


def _cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    a = np.asarray(list(vec_a), dtype=np.float32)
    b = np.asarray(list(vec_b), dtype=np.float32)
    if a.size == 0 or b.size == 0 or a.shape != b.shape:
        return 0.0

    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _hamming_similarity(hash_a: str | None, hash_b: str | None) -> float:
    if not hash_a or not hash_b or len(hash_a) != len(hash_b):
        return 0.0
    distance = sum(ch1 != ch2 for ch1, ch2 in zip(hash_a, hash_b))
    max_len = max(len(hash_a), 1)
    return float(1.0 - (distance / max_len))


def detect_similarity(content_embedding, fingerprints: list[dict], content_hash: str | None = None):
    best_match = None
    best_score = 0.0

    for fp in fingerprints:
        emb_score = _cosine_similarity(content_embedding, fp.get("embedding", []))
        hash_score = _hamming_similarity(content_hash, fp.get("hash"))
        score = max(emb_score, hash_score)

        if score > best_score:
            best_score = score
            best_match = fp

    return {
        "similarity_score": best_score,
        "matched_asset_id": (best_match or {}).get("asset_id"),
    }
