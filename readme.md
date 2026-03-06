用于comfyui的插件，用于两张图片使用hash比较
输出扩展：
4个 FLOAT 输出：分别对应 score_phash, score_ahash, score_dhash, score_whash。你可以观察到不同算法给出的分数差异。
4个 BOOLEAN 输出：分别对应上述四种算法是否超过阈值。这允许你在工作流中设置更复杂的逻辑（例如：“只有当 pHash 和 dHash 都认为相似时，才执行下一步”）。
4个 STRING 输出：debug_info 会打印出每种算法的具体得分、汉明距离和哈希值字符串，方便你在控制台或通过 ShowText 节点查看。
算法实现细节：
使用了 imagehash.phash, average_hash, dhash, whash。
增加了异常处理：whash (小波哈希) 对图像尺寸有特定要求（必须是2的幂次且大于等于某个值），代码中加入了 try-except 块，如果某种算法因图片尺寸问题失败，该路输出会返回 0.0 和 False，而不会导致整个节点崩溃。

算法特性简析（供参考）
pHash (感知哈希)：推荐作为主要指标。对图像缩放、轻微压缩、亮度变化都有很好的鲁棒性，最能代表“人眼看起来像不像”。
aHash (平均哈希)：计算最快，但对亮度变化非常敏感。如果两张图只是亮度不同，这个分数会很低。
dHash (差异哈希)：基于梯度（边缘）。对图像的几何结构敏感，对颜色不敏感。如果两张图结构一样但颜色完全不同，这个分数依然会很高。
wHash (小波哈希)：基于小波变换，通常比 pHash 更精确，但对图像尺寸要求严格，计算稍慢。
通过一次性输出这四个值，你可以非常精准地控制你的工作流逻辑！


A custom node for comfyui, used for comparing two images using hash and outputting extensions: 4 FLOAT outputs: corresponding to score_phash, score_ahash, score_dhash, and score_whash respectively. You can observe the score differences given by different algorithms.
4 Boolean outputs: one for each of the four algorithms mentioned above, indicating whether they have exceeded the threshold. This allows you to set up more complex logic in your workflow (e.g., "only proceed to the next step if both pHash and dHash consider it similar").
4 STRING outputs: debug_info will print out the specific score, Hamming distance, and hash value string for each algorithm, making it easy for you to view on the console or through the ShowText node.
Algorithm implementation details: imagehash.phash, average_hash, dhash, and whash were used.
Exception handling has been added: whash (wavelet hash) has specific requirements for image size (it must be a power of 2 and greater than or equal to a certain value). A try-except block has been added to the code. If an algorithm fails due to an image size issue, the output for that path will return 0.0 and False, without causing the entire node to crash.

A brief analysis of algorithm characteristics (for reference): pHash (Perceptual Hashing): Recommended as the primary metric. It exhibits strong robustness against image scaling, minor compression, and brightness variations, and best represents "whether it looks similar to the human eye".
aHash (Average Hash): It has the fastest calculation speed, but is highly sensitive to brightness changes. If two images differ only in brightness, this score will be very low.
dHash (differential hashing): Based on gradients (edges). Sensitive to the geometric structure of the image, insensitive to color. If two images have the same structure but completely different colors, this score will still be high.
wHash (Wavelet Hash): Based on wavelet transform, it is generally more accurate than pHash, but it has strict requirements on image size and is slightly slower in computation.
By outputting these four values at once, you can control your workflow logic with great precision!
