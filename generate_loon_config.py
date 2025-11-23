#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Loon配置文件脚本
将聚合的广告规则集成到Loon配置中
"""

import os
import time
from datetime import datetime

class LoonConfigGenerator:
    def __init__(self, rules_file="rules/merged_adblock.list"):
        self.rules_file = rules_file
    
    def generate_loon_config(self, output_file="loon_adblock_config.conf"):
        """生成包含广告拦截规则的Loon配置文件"""
        
        # 读取聚合的广告规则
        adblock_rules = []
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 跳过注释行，只保留规则
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('#!'):
                        adblock_rules.append(line)
        
        # 生成Loon配置
        config_content = f"""#!/bin/bash
# Loon 广告拦截配置文件
# 自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 包含 {len(adblock_rules)} 条广告拦截规则

[Remote Rule]
# 聚合广告拦截规则
"""
        
        # 添加广告拦截规则
        for rule in adblock_rules:
            config_content += f"{rule}, policy=REJECT, tag=聚合广告拦截, enabled=true\n"
        
        # 添加其他推荐的规则
        config_content += """
# 推荐添加的其他规则
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Apple/Apple_Domain.list, policy=🇯🇵 日本节点, tag=Apple_Domain, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Apple/Apple.list, policy=🇯🇵 日本节点, tag=Apple.list, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/China/China_Domain.list, policy=DIRECT, tag=China-Domain, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/China/China.list, policy=DIRECT, tag=China, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Gemini/Gemini.list, policy=🇺🇸 美国节点, tag=Gemini, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Claude/Claude.list, policy=🇺🇸 美国节点, tag=Claude, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/OpenAI/OpenAI.list, policy=🇺🇸 美国节点, tag=OpenAI, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Google/Google.list, policy=🇺🇸 美国节点, tag=Google, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Spotify/Spotify.list, policy=🍿 国外媒体, tag=Spotify, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/TikTok/TikTok.list, policy=🍿 国外媒体, tag=TikTok, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/YouTube/YouTube.list, policy=🍿 国外媒体, tag=YouTube, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Reddit/Reddit.list, policy=📖 Reddit, tag=Reddit, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Pixiv/Pixiv.list, policy=🇯🇵 日本节点, tag=Pixiv, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/GitHub/GitHub.list, policy=🇺🇸 美国节点, tag=GitHub, enabled=true
https://whatshub.top/rule/ai.list, policy=🇺🇸 美国节点, tag=ai, enabled=true
https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Microsoft/Microsoft.list, policy=DIRECT, tag=微软, enabled=true
https://whatshub.top/rule/ASN-CN.list, policy=DIRECT, tag=ASN-CN, enabled=true

[Rule]
# 默认规则
FINAL,🇯🇵 日本节点
"""
        
        # 写入配置文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✓ Loon配置文件已生成: {output_file}")
        print(f"✓ 包含 {len(adblock_rules)} 条广告拦截规则")
        
        return output_file
    
    def generate_simple_rule_file(self, output_file="adblock_rules_only.list"):
        """生成纯规则文件，可以直接导入Loon"""
        
        if not os.path.exists(self.rules_file):
            print(f"❌ 规则文件不存在: {self.rules_file}")
            return None
        
        # 读取聚合规则
        with open(self.rules_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成简化版本
        simple_content = f"""# 聚合广告拦截规则 - Loon格式
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 使用方法: 在Loon中添加远程规则，指向此文件

"""
        
        # 添加规则
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('#!'):
                simple_content += f"{line},REJECT\n"
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(simple_content)
        
        print(f"✓ 简化规则文件已生成: {output_file}")
        return output_file

def main():
    generator = LoonConfigGenerator()
    
    print("🚀 开始生成Loon配置文件...")
    
    # 生成完整配置
    config_file = generator.generate_loon_config()
    
    # 生成简化规则文件
    simple_file = generator.generate_simple_rule_file()
    
    print("\n🎉 配置文件生成完成!")
    print(f"📄 完整配置: {config_file}")
    print(f"📋 简化规则: {simple_file}")
    print("\n📖 使用说明:")
    print("1. 将完整配置内容复制到Loon配置文件的[Remote Rule]部分")
    print("2. 或者将简化规则文件上传到网络服务器，在Loon中添加为远程规则")

if __name__ == "__main__":
    main()
