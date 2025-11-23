#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：检查和修复规则转换问题
"""

import os

def debug_conversion():
    """调试转换过程"""
    print("🔍 调试规则转换过程...")
    
    # 检查下载的文件
    files = [
        "rules/hBlock.txt",
        "rules/Multi_NORMAL.txt", 
        "rules/Fanboy-CookieMonster.txt"
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            print(f"\n📄 检查文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"总行数: {len(lines)}")
            
            # 显示前10行
            print("前10行内容:")
            for i, line in enumerate(lines[:10]):
                print(f"{i+1:2d}: {line.strip()}")
            
            # 查找域名规则
            domain_lines = []
            for line in lines[:50]:  # 只检查前50行
                line = line.strip()
                if line.startswith('||') or line.startswith('|') or '0.0.0.0' in line:
                    domain_lines.append(line)
            
            print(f"\n找到的域名规则示例 (前5个):")
            for i, line in enumerate(domain_lines[:5]):
                print(f"{i+1}: {line}")

def test_conversion():
    """测试转换逻辑"""
    print("\n🧪 测试转换逻辑...")
    
    test_rules = [
        "||example.com^",
        "|test.com",
        "0.0.0.0 ads.com",
        "127.0.0.1 tracker.com",
        "DOMAIN,bad.com",
        "good.com"
    ]
    
    print("测试规则:")
    for rule in test_rules:
        print(f"  {rule}")
    
    # 模拟转换
    converted = []
    for line in test_rules:
        line = line.strip()
        
        if line.startswith('||'):
            domain = line[2:].split('^')[0].split('/')[0]
            if domain and '.' in domain and len(domain) > 3:
                converted.append(f"DOMAIN,{domain}")
        elif line.startswith('|'):
            domain = line[1:].split('^')[0].split('/')[0]
            if domain and '.' in domain and len(domain) > 3:
                converted.append(f"DOMAIN,{domain}")
        elif line.startswith('0.0.0.0') or line.startswith('127.0.0.1'):
            parts = line.split()
            if len(parts) >= 2:
                domain = parts[1]
                if '.' in domain and len(domain) > 3:
                    converted.append(f"DOMAIN,{domain}")
        elif line.startswith('DOMAIN,'):
            converted.append(line)
        elif '.' in line and len(line) > 3:
            if not line.startswith(('http', 'www', 'ftp')):
                converted.append(f"DOMAIN,{line}")
    
    print("\n转换结果:")
    for rule in converted:
        print(f"  {rule}")

if __name__ == "__main__":
    debug_conversion()
    test_conversion()
