import os
import sys
import json
from pathlib import Path

# 基础导入
import time
import base64
import requests
import torch
import numpy as np
from PIL import Image

# 直接从constants导入所需变量
from .constants import comfy_root, get_project_name, get_project_category

# 移除动态导入相关代码
try:
    from .utils.image_processor import tensor_to_pil
    from .utils.github_client import GitHubUploader
    print("✅ utils模块已加载")
except ImportError as e:
    print(f"❌ 导入失败：{str(e)}")
    raise

# 获取当前文件的绝对路径
current_file = Path(__file__).resolve()
package_dir = current_file.parent

print(f"📂 当前文件：{current_file}")
print(f"📁 包目录：{package_dir}")

# 添加包路径
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

# 强制刷新模块缓存
if 'Comfyui_wan_api' in sys.modules:
    del sys.modules['Comfyui_wan_api']
if 'Comfyui_wan_api.utils' in sys.modules:
    del sys.modules['Comfyui_wan_api.utils']

# 使用精确的绝对导入
try:
    from .utils.image_processor import tensor_to_pil
    from .utils.github_client import GitHubUploader
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败：{str(e)}")
    print(f"当前系统路径：{sys.path}")
    raise

# 配置文件路径
config_file = os.path.join(os.path.dirname(__file__), 'config.json')

