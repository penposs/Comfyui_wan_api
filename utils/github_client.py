import os
import time
import base64
import requests
from pathlib import Path

class GitHubUploader:
    def __init__(self, repo, branch, token):
        self.repo = repo
        self.branch = branch
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def _validate_permissions(self):
        """验证Token权限"""
        try:
            # 验证Token
            auth_check = requests.get(
                "https://api.github.com/user",
                headers=self.headers,
                timeout=5
            )
            
            if auth_check.status_code != 200:
                print(f"❌ Token验证失败: {auth_check.json().get('message')}")
                return False
                
            # 验证仓库访问权限
            repo_check = requests.get(
                f"https://api.github.com/repos/{self.repo}",
                headers=self.headers
            )
            
            if repo_check.status_code != 200:
                print(f"❌ 仓库访问失败: {repo_check.json().get('message')}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 权限验证失败: {str(e)}")
            return False

    def upload(self, file_path):
        """上传文件到GitHub"""
        if not self._validate_permissions():
            return None
            
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            # 生成文件名
            filename = f"wanx_{int(time.time())}.jpg"
            
            # 上传到GitHub
            response = requests.put(
                f"https://api.github.com/repos/{self.repo}/contents/images/{filename}",
                headers=self.headers,
                json={
                    "message": "Auto-upload from ComfyUI",
                    "content": content,
                    "branch": self.branch
                },
                timeout=10
            )
            
            # 处理响应
            if response.status_code == 201:
                # 返回原始 GitHub URL 而不是 CDN URL
                return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/images/{filename}"
            elif response.status_code == 403:
                error_msg = response.json().get('message', '')
                if 'resource is not accessible' in error_msg:
                    print("""❌ 权限不足，请检查：
                    1. Token是否具有repo权限
                    2. 仓库是否设置为私有
                    3. Token是否已过期""")
                return None
            
            print(f"❌ 上传失败: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ 上传失败: {str(e)}")
            import traceback
            print(f"🔍 详细错误：\n{traceback.format_exc()}")
            return None 