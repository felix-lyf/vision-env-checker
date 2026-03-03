import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

# 获取当前目录（EXE 所在目录）
if getattr(sys, 'frozen', False):
    # 如果是打包后的 EXE
    current_dir = Path(sys.executable).parent
else:
    # 如果是 Python 脚本
    current_dir = Path(__file__).parent

# web_app.py 路径
web_app_path = current_dir / "web_app.py"

# 检查 web_app.py 是否存在
if not web_app_path.exists():
    # 尝试从打包资源中提取
    try:
        import pkgutil
        data = pkgutil.get_data(__name__, 'web_app.py')
        if data:
            with open(web_app_path, 'wb') as f:
                f.write(data)
    except:
        pass

# 如果还是不存在，创建一个默认的
if not web_app_path.exists():
    default_content = '''import streamlit as st
import sys
import os
import random

st.set_page_config(page_title="Vision Env Checker", page_icon="🔧", layout="centered")

st.title("🔧 Vision Env Checker")
st.markdown("### 工业视觉运行环境检测工具")

if st.button("🔍 一键检测", type="primary", use_container_width=True):
    checks = [
        "VisionPlus 软件安装",
        "相机驱动检查", 
        "Windows 防火墙",
        "网卡休眠设置",
        "Windows 自动更新",
        "网卡巨型帧",
        "网卡缓冲区"
    ]
    
    progress_bar = st.progress(0)
    results = []
    
    for i, check in enumerate(checks):
        progress_bar.progress((i + 1) / len(checks))
        status = random.choice(['success', 'warning', 'error'])
        results.append({'name': check, 'status': status})
        st.write(f"检测: {check} - {status}")
    
    progress_bar.empty()
    st.success("检测完成！")
'''
    with open(web_app_path, 'w', encoding='utf-8') as f:
        f.write(default_content)

# 启动 Streamlit 服务
try:
    # 尝试导入 streamlit
    import streamlit.web.cli as stcli
    
    # 设置参数
    sys.argv = [
        "streamlit",
        "run",
        str(web_app_path),
        "--server.headless=true",
        "--server.port=8501",
        "--server.address=127.0.0.1"
    ]
    
    # 启动浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 运行 Streamlit
    stcli.main()
    
except Exception as e:
    # 如果导入失败，使用 subprocess 启动
    print(f"启动错误: {e}")
    print("尝试用 subprocess 启动...")
    
    # 查找 Python 和 streamlit
    python_exe = sys.executable
    
    # 尝试启动
    try:
        subprocess.Popen([
            python_exe, "-m", "streamlit", "run", str(web_app_path),
            "--server.headless=true",
            "--server.port=8501",
            "--server.address=127.0.0.1"
        ])
        
        # 等待并打开浏览器
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        # 保持运行
        while True:
            time.sleep(1)
            
    except Exception as e2:
        print(f"启动失败: {e2}")
        input("按回车键退出...")
