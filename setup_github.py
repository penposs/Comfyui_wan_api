import os
import json
import time
import requests
from getpass import getpass
import webbrowser
from pathlib import Path

def setup_github():
    """一键设置GitHub仓库"""
    print("""
=== WanAPI GitHub仓库设置向导 ===
这个向导将帮助您：
1. 创建GitHub个人访问令牌(Token)
2. 创建专用的图片仓库
3. 自动配置WanAPI
""")
    
    # 获取用户输入
    email = input("\n请输入GitHub邮箱: ").strip()
    
    # 指导用户创建token
    print("""
\n=== 创建访问令牌(Token) ===
1. 正在为您打开GitHub Token创建页面...
2. 请登录GitHub（如果需要）
3. 在打开的页面中：
   - 设置Token名称为：WanAPI
   - 设置有效期为：No expiration
   - 勾选 repo 权限
   - 点击最下方的 [Generate token] 按钮
4. 复制生成的token
""")
    
    # 打开token创建页面
    webbrowser.open('https://github.com/settings/tokens/new')
    token = getpass("\n请粘贴生成的Token: ").strip()
    
    if not token:
        print("❌ Token不能为空")
        return
    
    # 验证token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 验证token
        user_response = requests.get(
            "https://api.github.com/user",
            headers=headers
        )
        
        if user_response.status_code != 200:
            print("❌ Token无效，请检查是否正确复制")
            return
        
        username = user_response.json()['login']
        print(f"\n✅ Token验证成功！欢迎 {username}")
        
        # 创建仓库
        repo_name = "wanapi-images"
        repo_data = {
            "name": repo_name,
            "description": "WanAPI图片存储仓库",
            "private": False,
            "auto_init": True
        }
        
        print(f"\n正在创建仓库 {repo_name}...")
        
        repo_response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=repo_data
        )
        
        if repo_response.status_code == 201:
            print("✅ 仓库创建成功！")
        elif repo_response.status_code == 422:
            print("ℹ️ 仓库已存在，继续使用")
        else:
            print(f"❌ 仓库创建失败：{repo_response.json().get('message')}")
            return
        
        # 更新配置文件
        config_path = Path(__file__).parent / 'config.json'
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config.update({
                "GITHUB_TOKEN": token,
                "GITHUB_REPO": f"{username}/{repo_name}",
                "GITHUB_BRANCH": "main"
            })
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"""
=== 设置完成 ===
✅ 配置已更新：
- 仓库：{username}/{repo_name}
- Token：{token[:4]}...{token[-4:]}
- 分支：main

🎉 现在您可以：
1. 重启ComfyUI
2. 使用WanAPI节点上传图片和生成视频了！
""")
            
        except Exception as e:
            print(f"❌ 配置文件更新失败：{str(e)}")
            return
            
    except Exception as e:
        print(f"❌ 设置失败：{str(e)}")
        return

if __name__ == "__main__":
    setup_github() 