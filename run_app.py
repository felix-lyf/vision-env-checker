import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加 src 到路径
sys.path.insert(0, os.path.join(current_dir, 'src'))

# 导入 streamlit
import streamlit.web.cli as stcli

# web_app.py 路径
web_app_path = os.path.join(current_dir, "web_app.py")

# 如果 web_app.py 不存在，创建一个简单的
if not os.path.exists(web_app_path):
    print("警告：web_app.py 不存在，创建默认版本...")
    with open(web_app_path, 'w', encoding='utf-8') as f:
        f.write('''import streamlit as st
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

st.set_page_config(
    page_title="Vision Env Checker",
    page_icon="🔧",
    layout="centered"
)

st.title("🔧 Vision Env Checker")
st.markdown("### 工业视觉运行环境检测工具")

if st.button("🔍 一键检测", type="primary", use_container_width=True):
    st.info("检测功能需要在本地运行 Python 环境")
    st.markdown("""
    请确保：
    1. 安装了 Python 3.8+
    2. 安装了依赖：`pip install -r requirements.txt`
    3. 运行：`streamlit run web_app.py`
    """)
''')

# 启动 Streamlit
sys.argv = ["streamlit", "run", web_app_path, "--server.headless=true", "--server.port=8501"]
stcli.main()
