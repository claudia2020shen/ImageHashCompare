# ComfyUI Image Hash Compare Plugin

> **项目来源**: 本插件代码及文档源自 GitHub 项目 [claudia2020shen/ImageHashCompare](https://github.com/claudia2020shen/ImageHashCompare)。

## 📖 简介
这是一个专为 **ComfyUI** 设计的自定义节点（Custom Node），用于通过哈希算法比较两张图片的相似度。该节点一次性输出四种不同哈希算法的评分、布尔判断及详细调试信息，帮助用户在工作流中实现更精准的图像去重或相似度控制逻辑。

## 🚀 输出扩展 (Outputs)

该节点提供三类共 12 个输出端口：

### 1. 浮点数评分 (4x FLOAT)
分别对应四种算法的相似度得分，便于观察不同算法给出的分数差异：
- `score_phash`: 感知哈希得分
- `score_ahash`: 平均哈希得分
- `score_dhash`: 差异哈希得分
- `score_whash`: 小波哈希得分

### 2. 布尔阈值判断 (4x BOOLEAN)
分别指示上述四种算法的得分是否超过预设阈值。这允许在工作流中设置复杂的逻辑分支，例如：
> *“只有当 pHash 和 dHash 都认为相似时，才执行下一步”*

- `is_similar_phash`
- `is_similar_ahash`
- `is_similar_dhash`
- `is_similar_whash`

### 3. 调试信息 (4x STRING)
- `debug_info`: 打印每种算法的具体得分、汉明距离（Hamming Distance）和哈希值字符串。方便在控制台查看，或通过 `ShowText` 节点在工作流界面直接显示。

## ⚙️ 算法实现细节

本节点基于 Python 的 `imagehash` 库实现，具体包括：
- `imagehash.phash`
- `imagehash.average_hash`
- `imagehash.dhash`
- `imagehash.whash`

### 🛡️ 异常处理机制
针对 **wHash (小波哈希)** 对图像尺寸的严格要求（必须为 2 的幂次且大于等于特定值），代码中加入了 `try-except` 保护块：
- 如果某种算法因图片尺寸问题失败，该路输出将自动返回 `0.0` (Float) 和 `False` (Boolean)。
- **优势**: 确保单个算法的失败不会导致整个 ComfyUI 节点崩溃，保证工作流的稳定性。

## 🧠 算法特性简析

| 算法 | 全称 | 特性描述 | 推荐场景 |
| :--- | :--- | :--- | :--- |
| **pHash** | Perceptual Hash (感知哈希) | **推荐作为主要指标**。对图像缩放、轻微压缩、亮度变化有极好的鲁棒性，最能代表“人眼看起来像不像”。 | 通用相似度检测 |
| **aHash** | Average Hash (平均哈希) | 计算速度**最快**，但对亮度变化非常敏感。若两张图仅亮度不同，得分会很低。 | 快速初筛 |
| **dHash** | Differential Hash (差异哈希) | 基于梯度（边缘）。对图像的**几何结构**敏感，对颜色不敏感。即使颜色完全不同但结构一致，得分依然很高。 | 结构/构图比对 |
| **wHash** | Wavelet Hash (小波哈希) | 基于小波变换，通常比 pHash **更精确**，但对图像尺寸要求严格，计算稍慢。 | 高精度比对 |

## 💡 使用建议
通过一次性输出这四个维度的数值，您可以非常精准地控制 ComfyUI 的工作流逻辑，灵活应对不同的图像去重或筛选需求。

---
*更多详细信息请访问: [https://github.com/claudia2020shen/ImageHashCompare](https://github.com/claudia2020shen/ImageHashCompare)*


# ComfyUI Image Hash Compare Plugin

> **Source**: This plugin code and documentation originate from the GitHub project [claudia2020shen/ImageHashCompare](https://github.com/claudia2020shen/ImageHashCompare).

## 📖 Introduction
This is a custom node designed specifically for **ComfyUI** to compare the similarity of two images using hash algorithms. The node outputs scores, boolean judgments, and detailed debug information for four different hash algorithms simultaneously, enabling users to implement precise image deduplication or similarity control logic within their workflows.

## 🚀 Output Extensions

The node provides three categories of outputs, totaling 12 ports:

### 1. Float Scores (4x FLOAT)
Corresponding to the similarity scores of the four algorithms, allowing you to observe the differences in scores given by each method:
- `score_phash`: Perceptual Hash score
- `score_ahash`: Average Hash score
- `score_dhash`: Difference Hash score
- `score_whash`: Wavelet Hash score

### 2. Boolean Threshold Checks (4x BOOLEAN)
Indicates whether the score for each of the four algorithms has exceeded the preset threshold. This allows for setting up complex logic branches in your workflow, for example:
> *"Proceed to the next step only if both pHash and dHash consider the images similar."*

- `is_similar_phash`
- `is_similar_ahash`
- `is_similar_dhash`
- `is_similar_whash`

### 3. Debug Information (STRING)
- `debug_info`: Prints the specific score, Hamming Distance, and hash value string for each algorithm. This makes it easy to view details in the console or via a `ShowText` node directly in the workflow interface.

## ⚙️ Algorithm Implementation Details

This node is implemented using Python's `imagehash` library, specifically utilizing:
- `imagehash.phash`
- `imagehash.average_hash`
- `imagehash.dhash`
- `imagehash.whash`

### 🛡️ Exception Handling
Specific attention is paid to **wHash (Wavelet Hash)**, which has strict requirements for image dimensions (must be a power of 2 and greater than or equal to a certain value). A `try-except` block has been added to the code:
- If an algorithm fails due to image dimension issues, that specific output path will automatically return `0.0` (Float) and `False` (Boolean).
- **Benefit**: This ensures that a failure in a single algorithm does not crash the entire ComfyUI node, maintaining workflow stability.

## 🧠 Algorithm Characteristics Analysis

| Algorithm | Full Name | Characteristics | Recommended Use Case |
| :--- | :--- | :--- | :--- |
| **pHash** | Perceptual Hash | **Recommended as the primary metric**. Exhibits strong robustness against image scaling, minor compression, and brightness variations. Best represents "visual similarity to the human eye". | General similarity detection |
| **aHash** | Average Hash | **Fastest calculation speed**, but highly sensitive to brightness changes. If two images differ only in brightness, the score will be very low. | Quick initial screening |
| **dHash** | Difference Hash | Based on gradients (edges). Sensitive to the **geometric structure** of the image, insensitive to color. Scores remain high even if colors are completely different but the structure is identical. | Structure/Composition comparison |
| **wHash** | Wavelet Hash | Based on wavelet transform. Generally **more accurate** than pHash, but has strict image size requirements and is slightly slower to compute. | High-precision comparison |

## 💡 Usage Tips
By outputting these four values simultaneously, you can control your ComfyUI workflow logic with great precision, flexibly addressing various image deduplication or filtering needs.

---
*For more details, please visit: [https://github.com/claudia2020shen/ImageHashCompare](https://github.com/claudia2020shen/ImageHashCompare)*
