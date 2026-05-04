import sys
import urllib.request

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
            # 过滤空行与注释
            if not line or line.startswith('#'):
                continue
            
            # 通用规则清洗逻辑，兼容 Mihomo/Clash 与 Geosite 格式
            # 1. 处理带逗号的格式 (如 "DOMAIN-SUFFIX,example.com")
            if ',' in line:
                line = line.split(',', 1)[1].strip()
            
            # 2. 处理前缀 (去除 "+." 或 "." 等无用修饰符)
            domain = line.lstrip('+.').strip()
            
            if domain:
                domains.add(domain)
                parsed_count += 1
                
        # 兜底校验：如果 HTTP 200 但文件内容为空（作者删除了所有规则但保留了文件）
        if parsed_count == 0:
            raise Exception("文件内容为空或无有效规则格式")
            
        print(f"[*] 成功拉取并解析 {r_type} 规则: {url} (新增 {parsed_count} 条)")

    except Exception as e:
        # 触发“一票否决”保护机制
        print(f"[!] 致命错误：拉取 [{r_type}] 规则失败！")
        print(f"[!] 失败链接：{url}")
        print(f"[!] 错误详情：{e}")
        print("[*] 保护机制已启动：为防止订阅被清空，即刻终止程序，本次不做任何文件覆写！")
        sys.exit(1)

# 若三个链接均成功拉取且包含有效内容，则执行格式转换并写入本地文件
try:
    with open("adguard_rules.txt", "w", encoding="utf-8") as f:
        f.write("! Title: Merged Reject & PCDN & HTTPDNS Rules\n")
        f.write("! Description: Auto-generated for AdGuard Home\n")
        for domain in sorted(domains):
            # 转换为 AdGuardHome 标准 Adblock 拦截格式
            f.write(f"||{domain}^\n")
            
    print(f"[*] 写入成功，最终合并去重后的规则总数为：{len(domains)} 条。")
    
except Exception as e:
    print(f"[!] 文件写入失败: {e}")
    sys.exit(1)
