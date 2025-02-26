import os
import json
import traceback
import time
import requests
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.util.ssl_ import create_urllib3_context
from .constants import get_project_category, get_project_name, project_root, comfy_root
from PIL import Image
import PIL
import base64
import io
import folder_paths
import numpy as np
import torch
import ssl
import hashlib
from modelscope.hub.api import HubApi
from modelscope.utils.constant import DEFAULT_MODEL_REVISION
from pathlib import Path

# API URL for DashScope
dashscope_api_url = 'https://dashscope.aliyuncs.com'
# API URL for file upload
file_upload_api_url = 'https://api.modelscope.cn'

# Output folder for saving videos
output_folder = os.path.join(comfy_root, 'output')
os.makedirs(output_folder, exist_ok=True)

# Config file path
config_file = os.path.join(project_root, 'config.json')

# Try to load API key from config file
DASHSCOPE_API_KEY = None
try:
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            data = file.read()
            json_data = json.loads(data)
            DASHSCOPE_API_KEY = json_data.get("DASHSCOPE_API_KEY")
except Exception as e:
    print(f"Error loading config file: {e}")

NODE_CATEGORY = get_project_category("wanapi")

# 设置ModelScope缓存目录
os.environ['MODELSCOPE_CACHE'] = os.path.join(comfy_root, 'modelscope_cache')

# 添加重试配置
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", http_adapter)
session.mount("https://", http_adapter)

