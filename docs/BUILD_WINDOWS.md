# 为 Windows 打包可执行文件

## 方法：使用 PyInstaller

### 1. 在 Windows 电脑上安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
pip install pyinstaller

# 或者使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 打包为单文件 EXE

```bash
# 简单打包（推荐）
pyinstaller --onefile --windowed --name "VisionEnvChecker" src/main.py

# 包含图标（如果有的话）
pyinstaller --onefile --windowed --icon=assets/icon.ico --name "VisionEnvChecker" src/main.py

# 使用 spec 文件打包（更完整）
pyinstaller VisionEnvChecker.spec
```

### 3. 找到生成的 EXE 文件

打包完成后，可执行文件在：
```
dist/VisionEnvChecker.exe
```

### 4. 分发给用户

将 `dist/VisionEnvChecker.exe` 复制到任意 Windows 电脑，**双击即可运行**，无需安装 Python 或其他依赖。

---

## 打包选项说明

| 选项 | 说明 |
|------|------|
| `--onefile` | 打包为单个 EXE 文件（推荐） |
| `--windowed` | Windows GUI 程序，不显示命令行窗口 |
| `--icon` | 设置程序图标 |
| `--name` | 设置输出文件名 |

---

## 减小文件大小

生成的 EXE 文件可能较大（50-100MB），因为包含了 Python 运行时和所有依赖。

优化方法：
1. 使用 UPX 压缩（自动）
2. 使用 `--exclude-module` 排除不需要的模块
3. 使用虚拟环境，只安装必要的包

---

## 常见问题

### 1. 运行时提示缺少 DLL
如果打包后在其他电脑上运行报错，尝试：
```bash
pyinstaller --onefile --windowed --add-binary "path/to/dll;." src/main.py
```

### 2. 杀毒软件误报
PyInstaller 打包的程序有时会被杀毒软件误报，可以：
- 添加数字签名（需要证书）
- 告知用户添加信任
- 使用 Nuitka 替代 PyInstaller

### 3. 文件太大
使用 Nuitka 编译可以获得更小的体积：
```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console src/main.py
```
