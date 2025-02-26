import torch
import numpy as np
from PIL import Image
import traceback

def tensor_to_pil(tensor):
    """将图像张量转换为PIL图像（兼容4D/3D张量）"""
    try:
        # 转换为CPU张量
        image = tensor.cpu().detach()
        
        # 处理不同维度
        if len(image.shape) == 4:
            image = image[0]  # 取批次中第一张
        if len(image.shape) == 3 and image.shape[0] in [1, 3, 4]:
            image = image.permute(1, 2, 0)  # CHW -> HWC
            
        # 转换为numpy数组
        image = (image * 255).clamp(0, 255).byte().numpy()
        
        # 处理通道数
        if image.shape[-1] == 1:
            image = np.concatenate([image]*3, axis=-1)
        elif image.shape[-1] == 4:
            image = image[..., :3]  # 移除Alpha通道
            
        return Image.fromarray(image)
    except Exception as e:
        print(f"❌ 图像处理失败: {traceback.format_exc()}")
        return None

def validate_image_url(url):
    """验证图片URL格式"""
    if not url.startswith(("http://", "https://")):
        raise ValueError("图片URL必须以http/https开头")
    if "cdn.jsdelivr.net" not in url and "aliyuncs.com" not in url:
        print("⚠️ 警告：非受信图片源，可能影响生成稳定性") 