from flask import Flask, make_response, request, send_file
import time
import json
from datetime import datetime
import os
import requests

ip_connect_dict = {}
block_list = {}

# 备份文件的路径
backup_folder = "C:/Users/Administrator/Desktop/"

app = Flask(__name__)

response_403_json = {
    "status": 403
}

connect_num = 0

# 处理文件获取的逻辑，优先从链接获取，再返回本地缓存
def get_file(path, fallback_url_1, fallback_url_2, local_path):
    try:
        # 尝试从第一个备用 URL 获取文件
        print(f"尝试从第一个备用链接获取文件：{fallback_url_1}")
        response = requests.get(fallback_url_1)
        if response.status_code != 404:
            return response.content  # 返回文件内容

        # 如果第一个链接返回 404 错误，尝试第二个备用 URL
        print(f"第一个备用链接返回 404，尝试第二个备用链接：{fallback_url_2}")
        response = requests.get(fallback_url_2)
        if response.status_code != 404:
            return response.content  # 返回文件内容

        # 如果两个备用 URL 都不可用，返回本地缓存
        print(f"两个备用链接都不可用，返回本地缓存文件：{local_path}")
        if os.path.exists(local_path):
            return send_file(local_path)
        else:
            return make_response("文件不可用", 404)

    except requests.RequestException as e:
        # 如果请求异常，返回本地文件
        print(f"请求异常，返回本地缓存文件：{local_path}")
        if os.path.exists(local_path):
            return send_file(local_path)
        else:
            return make_response("文件不可用", 404)

@app.route("/<path>")
def send_response(path):
    print(path)
    try:
        address = request.remote_addr
        time_now = int(str(time.time()).split(".")[0])

        # 检查是否有封禁的IP
        try:
            is_block = block_list[address]["isBlock"]
        except KeyError:
            is_block = False
        try:
            connect_num = ip_connect_dict[address]["content"]
        except KeyError:
            ip_connect_dict[address] = {
                "exp": [str(time.time()).split(".")[0]]
            }
            connect_num = 0

        # 检查 IP 是否被封禁
        if is_block:
            block_exp_time = block_list[address]["exp"]
            if time_now - int(block_exp_time) <= 0:
                del block_list[address]  # 解除封禁
            else:
                dt_object = datetime.fromtimestamp(block_exp_time)
                std_time = dt_object.isoformat()
                reason = block_list[address]["reason"]
                response_403_json["errorMessage"] = f"此 IP 已被封禁，封禁原因:{reason}，解封时间:{std_time}"
                response = make_response()
                response.status_code = 403
                response.content_encoding = "utf-8"
                response.data = json.dumps(response_403_json)
                return response

        if connect_num < 10:
            # 检查路径是否合法，避免路径遍历攻击
            if ".." in path or "." in path:
                block_exp = int(str(time.time()).split(".")[0]) + 3600 * 24 * 7
                block_list[address] = {
                    "exp": str(block_exp),
                    "reason": "攻击 API 服务"
                }
                response = make_response()
                response.status_code = 403
                dt_object = datetime.fromtimestamp(block_exp)
                std_time = dt_object.isoformat()
                reason = block_list[address]["reason"]
                response_403_json["errorMessage"] = f"此 IP 已被封禁，封禁原因:{reason}，解封时间:{std_time}"
                response.data = json.dumps(response_403_json).encode('utf-8')
                return response

            # 文件路径处理
            if path == "UpdateHomepage.xaml":
                local_path = os.path.join(backup_folder, "Homepagebackup", "UpdateHomepage.xaml")
                # 尝试从 URL 获取文件
                return get_file(path, 
                                "http://pclhomeplazaoss.lingyunawa.top:26994/d/Homepages/Joker2184/UpdateHomepage.xaml", 
                                "https://UpdateHomepage.pages.dev/UpdateHomepage.xaml", 
                                local_path)
            
            response = make_response()
            response.status_code = 200
            ip_connect_dict[address] = {"content": connect_num + 1}

        elif connect_num == 10:
            # 达到请求次数限制，返回 429 状态码
            response = make_response()
            response.status_code = 429
            # 将此 IP 添加到封禁列表
            block_list[address] = {
                "exp": time_now + 3600,
                "reason": "请求次数过多"
            }

        else:
            # 请求次数过多，封禁该 IP
            response = make_response()
            response.status_code = 403
            dt_object = datetime.fromtimestamp(time_now + 3600)
            std_time = dt_object.isoformat()
            response_403_json["errorMessage"] = f"此 IP 已被封禁，封禁原因: 请求次数过多，解封时间: {std_time}"
            response.data = json.dumps(response_403_json).encode('utf-8')

    except KeyboardInterrupt as e:
        print(e)
        response = make_response()
        response.status_code = 500
        return response


# 启动 Flask 应用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
