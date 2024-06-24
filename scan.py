import nmap

# 初始化nmap扫描器
nm = nmap.PortScanner()

# 目标域名或IP地址
target = 'www.biqooge.com'

# 扫描端口范围
# 常用端口范围，可以根据需要调整
scan_range = '1-1024,8080,8888,443,80,3306,5432,27017,6379'  

# 保存开放端口的列表
open_ports = []

# 执行扫描
print(f"Scanning {target} for open ports in range {scan_range} with increased speed...")
try:
    # 使用-T4选项提高扫描速度
    nm.scan(target, scan_range, arguments='-T4')
except nmap.PortScannerError as e:
    print(f"Nmap scanner error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# 输出扫描结果
for host in nm.all_hosts():
    print(f"Host: {host} ({nm[host].hostname()})")
    print(f"State: {nm[host].state()}")
    for proto in nm[host].all_protocols():
        print(f"Protocol: {proto}")
        lport = nm[host][proto].keys()
        for port in sorted(lport):
            port_state = nm[host][proto][port]['state']
            print(f"Port: {port}\tState: {port_state}")
            if port_state == 'open':
                open_ports.append(port)
                print(f"Port: {port} is open")

# 打印并保存开放的端口到文件
output_file = 'open_ports.txt'
with open(output_file, 'w') as file:
    for port in open_ports:
        file.write(f"{port}\n")
        print(f"Port: {port} is open")

print(f"Open ports saved to {output_file}")
