
# ComfyUI WanAPI 节点 / ComfyUI WanAPI Nodes

白嫖通义万相 wan2.1模型，这是一个批量调用wan2.1 api的实现，给你的短剧生产提供批量解决方案。

Free trial of Tongyi Wanxiang wan2.1 model, this is a batch implementation of wan2.1 API, providing batch processing for your short video production.

## 功能特点 / Features

- 🎬 支持图片转视频 / Support image to video conversion
- 📤 自动上传图片到 GitHub / Auto upload images to GitHub
- 🔄 支持批量处理 / Support batch processing
- 🧹 自动清理临时文件 / Auto cleanup temporary files
- 💾 定期清理 GitHub 仓库 / Periodic GitHub repository cleanup

## 安装步骤 / Installation

1. 克隆仓库到 ComfyUI 的 custom_nodes 目录：
   Clone the repository to ComfyUI's custom_nodes directory:
```bash
cd custom_nodes
git clone https://github.com/your-repo/Comfyui_wan_api.git
```

2. 安装依赖：
   Install dependencies:
```bash
pip install -r Comfyui_wan_api/requirements.txt
```

## 初始配置 / Initial Setup

### 1. 创建 GitHub 仓库 / Create GitHub Repository

#### 方法一：自动配置 / Method 1: Automatic Setup
1. 运行自动配置脚本 / Run the auto-setup script:
```bash
cd Comfyui_wan_api
setup_github.bat
```

2. 配置步骤 / Setup steps:
   - 输入 GitHub 邮箱 / Enter GitHub email
   - 创建 Token / Create Token:
     - Token 名称 / Token name: `WanAPI`
     - 有效期 / Expiration: `No expiration`
     - 权限 / Permissions: 勾选 `repo` / Check `repo`
   - 复制并粘贴 Token / Copy and paste Token

#### 方法二：手动配置 / Method 2: Manual Setup
1. 访问 / Visit: https://github.com/settings/tokens/new
2. 创建 Token / Create Token
3. 创建公开仓库 / Create public repository
4. 编辑配置文件 / Edit config file

### 2. 配置百炼 API / Configure DashScope API

1. 访问并登录百炼平台 / Visit and login to DashScope:
   https://www.aliyun.com/minisite/goods?userCode=4onztxky
   
2. 白嫖通义万相 200秒 / Get 200 seconds free trial
   注意查看模型调用页面的收费 / Check the pricing on model usage page

3. 配置 API Key / Configure API Key:
```json
{
    "DASHSCOPE_API_KEY": "your-api-key"
}
```

## 使用方法 / Usage

### 1. 基本用法 / Basic Usage
1. 添加 `WanAPIImageUploader` 节点 / Add `WanAPIImageUploader` node
2. 连接图片输入 / Connect image input
3. 添加 `WanAPIImageToVideo` 节点 / Add `WanAPIImageToVideo` node
4. 设置参数 / Set parameters
5. 运行工作流 / Run workflow

### 2. 示例工作流 / Example Workflows
- 提供多个示例工作流 / Multiple example workflows provided
- 包括基础和高级用法 / Including basic and advanced usage
- 可直接加载使用 / Ready to load and use

## 模型说明 / Model Description

### wanx2.1-i2v-plus
- 高质量模型 / High-quality model
- 固定 5 秒时长 / Fixed 5-second duration
- 处理时间：7-10 分钟 / Processing time: 7-10 minutes
- 计费：0.70元/秒 / Cost: 0.70 CNY/second

### wanx2.1-i2v-turbo
- 快速模型 / Fast model
- 支持 3-5 秒时长 / Support 3-5 seconds duration
- 处理时间：3-5 分钟 / Processing time: 3-5 minutes
- 计费：0.24元/秒 / Cost: 0.24 CNY/second

## 常见问题 / FAQ

1. Token 无效 / Invalid Token
   - 检查权限 / Check permissions
   - 确认未过期 / Verify expiration

2. 上传失败 / Upload Failed
   - 检查网络 / Check network
   - 验证权限 / Verify permissions
   - 确认配置 / Confirm configuration

3. 视频生成失败 / Video Generation Failed
   - 检查 API Key / Check API Key
   - 确认图片上传 / Verify image upload
   - 查看错误信息 / Check error messages

## 更新日志 / Changelog

### v1.0.0
- 初始版本发布 / Initial release
- 支持图片转视频 / Support image to video
- 自动上传到 GitHub / Auto upload to GitHub
- 添加仓库清理功能 / Add repository cleanup

## 联系方式 / Contact

- GitHub Issues
- Email: 2363939182@qq.com

## 许可证 / License

MIT License
```