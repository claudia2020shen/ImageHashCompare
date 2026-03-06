# 从 node.py 导入所有的映射字典
from .node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 将导入的内容暴露给 ComfyUI
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 打印加载信息（可选，方便在控制台看到节点已加载）
if NODE_CLASS_MAPPINGS:
    print(f"Loaded ImageHashCompareMulti Node: {list(NODE_CLASS_MAPPINGS.keys())}")
