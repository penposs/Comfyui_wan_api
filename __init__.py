# 避免直接导入，改用动态导入
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def register_nodes():
    # 动态导入节点类
    from .ImageUploader import WanAPIImageUploader
    from .wan_api import WanAPIImageToVideo
    
    # 注册节点
    global NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    NODE_CLASS_MAPPINGS.update({
        "WanAPIImageUploader": WanAPIImageUploader,
        "WanAPIImageToVideo": WanAPIImageToVideo,
    })
    
    NODE_DISPLAY_NAME_MAPPINGS.update({
        "WanAPIImageUploader": "WanAPI Image Uploader",
        "WanAPIImageToVideo": "WanAPI Image2Video",
    })

# 执行注册
try:
    register_nodes()
    print("✅ Comfyui_wan_api 节点已注册")
except Exception as e:
    print(f"❌ 节点注册失败：{str(e)}")

from .wan_api import WanAPIImageToVideo
from .ImageUploader import WanAPIImageUploader

def register_nodes():
    try:
        NODE_CLASS_MAPPINGS = {
            "WanAPI_Image2Video": WanAPIImageToVideo,
            "WanAPI_ImageUploader": WanAPIImageUploader
        }

        NODE_DISPLAY_NAME_MAPPINGS = {
            "WanAPI_Image2Video": "WanAPI图片转视频",
            "WanAPI_ImageUploader": "WanAPI图片上传"
        }

        print("✅ WanAPI节点注册成功")
        return NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    except Exception as e:
        print(f"❌ WanAPI节点注册失败：{str(e)}")
        raise e

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = register_nodes()

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']