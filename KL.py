# 导入所需的库
import requests  # 用于发送HTTP请求
import threading  # 用于多线程
from tqdm import tqdm  # 用于显示进度条

# 创建一个线程锁，用于线程安全地写入文件
lock = threading.Lock()

# 定义一个函数，检查URL有效性，并将其写入文件
def check_url(base_url, directory, file_path, headers, proxies, total, pbar):
    # 构造完整的URL
    full_url = f"{base_url.rstrip('/')}/{directory.lstrip('/')}"
    try:
        # 发送GET请求
        response = requests.get(full_url, headers=headers, proxies=proxies, timeout=5)
        # 如果响应状态码为200，表示URL有效
        if response.status_code == 200:
            # 使用线程锁来确保文件写入的线程安全
            with lock:
                with open(file_path, 'a', encoding='utf-8') as success_file:


                    success_file.write(full_url + '\n')
            # 打印有效目录的信息
            print(f"有效目录---> {full_url} (状态码: {response.status_code})")
        else:
            # 打印无效目录的信息
            print(f"无效目录---> {full_url} (状态码: {response.status_code})")
    except requests.RequestException as e:
        # 如果请求失败，打印错误信息
        print(f"请求失败: {full_url} (错误: {e})")
    finally:
        # 更新进度条
        pbar.update(1)

#检查文件
def check_urls(base_url, file_path, threads, headers, proxies):
    try:
        # 读取包含目录路径的文件
        with open(file_path, 'r', encoding='utf-8') as file:
            directories = [line.strip() for line in file if line.strip()]#列表推导式
    except FileNotFoundError:
        # 如果文件不存在，打印错误信息并返回
        print(f"错误: 文件 '{file_path}' 不存在")
        return
    except UnicodeDecodeError:
        # 如果文件编码格式不正确，打印错误信息并返回
        print(f"错误: 文件 '{file_path}' 编码格式不正确，无法读取")
        return

    # 获取总目录数
    total = len(directories)
    # 创建进度条
    pbar = tqdm(total=total)

    # 创建一个线程列表
    threads_list = []

    # 遍历目录列表，为每个目录创建一个线程
    for directory in directories:
        thread = threading.Thread(target=check_url, args=(base_url, directory, '成功URL.txt', headers, proxies, total, pbar))
        threads_list.append(thread)
        thread.start()

        # 如果线程数量达到指定的线程数，等待这些线程完成
        if len(threads_list) >= threads:
            for t in threads_list:
                t.join()
            threads_list = []

    # 等待剩余的线程完成
    for t in threads_list:
        t.join()
    # 关闭进度条
    pbar.close()

# 定义主函数
def main():
    # 获取用户输入的基础URL、文件名、线程数量、代理
    base_url = input("请输入基础URL: ")
    file_path = input("请输入字典的文件名(字典需放在代码文件同目录下): ")
    threads = int(input("请输入线程数量(1-30): "))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    proxies = input("请输入代理（如有，格式为http://proxy:port，否则留空）: ")
    if proxies:
        # 如果输入了代理，创建代理字典

        proxies = {"http": proxies, "https": proxies}
    else:
        # 如果没有输入代理，设置为None
        proxies = None

    # 调用check_urls函数开始检查URL
    check_urls(base_url, file_path, threads, headers, proxies)

# 程序入口点
if __name__ == "__main__":
    main()