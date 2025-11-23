#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行脚本：下载广告规则并生成Loon配置
"""

import sys
import os

def main():
    print("🚀 Loon广告规则配置生成器")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 需要Python 3.6或更高版本")
        return
    
    # 安装依赖
    try:
        import requests
    except ImportError:
        print("📦 正在安装requests库...")
        os.system("pip install requests")
        import requests
    
    print("\n📥 第一步：下载广告规则...")
    try:
        from download_adblock_rules import AdBlockDownloader
        downloader = AdBlockDownloader()
        downloader.download_and_process_all()
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return
    
    print("\n⚙️  第二步：生成Loon配置...")
    try:
        from generate_loon_config import LoonConfigGenerator
        generator = LoonConfigGenerator()
        generator.generate_loon_config()
        generator.generate_simple_rule_file()
    except Exception as e:
        print(f"❌ 配置生成失败: {e}")
        return
    
    print("\n🎉 完成! 文件列表:")
    print("📁 rules/merged_adblock.list - 聚合的广告规则")
    print("📄 loon_adblock_config.conf - 完整Loon配置")
    print("📋 adblock_rules_only.list - 简化规则文件")
    
    print("\n📖 使用方法:")
    print("1. 复制loon_adblock_config.conf中的[Remote Rule]部分到你的Loon配置")
    print("2. 或者将adblock_rules_only.list上传到网络服务器，在Loon中添加远程规则")

if __name__ == "__main__":
    main()
