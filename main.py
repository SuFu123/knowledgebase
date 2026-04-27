import os
import json
import uuid
import requests
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. 基础配置 ---
FOLDER_ID = '1XJbuZw8M2q-7hf1hZShvRLD2UpleNSkT'

# --- 2. 授权 Google Drive ---
def auth_gdrive():
    scope = ['https://www.googleapis.com/auth/drive']
    creds_json = os.getenv('GDRIVE_CREDENTIALS_DATA')
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gauth = GoogleAuth()
    gauth.credentials = creds
    return GoogleDrive(gauth)

# --- 3. 事实性提取逻辑 ---
def extract_knowledge(url, platform):
    print(f"开始处理 {platform} 链接: {url}")
    
    # 基础 Markdown 模板
    md_content = f"# 知识卡片: {platform.upper()}\n- 来源链接: {url}\n\n"

    if platform == "douyin":
        # 此处后续可接入你之前的 Video2Text 逻辑
        # 暂时使用占位符
        md_content += "## 视频语音摘要 (ASR)\n[等待接入 Video2Text 逻辑...]\n"
        
    elif platform == "xhs":
        # 小红书逻辑：抓取文案 + 尝试 OCR
        md_content += "## 图文/视频事实提取\n"
        # 简单示例：抓取页面标题（实际需更复杂的爬取逻辑）
        md_content += f"> 已记录该小红书链接，建议后续结合 EasyOCR 处理图片文字。\n"
        
    return md_content

# --- 4. 主函数 ---
def main():
    target_url = os.getenv('TARGET_URL')
    platform = os.getenv('PLATFORM')
    
    if not target_url:
        print("未获取到目标 URL")
        return

    # 执行提取
    markdown_text = extract_knowledge(target_url, platform)
    
    # 上传至 Google Drive
    drive = auth_gdrive()
    file_name = f"{platform}_{uuid.uuid4().hex[:6]}.md"
    
    file_metadata = {
        'title': file_name,
        'parents': [{'id': FOLDER_ID}],
        'mimeType': 'text/markdown'
    }
    
    file = drive.CreateFile(file_metadata)
    file.SetContentString(markdown_text)
    
    # --- 关键修改点 ---
    # 增加 supportsAllDrives 参数，确保在共享空间内正常操作
    file.Upload(param={'supportsAllDrives': True}) 
    
    print(f"✅ 成功! 文件已同步至云端: {file_name}")

if __name__ == "__main__":
    main()
