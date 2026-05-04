import sys
import urllib.request

urls_to_fetch =[
    ("reject", "https://raw.githubusercontent.com/JohnsonRan/CRules/master/rules/reject.txt"),
    ("pcdn", "https://raw.githubusercontent.com/ForestL18/rules-dat/mihomo/geo/classical/pcdn.list")
]

domains = set()
fetched_types = set()

for r_type, url in urls_to_fetch:
    if r_type in fetched_types and r_type == "reject":
        continue
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req)
        lines = response.read().decode('utf-8').splitlines()
        
        for line in lines:
            line = line.strip()
            # 过滤空行与注释
            if not line or line.startswith('#'):
                continue
            
            domain = ""
            if r_type == "reject":
                # 原始格式如: "+.example.com" 或 "example.com"
                domain = line.lstrip('+.').strip()
            elif r_type == "pcdn":
                # 原始格式如: "DOMAIN-SUFFIX,example.com"
                if ',' in line:
                    domain = line.split(',', 1)[1].strip()
                else:
                    domain = line.strip()
            
            # AdGuardHome 标准 Adblock 格式: ||example.com^
            if domain:
                domains.add(domain)
                
        fetched_types.add(r_type)
        print(f"[*] 成功拉取并解析 {r_type} 规则: {url}")
    except Exception as e:
        print(f"[!] 拉取失败 {r_type} ({url}): {e}")

SAFE_THRESHOLD = 10

if len(domains) < SAFE_THRESHOLD:
    print(f"[!] 致命异常：当前抓取到的总规则数 ({len(domains)}) 低于安全阈值 ({SAFE_THRESHOLD})。")
    print("[!] 可能原因：上游仓库删库、大规模删减规则或 GitHub Raw 域名遭 SNI 阻断。")
    print("[*] 触发保护机制：终止覆写本地文件，保留上一次的旧版订阅规则。")
    sys.exit(1)

# 写入 AdGuardHome 格式文件
with open("adguard_rules.txt", "w", encoding="utf-8") as f:
    f.write("! Title: Merged Reject & PCDN Rules\n")
    f.write("! Description: Auto-generated for AdGuard Home\n")
    for domain in sorted(domains):
        f.write(f"||{domain}^\n")

print(f"[*] 处理完成，共生成 {len(domains)} 条去重规则。")