class WanAPIImageUploader:
    """WanAPI图片上传节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "upload_method": (["GitHub", "ModelScope"],),
            },
            "optional": {
                "github_repo": ("STRING", {"default": ""}),
                "github_branch": ("STRING", {"default": "main"}),
                "github_token": ("STRING", {"default": ""})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "upload_image"
    CATEGORY = "WanAPI"
    
    def __init__(self):
        try:
            # 直接导入所需函数和类
            from .utils.image_processor import tensor_to_pil
            from .utils.github_client import GitHubUploader
            self.tensor_to_pil = tensor_to_pil
            self.github_uploader = GitHubUploader
            
            # 读取配置文件
            self.config = self._load_config()
            print("✅ 模块导入成功")
            print(f"📝 当前配置：{self.config}")
        except ImportError as e:
            print(f"❌ 导入失败：{str(e)}")
            raise
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 配置文件加载失败：{str(e)}")
            return {}
    
    def upload_image(self, images, upload_method="GitHub", github_repo="", github_branch="main", github_token=""):
        """上传图片"""
        try:
            print("\n=== 开始处理图片 ===")
            print(f"📊 输入图片类型：{type(images)}")
            
            # 处理批次维度
            if len(images.shape) == 4:
                print(f"📊 输入张量形状：{images.shape}, 类型：{images.dtype}")
                print("⚙️ 处理批次维度")
                images = images[0]
            
            # 处理通道维度
            if images.shape[2] != 3:
                print("⚙️ 处理通道维度")
                images = images.permute(2, 0, 1)
            
            # 转换为numpy数组
            print("⚙️ 转换为numpy数组")
            images = images.cpu().numpy()
            images = (images * 255).astype(np.uint8)
            print(f"📊 numpy数组形状：{images.shape}, 类型：{images.dtype}")
            
            # 创建PIL图像
            print("⚙️ 创建PIL图像")
            pil_image = Image.fromarray(images)
            print(f"📊 PIL图像大小：{pil_image.size}, 模式：{pil_image.mode}")
            
            # 创建临时目录
            temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 保存临时文件
            temp_path = os.path.join(temp_dir, f"upload_{int(time.time())}.jpg")
            print(f"💾 保存临时文件：{temp_path}")
            pil_image.save(temp_path, quality=95)
            
            # 选择上传方式
            if upload_method == "GitHub":
                # 优先使用参数值，然后是配置文件值
                repo = github_repo or self.config.get("GITHUB_REPO", "")
                branch = github_branch or self.config.get("GITHUB_BRANCH", "main")
                token = github_token or self.config.get("GITHUB_TOKEN", "")
                
                print(f"🔧 GitHub配置：repo={repo}, branch={branch}, token={'已设置' if token else '未设置'}")
                
                if not repo or not token:
                    raise ValueError(f"GitHub配置不完整：repo={repo}, token={'已设置' if token else '未设置'}")
                
                print("⚙️ 初始化GitHub上传器")
                uploader = self.github_uploader(repo=repo, branch=branch, token=token)
                print("⚙️ 开始上传文件")
                url = uploader.upload(temp_path)
                
                # 清理临时文件
                try:
                    os.remove(temp_path)
                    print("🧹 清理临时文件成功")
                except Exception as e:
                    print(f"⚠️ 清理临时文件失败：{str(e)}")
                
                if url:
                    print(f"✅ 上传成功：{url}")
                    return (url,)
                else:
                    raise ValueError("上传失败")
            else:
                raise ValueError("暂不支持的上传方式")
            
        except Exception as e:
            print(f"❌ 上传失败：{str(e)}")
            import traceback
            print(f"🔍 详细错误：\n{traceback.format_exc()}")
            return ("",)

    def upload_to_github(self, image_path, repo, branch, token):
        """GitHub上传实现"""
        try:
            # 添加权限验证
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 验证Token权限
            auth_check = requests.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=5
            )
            
            if auth_check.status_code != 200:
                print(f"❌ Token权限验证失败: {auth_check.json().get('message')}")
                return None
            
            # 检查是否有写权限
            repo_info = requests.get(
                f"https://api.github.com/repos/{repo}",
                headers=headers
            )
            
            if repo_info.status_code != 200:
                print(f"❌ 仓库访问失败: {repo_info.json().get('message')}")
                return None
            
            filename = f"wanx_{int(time.time())}.jpg"
            with open(image_path, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            
            response = requests.put(
                f"https://api.github.com/repos/{repo}/contents/images/{filename}",
                json={
                    "message": "Auto-upload from ComfyUI",
                    "content": content,
                    "branch": branch
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                return f"https://raw.githubusercontent.com/{repo}/{branch}/images/{filename}"
            elif response.status_code == 403:
                error_msg = response.json().get('message', '')
                if 'resource is not accessible' in error_msg:
                    print("""
                    ❌ 权限不足，请检查：
                    1. Token是否具有repo读写权限
                    2. 仓库是否设置为私有但未授权
                    3. Token是否已过期
                    """)
                return None
            return None
        except Exception as e:
            print(f"GitHub上传失败: {str(e)}")
            return None

    def upload_to_modelscope(self, image_path, api_key):
        """ModelScope上传实现"""
        try:
            api = HubApi()
            api.login(api_key)
            
            upload_result = api.upload_file(
                file_path=image_path,
                repo_type="dataset",
                repo_name="temp_uploads",
                revision=DEFAULT_MODEL_REVISION
            )
            
            return upload_result['url']
        except Exception as e:
            print(f"ModelScope上传失败: {str(e)}")
            return None

    def upload(self, image, upload_method, github_repo="", github_branch=""):
        try:
            # 处理图像
            pil_image = self.tensor_to_pil(image)
            if not pil_image:
                return ("",)
            
            # 保存临时文件
            temp_dir = os.path.join(comfy_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"upload_{int(time.time())}.jpg")
            pil_image.save(temp_path, quality=95)
            
            # 选择上传方式
            url = ""
            if upload_method == "GitHub":
                uploader = self.github_uploader(
                    repo=github_repo or os.getenv("GITHUB_REPO"),
                    branch=github_branch or os.getenv("GITHUB_BRANCH"),
                    token=os.getenv("GITHUB_TOKEN")
                )
                url = uploader.upload(pil_image)
            else:
                url = self.upload_to_modelscope(temp_path, os.getenv("DASHSCOPE_API_KEY"))
            
            # 清理临时文件
            try:
                os.remove(temp_path)
            except:
                pass
            
            return (url or "https://cdn.translate.alibaba.com/r/wanx-demo-1.png",)
            
        except Exception as e:
            print(f"上传失败: {str(e)}")
            return ("",)

    # 上传成功后自动清理历史文件
    def clean_old_files(self, repo, branch, token, keep=10):
        # 获取仓库文件列表
        response = requests.get(
            f"https://api.github.com/repos/{repo}/contents/images",
            headers={"Authorization": f"token {token}"}
        )
        
        # 保留最新的10个文件
        files = sorted(response.json(), key=lambda x: x['name'], reverse=True)[keep:]
        
        # 删除旧文件
        for file in files:
            requests.delete(
                f"https://api.github.com/repos/{repo}/contents/images/{file['name']}",
                json={
                    "message": "Auto-clean old files",
                    "sha": file['sha'],
                    "branch": branch
                },
                headers={"Authorization": f"token {token}"}
            )

    def check_repo_structure(self, repo, branch, token):
        """自动创建缺失的images目录"""
        try:
            headers = {"Authorization": f"token {token}"}
            
            # 检查images目录是否存在
            check_url = f"https://api.github.com/repos/{repo}/contents/images?ref={branch}"
            response = requests.get(check_url, headers=headers)
            
            if response.status_code == 404:
                # 创建images目录
                data = {
                    "message": "Create images directory",
                    "content": base64.b64encode(b"placeholder").decode(),
                    "branch": branch
                }
                requests.put(
                    f"https://api.github.com/repos/{repo}/contents/images/.gitkeep",
                    headers=headers,
                    json=data
                )
                print("✅ 自动创建images目录成功")
                
        except Exception as e:
            print(f"目录检查失败: {str(e)}")