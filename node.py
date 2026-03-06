import torch
import numpy as np
from PIL import Image
import imagehash

class ImageHashCompareMulti:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "hash_size": ("INT", {"default": 32, "min": 8, "max": 64, "step": 8}),
                "threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "STRING")
    RETURN_NAMES = ("score_phash", "score_ahash", "score_dhash", "score_whash", "bool_phash", "bool_ahash", "bool_dhash", "bool_whash", "debug_info")
    FUNCTION = "compare_multi_hashes"
    CATEGORY = "image/utils"

    def tensor_to_pil(self, tensor):
        if len(tensor.shape) == 4:
            img_tensor = tensor[0].cpu().numpy()
        else:
            img_tensor = tensor.cpu().numpy()
        img_array = (img_tensor * 255).astype(np.uint8)
        if img_array.shape[-1] == 4:
            img_array = img_array[:, :, :3]
        return Image.fromarray(img_array)

    def calculate_similarity(self, hash_a, hash_b):
        try:
            distance = hash_a - hash_b
            # 获取哈希位的总长度
            max_distance = len(str(hash_a)) 
            if max_distance == 0: return 0.0
            similarity = 1.0 - (distance / max_distance)
            return max(0.0, min(1.0, similarity))
        except:
            return 0.0

    def compare_multi_hashes(self, image_a, image_b, hash_size, threshold):
        try:
            pil_a = self.tensor_to_pil(image_a)
            pil_b = self.tensor_to_pil(image_b)
        except Exception as e:
            return (0.0, 0.0, 0.0, 0.0, False, False, False, False, f"Image conversion error: {str(e)}")

        algorithms = [
            ("pHash", lambda img: imagehash.phash(img, hash_size=hash_size)),
            ("aHash", lambda img: imagehash.average_hash(img, hash_size=hash_size)),
            ("dHash", lambda img: imagehash.dhash(img, hash_size=hash_size)),
            ("wHash", lambda img: imagehash.whash(img, hash_size=hash_size)),
        ]

        scores = []
        bools = []
        debug_lines = []

        for name, func in algorithms:
            try:
                h_a = func(pil_a)
                h_b = func(pil_b)
                score = self.calculate_similarity(h_a, h_b)
                is_similar = score >= threshold
                scores.append(score)
                bools.append(is_similar)
                debug_lines.append(f"{name}: Score={score:.4f}, Dist={h_a - h_b}")
            except Exception as e:
                scores.append(0.0)
                bools.append(False)
                debug_lines.append(f"{name}: Error - {str(e)}")

        return (
            scores[0], scores[1], scores[2], scores[3],
            bools[0], bools[1], bools[2], bools[3],
            "\n".join(debug_lines)
        )

NODE_CLASS_MAPPINGS = {
    "ImageHashCompareMulti": ImageHashCompareMulti
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageHashCompareMulti": "Image Hash Compare (All Algorithms)"
}