class WanAPIImageToVideo:
    """WanAPI图片转视频节点"""
    NAME = get_project_name('WanAPI_Image2Video')  # 添加节点名称
    CATEGORY = NODE_CATEGORY
    RETURN_TYPES = ("STRING", "STRING",)  # 添加历史记录输出
    RETURN_NAMES = ("video_url", "history_info",)  # 添加历史记录名称
    FUNCTION = "generate_video"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url": ("STRING", {"default": ""}),
                "model": (["wanx2.1-i2v-plus", "wanx2.1-i2v-turbo"], {
                    "default": "wanx2.1-i2v-plus",
                    "description": "plus: 高质量(5秒), turbo: 快速生成(3-5秒)"
                }),
                "duration": ([3, 4, 5], {  # 改为下拉选择
                    "default": 5,
                    "description": "plus模型固定5秒，turbo模型可选3-5秒"
                }),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "description": "生成视频的文本提示词"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "description": "-1表示随机种子"
                }),
                "prompt_extend": (["True", "False"], {
                    "default": "True",
                    "description": "是否启用提示词智能扩展"
                })
            }
        }
    # 删除以下重复定义：
    # RETURN_TYPES = ("STRING",)
    # RETURN_NAMES = ("video_url",)
    # FUNCTION = "generate_video"
    # CATEGORY = "WanAPI"
    def __init__(self):
        self.config = self._load_config()
        print(f"✅ WanAPI视频节点初始化成功，API Key: {'已配置' if self.config.get('DASHSCOPE_API_KEY') else '未配置'}")
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"📝 加载配置：{config_path}")
                return config
        except Exception as e:
            print(f"⚠️ 配置文件加载失败：{str(e)}")
            return {}
    
    def generate_video(self, image_url, model="wanx2.1-i2v-plus", duration=5, api_key="", prompt="", seed=-1, prompt_extend="True"):
        """生成视频并等待完成"""
        try:
            if not image_url:
                raise ValueError("无效图片URL，请先连接上传节点")
            
            # 验证模型和时长组合
            if model == "wanx2.1-i2v-plus" and duration != 5:
                print("⚠️ wanx2.1-i2v-plus 模型仅支持5秒视频，已自动调整")
                duration = 5
            elif model == "wanx2.1-i2v-turbo" and duration not in [3, 4, 5]:
                print(f"⚠️ wanx2.1-i2v-turbo 模型仅支持3、4、5秒视频，已自动调整为5秒")
                duration = 5
            
            # 优先使用参数中的API密钥，其次使用配置文件中的密钥
            api_key = api_key or self.config.get("DASHSCOPE_API_KEY", "")
            
            print(f"""
🎬 开始生成视频：
- 模型：{model}
- 时长：{duration}秒
- 提示词：{prompt if prompt else '无'}
- 提示词扩展：{'开启' if prompt_extend == 'True' else '关闭'}
- 随机种子：{seed if seed != -1 else '随机'}
""")
            
            # 调用WanAPI创建任务
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "X-DashScope-Async": "enable"
                },
                json={
                    "model": model,
                    "input": {
                        "prompt": prompt,
                        "img_url": image_url
                    },
                    "parameters": {
                        "duration": duration,
                        "seed": seed if seed != -1 else random.randint(0, 2147483647),
                        "prompt_extend": prompt_extend == "True"
                    }
                },
                timeout=30  # 增加超时时间
            )
            
            if response.status_code != 200:
                error_msg = response.json().get('message', '未知错误')
                raise ValueError(f"API调用失败：{error_msg}")
            
            # 获取任务ID
            task_id = response.json().get('output', {}).get('task_id')
            if not task_id:
                raise ValueError("未获取到任务ID")
            
            print(f"✅ 任务已提交：{task_id}")
            
            # 等待任务完成
            max_retries = 120  # 增加到120次，
            retry_interval = 10.0  # 保持10秒间隔
            
            for i in range(max_retries):
                print(f"⏳ 等待中... ({i+1}/{max_retries}, 已等待{(i+1) * retry_interval}秒)")
                
                try:
                    status_response = requests.get(
                        f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=30  # 增加超时时间到30秒
                    )
                    
                    if status_response.status_code != 200:
                        error_msg = status_response.json().get('message', '未知错误')
                        raise ValueError(f"状态查询失败：{error_msg}")
                    
                    result = status_response.json()
                    status = result.get('output', {}).get('task_status')
                    
                    # 根据官方文档处理任务状态
                    if status == "SUCCEEDED":
                        video_url = result.get('output', {}).get('video_url')
                        if not video_url:
                            raise ValueError("未找到视频URL")
                            
                        # 构建历史记录信息
                        history_info = f"""任务ID: {task_id}
                    模型: {model}
                    时长: {duration}秒
                    提示词: {prompt if prompt else '无'}
                    提示词扩展: {'开启' if prompt_extend == 'True' else '关闭'}
                    种子: {seed if seed != -1 else '随机'}
                    视频URL: {video_url}
                    生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
                    总耗时: {(i+1) * retry_interval}秒"""
                        
                        print(f"""
                        ✅ 视频生成成功：
                        - 视频URL：{video_url}
                        - 任务ID：{task_id}
                        - 总耗时：{(i+1) * retry_interval}秒
                        """)
                        return (video_url, history_info)
                        
                    elif status == "FAILED":
                        error = result.get('output', {}).get('message', '未知错误')
                        error_code = result.get('code', 'UNKNOWN')
                        error_details = {
                            'RequestError': '请求参数错误',
                            'InvalidApiKey': 'API密钥无效',
                            'QuotaExceeded': '配额超限',
                            'InternalError': '服务内部错误',
                            'TaskNotExist': '任务不存在'
                        }
                        error_msg = error_details.get(error_code, error)
                        raise ValueError(f"任务失败 [{error_code}]：{error_msg}")
                        
                    elif status == "PENDING":
                        print(f"⏳ 任务排队中... ({i+1}/{max_retries})")
                        
                    elif status == "RUNNING":
                        progress = result.get('output', {}).get('progress', 0)
                        print(f"🔄 任务执行中... 进度：{progress}%")
                        
                    else:
                        print(f"⚠️ 未知状态：{status}")
                        print(f"📝 完整响应：{result}")
                    
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ 网络错误 ({i+1}/{max_retries}): {str(e)}")
                    if i == max_retries - 1:
                        raise ValueError(f"网络连接失败: {str(e)}")
                    time.sleep(min(2 ** i, 30))  # 指数退避重试
                    continue
                
                time.sleep(retry_interval)
            
            raise ValueError(f"超过最大等待时间({max_retries * retry_interval}秒)")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 视频生成失败：{error_msg}")
            return (error_msg, "")  # 失败时返回错误信息和空历史记录

