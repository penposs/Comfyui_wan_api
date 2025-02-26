import os
import json
import requests
from datetime import datetime, timedelta
import time

class GitHubCleaner:
    def __init__(self, repo, token, days_to_keep=7):
        """
        初始化GitHub清理器
        :param repo: 仓库名 (格式: 用户名/仓库名)
        :param token: GitHub Token
        :param days_to_keep: 保留最近几天的图片
        """
        self.repo = repo
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.days_to_keep = days_to_keep
        
    def get_images(self):
        """获取仓库中的所有图片"""
        try:
            response = requests.get(
                f"https://api.github.com/repos/{self.repo}/contents/images",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ 获取文件列表失败：{response.json().get('message')}")
                return []
                
            return response.json()
            
        except Exception as e:
            print(f"❌ 获取文件列表出错：{str(e)}")
            return []
    
    def get_file_info(self, file_sha):
        """获取文件的详细信息"""
        try:
            response = requests.get(
                f"https://api.github.com/repos/{self.repo}/git/blobs/{file_sha}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    def delete_file(self, file_path, file_sha):
        """删除文件"""
        try:
            response = requests.delete(
                f"https://api.github.com/repos/{self.repo}/contents/{file_path}",
                headers=self.headers,
                json={
                    "message": "Auto cleanup old images",
                    "sha": file_sha
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ 删除文件出错：{str(e)}")
            return False
    
    def cleanup(self):
        """执行清理"""
        print(f"\n=== 开始清理 {self.repo} 仓库 ===")
        print(f"🔍 保留最近 {self.days_to_keep} 天的图片")
        
        # 获取所有图片
        images = self.get_images()
        if not images:
            print("ℹ️ 没有找到需要清理的图片")
            return
            
        cutoff_date = datetime.now() - timedelta(days=self.days_to_keep)
        deleted_count = 0
        kept_count = 0
        
        print(f"📅 清理 {cutoff_date.strftime('%Y-%m-%d')} 之前的图片")
        
        for image in images:
            if not image['name'].endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            # 从文件名中提取时间戳
            try:
                # 假设文件名格式为 wanx_1234567890.jpg
                timestamp = int(image['name'].split('_')[1].split('.')[0])
                file_date = datetime.fromtimestamp(timestamp)
                
                if file_date < cutoff_date:
                    print(f"🗑️ 删除: {image['name']} ({file_date.strftime('%Y-%m-%d %H:%M:%S')})")
                    if self.delete_file(image['path'], image['sha']):
                        deleted_count += 1
                        # 添加延迟避免触发 GitHub API 限制
                        time.sleep(1)
                else:
                    kept_count += 1
                    
            except (ValueError, IndexError):
                print(f"⚠️ 跳过无效文件名: {image['name']}")
                continue
        
        print(f"""
=== 清理完成 ===
✅ 已删除: {deleted_count} 个文件
💾 已保留: {kept_count} 个文件
""")

def main():
    """主函数"""
    try:
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        repo = config.get('GITHUB_REPO')
        token = config.get('GITHUB_TOKEN')
        
        if not repo or not token:
            print("❌ 配置文件中缺少必要的GitHub配置")
            return
            
        # 创建清理器并执行清理
        cleaner = GitHubCleaner(
            repo=repo,
            token=token,
            days_to_keep=7  # 默认保留7天
        )
        cleaner.cleanup()
        
    except Exception as e:
        print(f"❌ 清理失败：{str(e)}")

if __name__ == "__main__":
    main() 