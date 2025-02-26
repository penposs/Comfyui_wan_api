# 避免在顶层导入，改为按需导入
def get_image_processor():
    from .image_processor import tensor_to_pil, validate_image_url
    return tensor_to_pil, validate_image_url

def get_github_client():
    from .github_client import GitHubUploader
    return GitHubUploader

print("✅ utils模块已加载")
