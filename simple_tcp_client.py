#!/usr/bin/env python3
"""
Simple TCP Client for Latency Testing
简化的TCP客户端，用于快速测试网络延迟
"""

import socket
import time
import json

def test_tcp_latency(host='127.0.0.1', port=8888, count=5):
    """测试TCP延迟"""
    print(f"🚀 开始TCP延迟测试")
    print(f"📍 目标服务器: {host}:{port}")
    print(f"📊 测试次数: {count}")
    print("-" * 40)
    
    latencies = []
    
    try:
        for i in range(count):
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5秒超时
            
            start_time = time.time()
            
            try:
                # 连接服务器
                sock.connect((host, port))
                
                # 发送ping请求
                request = {
                    'type': 'ping',
                    'timestamp': time.time()
                }
                
                sock.send(json.dumps(request).encode('utf-8'))
                
                # 接收响应
                response = sock.recv(1024)
                end_time = time.time()
                
                if response:
                    response_data = json.loads(response.decode('utf-8'))
                    latency = response_data.get('latency', (end_time - start_time) * 1000)
                    latencies.append(latency)
                    print(f"测试 {i+1}: {latency:8.2f}ms")
                else:
                    print(f"测试 {i+1}: 无响应")
                    
            except socket.timeout:
                print(f"测试 {i+1}: 超时")
            except Exception as e:
                print(f"测试 {i+1}: 错误 - {e}")
            finally:
                sock.close()
            
            # 短暂等待
            if i < count - 1:
                time.sleep(0.5)
        
        print("-" * 40)
        
        # 显示统计结果
        if latencies:
            print("📈 测试结果:")
            print(f"   成功次数: {len(latencies)}")
            print(f"   最小延迟: {min(latencies):.2f}ms")
            print(f"   最大延迟: {max(latencies):.2f}ms")
            print(f"   平均延迟: {sum(latencies)/len(latencies):.2f}ms")
        else:
            print("❌ 所有测试都失败了")
            
    except KeyboardInterrupt:
        print("\n🛑 测试被中断")

if __name__ == '__main__':
    # 可以修改这些参数
    HOST = '127.0.0.1'  # 服务器地址
    PORT = 8888          # 服务器端口
    COUNT = 5            # 测试次数
    
    test_tcp_latency(HOST, PORT, COUNT)
