# GitHub 仓库设置指南

## 自动设置（推荐）
1. 双击运行 `setup_github.bat`
2. 按照向导提示操作即可

## 手动设置
如果自动设置失败，您可以：
1. 访问 https://github.com/settings/tokens/new
2. 创建新的访问令牌：
   - 名称：WanAPI
   - 有效期：永不过期
   - 权限：勾选 repo
3. 复制生成的token
4. 编辑 config.json：
   ```json
   {
     "GITHUB_TOKEN": "你的token",
     "GITHUB_REPO": "你的用户名/仓库名",
     "GITHUB_BRANCH": "main"
   }
   ```

## 常见问题
1. Token无效
   - 检查是否正确复制
   - 确保有 repo 权限
2. 仓库创建失败
   - 检查仓库名是否已存在
   - 确保token权限正确 