#!/usr/bin/env python3
"""
TCP/IP Latency Measurement Tool
通过TCP/IP协议测量网络延迟的工具

功能：
1. 服务器端：监听连接并响应客户端请求
2. 客户端：发送请求并测量往返时间
3. 支持多次测量和统计分析
4. 可配置的测试参数
"""

import socket
import time
import threading
import statistics
import argparse
import json
from datetime import datetime
import sys

class TCPServer:
    """TCP服务器类，用于响应客户端请求并测量延迟"""
    
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.stats = {
            'total_requests': 0,
            'total_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0,
            'latencies': []
        }
    
    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 TCP服务器启动成功")
            print(f"📍 监听地址: {self.host}:{self.port}")
            print(f"⏳ 等待客户端连接...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"🔗 客户端连接: {client_address[0]}:{client_address[1]}")
                    
                    # 为每个客户端创建新线程
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"❌ 接受连接时出错: {e}")
                        
        except Exception as e:
            print(f"❌ 启动服务器失败: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        try:
            while self.running:
                # 接收客户端数据
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # 解析请求
                try:
                    request = json.loads(data.decode('utf-8'))
                    request_type = request.get('type', 'ping')
                    timestamp = request.get('timestamp', time.time())
                    
                    if request_type == 'ping':
                        # 计算延迟
                        current_time = time.time()
                        latency = (current_time - timestamp) * 1000  # 转换为毫秒
                        
                        # 更新统计信息
                        self.update_stats(latency)
                        
                        # 发送响应
                        response = {
                            'type': 'pong',
                            'timestamp': current_time,
                            'latency': latency,
                            'server_time': datetime.now().isoformat()
                        }
                        
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        print(f"📡 请求处理完成 - 延迟: {latency:.2f}ms")
                        
                    elif request_type == 'stats':
                        # 返回统计信息
                        response = {
                            'type': 'stats_response',
                            'stats': self.get_stats()
                        }
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        
                except json.JSONDecodeError:
                    print(f"⚠️ 无效的JSON数据: {data}")
                    
        except Exception as e:
            print(f"❌ 处理客户端请求时出错: {e}")
        finally:
            client_socket.close()
            print(f"🔌 客户端断开连接: {client_address[0]}:{client_address[1]}")
    
    def update_stats(self, latency):
        """更新统计信息"""
        self.stats['total_requests'] += 1
        self.stats['total_latency'] += latency
        self.stats['latencies'].append(latency)
        
        if latency < self.stats['min_latency']:
            self.stats['min_latency'] = latency
        if latency > self.stats['max_latency']:
            self.stats['max_latency'] = latency
    
    def get_stats(self):
        """获取统计信息"""
        stats = self.stats.copy()
        if stats['latencies']:
            stats['avg_latency'] = statistics.mean(stats['latencies'])
            stats['median_latency'] = statistics.median(stats['latencies'])
            stats['std_latency'] = statistics.stdev(stats['latencies']) if len(stats['latencies']) > 1 else 0
        else:
            stats['avg_latency'] = 0
            stats['median_latency'] = 0
            stats['std_latency'] = 0
        return stats
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 服务器已停止")

class TCPClient:
    """TCP客户端类，用于发送请求并测量延迟"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.client_socket = None
        self.latencies = []
    
    def connect(self):
        """连接到服务器"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"✅ 成功连接到服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接服务器失败: {e}")
            return False
    
    def send_ping(self):
        """发送ping请求并测量延迟"""
        if not self.client_socket:
            print("❌ 未连接到服务器")
            return None
        
        try:
            # 发送请求
            request = {
                'type': 'ping',
                'timestamp': time.time()
            }
            
            start_time = time.time()
            self.client_socket.send(json.dumps(request).encode('utf-8'))
            
            # 接收响应
            response = self.client_socket.recv(1024)
            end_time = time.time()
            
            if response:
                response_data = json.loads(response.decode('utf-8'))
                latency = response_data.get('latency', (end_time - start_time) * 1000)
                self.latencies.append(latency)
                return latency
            
        except Exception as e:
            print(f"❌ 发送ping请求失败: {e}")
            return None
    
    def get_stats(self):
        """获取统计信息"""
        if not self.latencies:
            return None
        
        return {
            'count': len(self.latencies),
            'min': min(self.latencies),
            'max': max(self.latencies),
            'avg': statistics.mean(self.latencies),
            'median': statistics.median(self.latencies),
            'std': statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0
        }
    
    def close(self):
        """关闭连接"""
        if self.client_socket:
            self.client_socket.close()
        print("🔌 客户端连接已关闭")

def run_server(host='0.0.0.0', port=8888):
    """运行服务器"""
    server = TCPServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号，正在停止服务器...")
        server.stop()

def run_client(host='127.0.0.1', port=8888, count=10, interval=1.0):
    """运行客户端测试"""
    client = TCPClient(host, port)
    
    if not client.connect():
        return
    
    print(f"🚀 开始延迟测试 - 目标: {host}:{port}")
    print(f"📊 测试次数: {count}, 间隔: {interval}秒")
    print("-" * 50)
    
    try:
        for i in range(count):
            latency = client.send_ping()
            if latency is not None:
                print(f"测试 {i+1:2d}: {latency:8.2f}ms")
            else:
                print(f"测试 {i+1:2d}: 失败")
            
            if i < count - 1:  # 最后一次不需要等待
                time.sleep(interval)
        
        print("-" * 50)
        
        # 显示统计结果
        stats = client.get_stats()
        if stats:
            print("📈 测试结果统计:")
            print(f"   总测试次数: {stats['count']}")
            print(f"   最小延迟:   {stats['min']:.2f}ms")
            print(f"   最大延迟:   {stats['max']:.2f}ms")
            print(f"   平均延迟:   {stats['avg']:.2f}ms")
            print(f"   中位数延迟: {stats['median']:.2f}ms")
            print(f"   标准差:     {stats['std']:.2f}ms")
        
    except KeyboardInterrupt:
        print("\n🛑 测试被中断")
    finally:
        client.close()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TCP/IP延迟测量工具')
    parser.add_argument('mode', choices=['server', 'client'], help='运行模式: server 或 client')
    parser.add_argument('--host', default='127.0.0.1', help='主机地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888, help='端口号 (默认: 8888)')
    parser.add_argument('--count', type=int, default=10, help='测试次数 (客户端模式, 默认: 10)')
    parser.add_argument('--interval', type=float, default=1.0, help='测试间隔秒数 (客户端模式, 默认: 1.0)')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        print("🎯 启动TCP延迟测量服务器")
        run_server(args.host, args.port)
    else:
        print("🎯 启动TCP延迟测量客户端")
        run_client(args.host, args.port, args.count, args.interval)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
        sys.exit(0)
