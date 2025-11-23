# Loon 广告规则下载和聚合工具

这个工具可以帮你下载多个广告规则源，转换成Loon格式，并聚合成一个配置文件。

## 功能特点

- 🌐 **多源下载**: 支持下载10个主流广告规则源
- 🔄 **格式转换**: 自动识别并转换Adblock、Hosts、Surge等格式
- 📦 **智能聚合**: 去重合并所有规则，生成单一配置文件
- ⚙️ **Loon兼容**: 生成Loon可直接使用的配置格式
- 🚀 **一键运行**: 简单命令完成所有操作

## 支持的规则源

1. **1Hosts (Lite)** - 轻量级广告拦截
2. **hBlock** - 基于hosts的广告拦截
3. **Multi NORMAL** - 多功能广告拦截
4. **Fanboy-CookieMonster** - Cookie追踪拦截
5. **EasylistChina** - 中文广告拦截
6. **AdGuardSDNSFilter** - AdGuard DNS过滤
7. **rejectAd.list** - 拒绝广告列表
8. **Advertising_Domain.list** - 广告域名列表
9. **Advertising.list** - 广告综合列表
10. **anti-ad.net** - 反广告网络

## 快速开始

### 方法一：一键运行（推荐）

```bash
python run_adblock_setup.py
```

这会自动完成所有步骤：下载规则 → 转换格式 → 聚合生成配置文件。

### 方法二：分步执行

```bash
# 1. 下载广告规则
python download_adblock_rules.py

# 2. 生成Loon配置
python generate_loon_config.py
```

## 输出文件

运行完成后会生成以下文件：

- 📁 `rules/merged_adblock.list` - 聚合的广告规则（Loon格式）
- 📄 `loon_adblock_config.conf` - 完整的Loon配置文件
- 📋 `adblock_rules_only.list` - 简化规则文件

## 使用方法

### 方法1：复制配置内容

1. 打开 `loon_adblock_config.conf`
2. 复制 `[Remote Rule]` 部分的内容
3. 粘贴到你的Loon配置文件中

### 方法2：使用远程规则

1. 将 `adblock_rules_only.list` 上传到网络服务器
2. 在Loon中添加远程规则：`https://your-server.com/adblock_rules_only.list`
3. 策略设置为 `REJECT`

### 方法3：本地文件

1. 将 `merged_adblock.list` 传输到手机
2. 在Loon中添加本地规则文件

## 配置示例

生成的配置会包含类似这样的规则：

```
[Remote Rule]
DOMAIN,ads.example.com, policy=REJECT, tag=聚合广告拦截, enabled=true
DOMAIN-SUFFIX,tracker.com, policy=REJECT, tag=聚合广告拦截, enabled=true
...
```

## 高级用法

### 自定义输出目录

```bash
python download_adblock_rules.py --output-dir custom_rules
```

### 添加自定义规则源

编辑 `download_adblock_rules.py` 中的 `rule_sources` 字典：

```python
rule_sources = {
    "CustomRule": "https://your-custom-source.com/rules.txt",
    # ... 其他规则源
}
```

## 注意事项

- ⚠️ 首次运行需要安装requests库：`pip install requests`
- ⚠️ 网络连接正常，能访问GitHub和CDN资源
- ⚠️ 规则文件较大，下载可能需要几分钟
- ⚠️ 建议定期更新规则（每周一次）

## 故障排除

### 下载失败
- 检查网络连接
- 确认防火墙设置
- 尝试使用代理

### 转换错误
- 检查规则源格式是否变化
- 查看控制台错误信息

### Loon导入失败
- 确认规则格式正确
- 检查文件编码（应为UTF-8）
- 验证Loon版本兼容性

## 更新日志

- **v1.0** - 初始版本，支持10个主流广告规则源
- 支持3种格式转换：Adblock、Hosts、Surge
- 自动去重和聚合
- 生成Loon兼容配置

## 许可证

MIT License - 可自由使用和修改
