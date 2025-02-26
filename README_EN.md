# ComfyUI WanAPI Nodes

[中文版](README.md)

Free trial of Tongyi Wanxiang wan2.1 model, this is a batch implementation of wan2.1 API, providing batch processing for your short video production.

## Features
- 🎬 Support image to video conversion
- 📤 Auto upload images to GitHub
- 🔄 Support batch processing
- 🧹 Auto cleanup temporary files
- 💾 Periodic GitHub repository cleanup

## Installation
1. Clone the repository to ComfyUI's custom_nodes directory:
```bash
cd custom_nodes
git clone https://github.com/penposs/Comfyui_wan_api.git
```

2. Install dependencies:
```bash
pip install -r Comfyui_wan_api/requirements.txt
```

## Initial Setup

### 1. Create GitHub Repository

#### Method 1: Automatic Setup
1. Run the auto-setup script:
```bash
cd Comfyui_wan_api
setup_github.bat
```

2. Setup steps:
   - Enter GitHub email
   - Create Token:
     - Token name: `WanAPI`
     - Expiration: No expiration
     - Permissions: Check `repo`
   - Copy and paste Token

#### Method 2: Manual Setup
1. Visit: https://github.com/settings/tokens/new
2. Create Token
3. Create public repository
4. Edit config file

### 2. Configure DashScope API

1. Visit and login to DashScope:
   https://www.aliyun.com/minisite/goods?userCode=4onztxky
   
2. Get 200 seconds free trial
   Check the pricing on model usage page

3. Configure API Key:
```json
{
    "DASHSCOPE_API_KEY": "your-api-key"
}
```

## Usage

### 1. Basic Usage
1. Add `WanAPIImageUploader` node
2. Connect image input
3. Add `WanAPIImageToVideo` node
4. Set parameters
5. Run workflow

### 2. Example Workflows
- Multiple example workflows provided
- Including basic and advanced usage
- Ready to load and use

## Model Description

### wanx2.1-i2v-plus
- High-quality model
- Fixed 5-second duration
- Processing time: 7-10 minutes
- Cost: 0.70 CNY/second

### wanx2.1-i2v-turbo
- Fast model
- Support 3-5 seconds duration
- Processing time: 3-5 minutes
- Cost: 0.24 CNY/second

## FAQ

1. Invalid Token
   - Check permissions
   - Verify expiration

2. Upload Failed
   - Check network
   - Verify permissions
   - Confirm configuration

3. Video Generation Failed
   - Check API Key
   - Verify image upload
   - Check error messages

## Changelog

### v1.0.0
- Initial release
- Support image to video
- Auto upload to GitHub
- Add repository cleanup

## Contact
- GitHub Issues
- Email: 2363939182@qq.com

## License
MIT License
```

