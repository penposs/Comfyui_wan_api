   ✅ utils模块已加载
   # 在ComfyUI的Python控制台中测试
   from Comfyui_wan_api.utils import image_processor, github_client
   print("图像处理器模块:", dir(image_processor))
   print("GitHub客户端:", dir(github_client))
   图像处理器模块: ['tensor_to_pil', 'validate_image_url']
   GitHub客户端: ['GitHubUploader']