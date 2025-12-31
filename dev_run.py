import subprocess
import signal
import sys
import os
import time

# 配置各服务的启动命令
backend_cmd = [sys.executable, "-m", "backend.main"]
frontend_cmd = ["npm", "run", "dev"] # shell=True 会处理扩展名
frontend_cwd = os.path.join(os.getcwd(), "frontend")

processes = []

def kill_processes():
    print("\n[Buddy] 正在关闭所有服务...")
    for p in processes:
        try:
            # 在 Windows 上彻底结束进程树
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], capture_output=True)
        except:
            p.terminate()
    print("[Buddy] 已安全退出。")

def signal_handler(sig, frame):
    kill_processes()
    sys.exit(0)

# 注册 Ctrl+C 信号
signal.signal(signal.SIGINT, signal_handler)

def main():
    print("="*40)
    print("    Buddy 探针选题系统 - 一键启动器")
    print("="*40)

    try:
        # 启动后端 (新窗口)
        print("[1/2] 正在启动后端服务 (新窗口)...")
        backend_proc = subprocess.Popen(
            backend_cmd, 
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            shell=True if os.name == 'nt' else False
        )
        processes.append(backend_proc)

        # 启动前端 (新窗口)
        print("[2/2] 正在启动前端服务 (新窗口)...")
        frontend_proc = subprocess.Popen(
            frontend_cmd, 
            cwd=frontend_cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            shell=True
        )
        processes.append(frontend_proc)

        print("\n🚀 服务已启动！")
        print("   - 后端入口: http://127.0.0.1:8321")
        print("   - 前端入口: http://localhost:5173")
        print("\n💡 提示: 按 Ctrl + C 可同时关闭前后端并释放端口。")
        print("-" * 40)

        # 实时合并输出日志（可选，为了整洁我们只在报错时提示）
        # 这里为了简单，我们只是等待
        while True:
            # 检查子进程是否意外退出
            if backend_proc.poll() is not None:
                print("❌ 后端服务意外停止，请确认配置是否正确。")
                break
            if frontend_proc.poll() is not None:
                print("❌ 前端服务意外停止，请确认依赖是否已安装。")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        kill_processes()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        kill_processes()

if __name__ == "__main__":
    main()
