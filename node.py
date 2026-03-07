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
                "hash_size": ("INT", {"default": 32, "min": 8, "max": 64, "step": 8, "tooltip": "哈希图大小 (N x N)，总比特数为 N*N"}),
                "threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "相似度阈值 (0-1)"}),
            },
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", "STRING")
    RETURN_NAMES = ("score_phash", "score_ahash", "score_dhash", "score_whash", "bool_phash", "bool_ahash", "bool_dhash", "bool_whash", "debug_info")
    FUNCTION = "compare_multi_hashes"
    CATEGORY = "image/utils"

    def tensor_to_pil(self, tensor):
        """将 ComfyUI Tensor [B,H,W,C] (0-1 float) 转换为 PIL Image (0-255 uint8)"""
        if len(tensor.shape) == 4:
            img_tensor = tensor[0].cpu().numpy()
        else:
            img_tensor = tensor.cpu().numpy()
        
        # 关键：缩放并裁剪到 0-255，转为 uint8
        img_array = np.clip(img_tensor * 255.0, 0, 255).astype(np.uint8)
        
        # 去除 Alpha 通道如果存在
        if img_array.shape[-1] == 4:
            img_array = img_array[:, :, :3]
            
        return Image.fromarray(img_array)

    def get_hamming_distance(self, hash_a, hash_b):
        """
        计算两个 ImageHash 对象之间的汉明距离。
        优先使用库自带的减法，失败则回退到手动二进制计算。
        """
        try:
            # 尝试直接使用库的重载运算符
            dist = hash_a - hash_b
            # 简单验证：如果距离为0但哈希字符串不同，说明库计算有误，触发异常进入手动模式
            if dist == 0 and str(hash_a) != str(hash_b):
                raise ValueError("Library subtraction returned 0 for different hashes.")
            return dist
        except Exception:
            # 手动计算模式：Hex -> Int -> XOR -> Count Bits
            try:
                hex_a = str(hash_a)
                hex_b = str(hash_b)
                int_a = int(hex_a, 16)
                int_b = int(hex_b, 16)
                xor_val = int_a ^ int_b
                return bin(xor_val).count('1')
            except:
                return -1 # 标记为计算错误

    def calculate_similarity(self, hash_a, hash_b, hash_size):
        """
        计算相似度：1 - (距离 / 总比特数)
        总比特数 = hash_size * hash_size
        """
        distance = self.get_hamming_distance(hash_a, hash_b)
        
        if distance < 0:
            return 0.0
            
        # 【关键修复】分母必须是总比特数，而不是十六进制字符串长度
        total_bits = hash_size * hash_size
        
        if total_bits == 0:
            return 0.0
            
        similarity = 1.0 - (distance / total_bits)
        return max(0.0, min(1.0, similarity))

    def compare_multi_hashes(self, image_a, image_b, hash_size, threshold):
        debug_lines = []
        
        # 1. 图像转换
        try:
            pil_a = self.tensor_to_pil(image_a)
            pil_b = self.tensor_to_pil(image_b)
            debug_lines.append(f"Images OK: A={pil_a.size}, B={pil_b.size}")
        except Exception as e:
            err_msg = f"Image conversion error: {str(e)}"
            print(err_msg)
            return (0.0, 0.0, 0.0, 0.0, False, False, False, False, err_msg)

        # 2. 定义算法
        algorithms = [
            ("pHash", lambda img: imagehash.phash(img, hash_size=hash_size)),
            ("aHash", lambda img: imagehash.average_hash(img, hash_size=hash_size)),
            ("dHash", lambda img: imagehash.dhash(img, hash_size=hash_size)),
            ("wHash", lambda img: imagehash.whash(img, hash_size=hash_size)),
        ]

        scores = []
        bools = []

        # 3. 循环计算
        for name, func in algorithms:
            try:
                h_a = func(pil_a)
                h_b = func(pil_b)
                
                # 记录哈希值用于调试
                debug_lines.append(f"{name}: HashA={str(h_a)} | HashB={str(h_b)}")
                
                # 计算相似度和布尔值
                score = self.calculate_similarity(h_a, h_b, hash_size)
                is_similar = score >= threshold
                
                scores.append(score)
                bools.append(is_similar)
                
                # 记录详细结果
                dist = self.get_hamming_distance(h_a, h_b)
                debug_lines.append(f"  -> Dist: {dist}, Score: {score:.4f}, Match: {is_similar}")
                
            except Exception as e:
                err_msg = f"{name} Error: {str(e)}"
                print(err_msg)
                debug_lines.append(err_msg)
                scores.append(0.0)
                bools.append(False)

        # 4. 返回结果 (顺序必须严格对应 RETURN_TYPES)
        return (
            scores[0], scores[1], scores[2], scores[3],  # 4个 Float
            bools[0], bools[1], bools[2], bools[3],      # 4个 Boolean
            "\n".join(debug_lines)                       # 1个 String
        )

# 注册字典
NODE_CLASS_MAPPINGS = {
    "ImageHashCompareMulti": ImageHashCompareMulti
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageHashCompareMulti": "Image Hash Compare (All Algorithms)"
}
