import sys
import urllib.request
from datetime import datetime, timezone, timedelta

tz_bj = timezone(timedelta(hours=8))
current_time = datetime.now(tz_bj).strftime("%Y-%m-%d %H:%M:%S")

urls_to_fetch =[
    ("reject", "https://raw.githubusercontent.com/JohnsonRan/CRules/master/rules/reject.txt"),
    ("pcdn", "https://raw.githubusercontent.com/ForestL18/rules-dat/mihomo/geo/classical/pcdn.list"),
    ("httpdns", "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/category-httpdns-cn.list")
]

domains = set()

for r_type, url in urls_to_fetch:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req, timeout=15)
        
        if response.status != 200:
            raise Exception(f"HTTP 状态码异常: {response.status}")
            
        lines = response.read().decode('utf-8').splitlines()
        
        parsed_count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ',' in line:
                line = line.split(',', 1)[1].strip()
            domain = line.lstrip('+.').strip()
            
            if domain:
                domains.add(domain)
                parsed_count += 1
                
        if parsed_count == 0:
            raise Exception("文件内容为空或无有效规则格式")
            
        print(f"[*] 成功拉取并解析 {r_type} 规则: {url} (新增 {parsed_count} 条)")

    except Exception as e:
        print(f"[!] 致命错误：拉取 [{r_type}] 规则失败！链接：{url}。详情：{e}")
        print("[*] 保护机制已启动：为防止订阅被清空，即刻终止程序，本次不做任何文件覆写！")
        sys.exit(1)

try:
    with open("adguard_rules.txt", "w", encoding="utf-8") as f:
        f.write("! Title: Merged Reject & PCDN & HTTPDNS Rules\n")
        f.write("! Description: Auto-generated for AdGuard Home\n")
        f.write(f"! Version: {current_time}\n")
        
        for domain in sorted(domains):
            f.write(f"||{domain}^\n")
            
    print(f"[*] 写入成功，规则总数: {len(domains)} 条。当前版本: {current_time}")
except Exception as e:
    print(f"[!] 文件写入失败: {e}")
    sys.exit(1)
