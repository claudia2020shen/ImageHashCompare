import torch
import numpy as np
from PIL import Image
import imagehash

class ImageHashCompareMulti:
    """
    同时使用四种哈希算法 (pHash, aHash, dHash, wHash) 比较两张图片的相似度
    输出每种算法的相似度分数 (0.0-1.0) 和是否超过阈值的布尔值
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "hash_size": ("INT", {"default": 32, "min": 8, "max": 64, "step": 8, "tooltip": "哈希图的大小"}),
                "threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "判定相似的阈值"}),
            },
        }

    # 定义输出类型：4个浮点数分数 + 4个布尔值 + 1个调试字符串
    RETURN_TYPES = (
        "FLOAT", "FLOAT", "FLOAT", "FLOAT",  # 相似度分数: pHash, aHash, dHash, wHash
        "BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN", # 是否相似: pHash, aHash, dHash, wHash
        "STRING" # 调试信息
    )
    
    RETURN_NAMES = (
        "score_phash", "score_ahash", "score_dhash", "score_whash",
        "bool_phash", "bool_ahash", "bool_dhash", "bool_whash",
        "debug_info"
    )
    
    FUNCTION = "compare_multi_hashes"
    CATEGORY = "image/utils"

    def tensor_to_pil(self, tensor):
        """将 ComfyUI 的 IMAGE Tensor 转换为 PIL Image"""
        # 确保取第一张图，处理可能的 batch 维度
        if len(tensor.shape) == 4:
            img_tensor = tensor[0].cpu().numpy()
        else:
            img_tensor = tensor.cpu().numpy()
            
        img_array = (img_tensor * 255).astype(np.uint8)
        
        # 如果通道数是 1 (灰度)，需要特殊处理，但通常 ComfyUI 是 RGB/RGBA
        if img_array.shape[-1] == 4:
            # 去掉 Alpha 通道
            img_array = img_array[:, :, :3]
            
        return Image.fromarray(img_array)

    def calculate_similarity(self, hash_a, hash_b, hash_size):
        """计算两个 hash 对象的相似度 (0.0 - 1.0)"""
        try:
            # imagehash 对象支持减法运算，返回汉明距离
            distance = hash_a - hash_b
            
            # 最大可能距离 = hash_size * hash_size (对于 dhash 通常是 hash_size * (hash_size+1) 等，但这里统一估算)
            # 为了更精确，我们直接获取 hash 的二进制长度
            max_distance = len(hash_a.hash) * len(hash_a.hash[0]) if hasattr(hash_a, 'hash') else hash_size * hash_size
            
            # 防止除以零或逻辑错误，重新获取实际位长
            # imagehash 的不同算法生成的矩阵大小可能略有不同，最稳妥的方式是直接看二进制串长度
            bin_a = str(hash_a)
            bin_b = str(hash_b)
            
            # 如果长度不一致（极少见情况），取较短的长度计算，或者报错
            if len(bin_a) != len(bin_b):
                min_len = min(len(bin_a), len(bin_b))
                bin_a = bin_a[:min_len]
                bin_b = bin_b[:min_len]
                max_distance = min_len
            else:
                max_distance = len(bin_a)

            # 重新计算准确的汉明距离 (通过字符串比对更稳妥，虽然 imagehash 重载了减号，但有时会有精度问题)
            # 实际上 imagehash 的减法就是汉明距离，直接用那个即可，但为了通用性我们信任库函数
            # 修正：直接使用库函数的减法结果作为 distance
            distance = hash_a - hash_b
            
            # 归一化相似度
            similarity = 1.0 - (distance / max_distance)
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def compare_multi_hashes(self, image_a, image_b, hash_size, threshold):
        # 转换 Tensor 到 PIL
        try:
            pil_a = self.tensor_to_pil(image_a)
            pil_b = self.tensor_to_pil(image_b)
        except Exception as e:
            return (0.0, 0.0, 0.0, 0.0, False, False, False, False, f"Image conversion error: {str(e)}")

        results = []
        debug_lines = []

        # 定义要计算的算法列表
        # 格式: (名称, 函数引用)
        algorithms = [
            ("pHash", lambda img: imagehash.phash(img, hash_size=hash_size)),
            ("aHash", lambda img: imagehash.average_hash(img, hash_size=hash_size)),
            ("dHash", lambda img: imagehash.dhash(img, hash_size=hash_size)),
            ("wHash", lambda img: imagehash.whash(img, hash_size=hash_size)),
        ]

        scores = []
        bools = []

        for name, func in algorithms:
            try:
                h_a = func(pil_a)
                h_b = func(pil_b)
                
                score = self.calculate_similarity(h_a, h_b, hash_size)
                is_similar = score >= threshold
                
                scores.append(score)
                bools.append(is_similar)
                
                dist = h_a - h_b
                debug_lines.append(f"{name}: Score={score:.4f}, Dist={dist}, Hash={str(h_a)}")
                
            except Exception as e:
                # 如果某种算法失败（例如 whash 对尺寸有严格要求），返回 0
                scores.append(0.0)
                bools.append(False)
                debug_lines.append(f"{name}: Error - {str(e)}")

        # 解包结果以匹配 RETURN_TYPES 顺序
        # 顺序: p, a, d, w (scores) -> p, a, d, w (bools) -> debug
        final_scores = scores # [p, a, d, w]
        final_bools = bools   # [p, a, d, w]
        
        debug_str = "\n".join(debug_lines)

        return (
            final_scores[0], final_scores[1], final_scores[2], final_scores[3], # 4 floats
            final_bools[0], final_bools[1], final_bools[2], final_bools[3],     # 4 booleans
            debug_str                                                           # 1 string
        )

# 节点注册
NODE_CLASS_MAPPINGS = {
    "ImageHashCompareMulti": ImageHashCompareMulti
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageHashCompareMulti": "Image Hash Compare (All Algorithms)"
}
