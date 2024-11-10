import requests
import json
import os
from datetime import datetime

def get_latest_version(url):
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    # 解析最新版本信息
    releases = response.json()
    if releases:
        latest_version = releases[0]['tag_name']  # 最新版本号
        return latest_version
    else:
        raise ValueError("无法找到最新版本号")

def create_json_file(version, save_path):
    data = {"Title": version}
    filename = os.path.join(save_path, f"{version}.json")  # 指定保存路径
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return filename

def create_ini_file(version, build_time, github_time, save_path):
    # 格式化为所需内容
    ini_data = f"PCL Version: {version}\nHomepage Version: {version}\nBuilder Time: {build_time}\nUpdate Time: {github_time}"
    ini_filename = os.path.join(save_path, "UpdateHomepage.xaml.ini")  # 指定保存路径
    with open(ini_filename, 'w') as ini_file:
        ini_file.write(ini_data)  # 写入没有空行的格式
    return ini_filename

if __name__ == "__main__":
    url = "https://api.github.com/repos/Hex-Dragon/PCL2/releases"
    save_path = r"H:\UpdateHomepage"  # 保存路径
    
    # 确保保存目录存在
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    try:
        # 获取最新版本号
        latest_version = get_latest_version(url)
        
        # 获取当前系统时间（运行该 Py 文件时的时间）
        build_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取 GitHub 上的最新更新时间
        releases = requests.get(url).json()
        latest_update_time = releases[0]['published_at']  # 最新更新时间
        github_time = datetime.strptime(latest_update_time, "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建 JSON 文件
        json_file_name = create_json_file(latest_version, save_path)
        print(f"成功创建 {json_file_name}，内容为: {{'Title': '{latest_version}'}}")
        
        # 创建 INI 文件
        ini_file_name = create_ini_file(latest_version, build_time, github_time, save_path)
        print(f"成功创建 {ini_file_name}，内容为:\n{open(ini_file_name).read()}")
        
    except Exception as e:
        print(f"发生错误: {e}")
