import base64
import hashlib
import hmac
import json
import random
import threading
import time
import logging
from websocket import create_connection, WebSocketConnectionClosedException

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


# 更改为您的WebSocket服务器地址
websocketBaseUrl = 'wss://midjourney-api.ai3.design/ws'
accessKey = 'G63oFg4M4cypUARRAHl3JSKdw3mPC_0pDXdJWGEBP0LH5AXG9SmEAw'
secretKey = 'akYz-FOafdoHYd2feMYe6j1cIPb-Y0ysru3HUYKGqBgLhGAYA3gyNQ'

# 使用SHA-256对字符串进行签名
def sign_string(stringToSign, secretKey):
    secretKey = secretKey.encode()
    stringToSign = stringToSign.encode()
    digester = hmac.new(secretKey, stringToSign, hashlib.sha256)
    signature = digester.digest()

    # 转换为URL安全的Base64编码
    signatureBase64 = base64.urlsafe_b64encode(signature).decode()
    return signatureBase64.rstrip('=')

def send_auth(ws):
    # 生成随机的nonce
    nonce = random.randint(0, 1e16)
    # 生成当前的Unix时间戳
    timestamp = int(time.time())
    # 准备用于签名的字符串
    stringToSign = f"access_key={accessKey}&nonce={nonce}&timestamp={timestamp}"
    signature = sign_string(stringToSign, secretKey)
    auth_message = {
        "type": 7,
        "data": {
            "access_key": accessKey,
            "timestamp": timestamp,
            "nonce": nonce,
            "signature": signature,
        }
    }
    ws.send(json.dumps(auth_message))

def send_heartbeat(ws):
    heartbeat_message = {
        "type": 1,
        "data": {
            "access_key": accessKey
        }
    }
    while True:
        ws.send(json.dumps(heartbeat_message))
        time.sleep(5)  # delay for 5 seconds

def send_imagine_task(ws, prompt):
    imagine_task = {
        "type": 4,
        "state": "用户id之类的",
        "data": {
            "mode": "Fast",
            "type": 1,
            "image_proxy": True,
            "imagine": {
                "prompt": prompt
            }
        }
    }
    ws.send(json.dumps(imagine_task))

def send_describe_task(ws):
    task = {
        "type": 4,
        "state": "用户id之类的",
        "data": {
            "mode": "Fast",
            "type": 7,
            "image_proxy": True,
            "describe": {
                "file_url": "https://pub-cc4c1f10781c4f63a50a0037a2aaf667.r2.dev/af0059c7713b2486a038c0fcceb397d3.jpg"
            }
        }
    }
    ws.send(json.dumps(task))

def handle_connection():
    ws = create_connection(websocketBaseUrl)
    send_auth(ws)
    threading.Thread(target=send_heartbeat, args=(ws,)).start()  # Launch heartbeat in the background
    # send_imagine_task(ws, "cat") # Launch imagine task
    # send_describe_task(ws)
    try:
        while True:
            message = ws.recv()
            logging.info(f"Received message: {message}")
    except WebSocketConnectionClosedException:
        logging.info("Connection with server closed")

handle_connection()
