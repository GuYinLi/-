# 该程序可以记录某个安装程序安装文件的所有路径，并且能精准的给记录下来，记录完成会创建一个txt文档，txt文档里面就包含了安装程序安装文件的路径了。
# 我无法确定该程序的兼容性和稳定性，想要重源代码中运行该程序需要用到PyCharm，遇到问题可以自行解决。
                                                                                                #2024-9-3 4:00
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time


class ProcessFileHandler(FileSystemEventHandler):
    def __init__(self, process_id, output_file):
        self.process_id = process_id
        self.output_file = output_file

    def on_created(self, event):
        if not event.is_directory:
            try:
                process = psutil.Process(self.process_id)
                if process.is_running():
                    with open(self.output_file, "a", encoding="utf-8") as f:
                        f.write(f"Created: {event.src_path}\n")
                    print(f"Recorded: {event.src_path}")  # 添加打印语句用于调试
            except psutil.NoSuchProcess:
                return


def get_user_processes():
    user_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if proc.info['username'] not in ['NT AUTHORITY\\SYSTEM', 'NT AUTHORITY\\LOCAL SERVICE',
                                             'NT AUTHORITY\\NETWORK SERVICE'] and proc.info['username']:
                user_processes.append((proc.info['pid'], proc.info['name']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return user_processes


def update_process_list():
    process_list.delete(0, tk.END)
    for pid, name in get_user_processes():
        process_list.insert(tk.END, f"{pid}: {name}")


def start_monitoring():
    global observer  # 使用全局变量以便后续停止监控
    selected = process_list.curselection()
    if selected:
        pid = int(process_list.get(selected[0]).split(':')[0])
        output_file = "installation_paths.txt"

        event_handler = ProcessFileHandler(pid, output_file)
        observer = Observer()
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f"{drive}:\\"
            if os.path.exists(path):
                observer.schedule(event_handler, path, recursive=True)

        observer.start()
        status_label.config(text=f"正在监控PID {pid}的文件创建...")
        messagebox.showinfo("监控开始", f"开始监控PID {pid}的文件创建。\n记录将保存在 {output_file}")

        stop_button = tk.Button(root, text="停止监控", command=stop_monitoring)
        stop_button.pack()
    else:
        status_label.config(text="请先选择一个进程")


def stop_monitoring():
    global observer
    if observer:
        observer.stop()
        observer.join()
        status_label.config(text="监控已停止")
        messagebox.showinfo("监控停止", "文件监控已停止")


# 创建主窗口
root = tk.Tk()
root.title("安装文件路径记录器")

# 创建进程列表
process_list = tk.Listbox(root, width=100, height=30)
process_list.pack()

# 刷新按钮
refresh_button = tk.Button(root, text="刷新进程列表", command=update_process_list)
refresh_button.pack()

# 开始监控按钮
start_button = tk.Button(root, text="开始监控", command=start_monitoring)
start_button.pack()

# 状态标签
status_label = tk.Label(root, text="")
status_label.pack()

# 初始化进程列表
update_process_list()

# 全局变量
observer = None

root.mainloop()