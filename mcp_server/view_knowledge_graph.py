#!/usr/bin/env python3
"""
Graphiti知识图谱查看工具
用于查看和管理知识图谱中的内容
"""

import requests
import json
from datetime import datetime
import sys

class GraphitiViewer:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def search_nodes(self, query, max_nodes=10, group_ids=None):
        """搜索节点"""
        url = f"{self.base_url}/search_memory_nodes"
        data = {
            "query": query,
            "max_nodes": max_nodes
        }
        if group_ids:
            data["group_ids"] = group_ids
            
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索节点失败: {e}")
            return None
    
    def search_facts(self, query, max_facts=10, group_ids=None):
        """搜索事实"""
        url = f"{self.base_url}/search_memory_facts"
        data = {
            "query": query,
            "max_facts": max_facts
        }
        if group_ids:
            data["group_ids"] = group_ids
            
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索事实失败: {e}")
            return None
    
    def get_episodes(self, last_n=10, group_id=None):
        """获取最近的episodes"""
        url = f"{self.base_url}/get_episodes"
        data = {"last_n": last_n}
        if group_id:
            data["group_id"] = group_id
            
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取episodes失败: {e}")
            return None
    
    def add_episode(self, name, content, source="text", group_id=None):
        """添加新的episode"""
        url = f"{self.base_url}/add_memory"
        data = {
            "name": name,
            "episode_body": content,
            "source": source
        }
        if group_id:
            data["group_id"] = group_id
            
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"添加episode失败: {e}")
            return None
    
    def check_service_status(self):
        """检查服务状态"""
        try:
            response = requests.get(self.base_url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def print_nodes(self, nodes_data):
        """打印节点信息"""
        if not nodes_data:
            print("没有找到节点数据")
            return
            
        print("\n=== 节点信息 ===")
        for i, node in enumerate(nodes_data, 1):
            print(f"\n{i}. 节点名称: {node.get('name', 'N/A')}")
            print(f"   节点类型: {node.get('labels', ['N/A'])}")
            print(f"   摘要: {node.get('summary', 'N/A')[:100]}...")
            print(f"   创建时间: {node.get('created_at', 'N/A')}")
            if 'group_id' in node:
                print(f"   组ID: {node['group_id']}")
    
    def print_facts(self, facts_data):
        """打印事实信息"""
        if not facts_data:
            print("没有找到事实数据")
            return
            
        print("\n=== 事实信息 ===")
        for i, fact in enumerate(facts_data, 1):
            print(f"\n{i}. 事实: {fact.get('fact', 'N/A')}")
            print(f"   相关实体: {fact.get('entities', [])}")
            print(f"   创建时间: {fact.get('created_at', 'N/A')}")
            if 'group_id' in fact:
                print(f"   组ID: {fact['group_id']}")
    
    def print_episodes(self, episodes_data):
        """打印episode信息"""
        if not episodes_data:
            print("没有找到episode数据")
            return
            
        print("\n=== Episodes信息 ===")
        for i, episode in enumerate(episodes_data, 1):
            print(f"\n{i}. 名称: {episode.get('name', 'N/A')}")
            print(f"   内容: {episode.get('content', 'N/A')[:100]}...")
            print(f"   来源: {episode.get('source', 'N/A')}")
            print(f"   创建时间: {episode.get('created_at', 'N/A')}")
            if 'group_id' in episode:
                print(f"   组ID: {episode['group_id']}")

def main():
    viewer = GraphitiViewer()
    
    # 检查服务状态
    print("🔍 检查Graphiti服务状态...")
    if not viewer.check_service_status():
        print("❌ 无法连接到Graphiti服务")
        print("请确保Docker服务正在运行: docker compose up -d")
        sys.exit(1)
    
    print("✅ Graphiti服务运行正常")
    
    while True:
        print("\n" + "="*50)
        print("Graphiti知识图谱查看工具")
        print("="*50)
        print("1. 搜索节点")
        print("2. 搜索事实")
        print("3. 查看最近的episodes")
        print("4. 添加新的episode")
        print("5. 退出")
        print("="*50)
        
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == "1":
            query = input("请输入搜索关键词: ").strip()
            if query:
                print(f"\n🔍 搜索节点: {query}")
                nodes = viewer.search_nodes(query, max_nodes=5)
                viewer.print_nodes(nodes)
        
        elif choice == "2":
            query = input("请输入搜索关键词: ").strip()
            if query:
                print(f"\n🔍 搜索事实: {query}")
                facts = viewer.search_facts(query, max_facts=5)
                viewer.print_facts(facts)
        
        elif choice == "3":
            print("\n📋 获取最近的episodes")
            episodes = viewer.get_episodes(last_n=5)
            viewer.print_episodes(episodes)
        
        elif choice == "4":
            name = input("请输入episode名称: ").strip()
            content = input("请输入episode内容: ").strip()
            if name and content:
                print(f"\n➕ 添加episode: {name}")
                result = viewer.add_episode(name, content)
                if result:
                    print("✅ Episode添加成功")
                else:
                    print("❌ Episode添加失败")
        
        elif choice == "5":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main() 