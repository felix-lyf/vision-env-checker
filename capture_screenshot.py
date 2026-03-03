import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# 导入主窗口
sys.path.insert(0, 'src')
from main import MainWindow

# 创建应用
app = QApplication(sys.argv)
app.setStyle('Fusion')

# 创建主窗口
window = MainWindow()
window.show()

# 处理事件
app.processEvents()

# 截图
screenshot = window.grab()
screenshot.save('/tmp/vision_env_checker_screenshot.png')

print("✅ 截图已保存: /tmp/vision_env_checker_screenshot.png")
print(f"尺寸: {screenshot.width()}x{screenshot.height()}")

# 模拟点击开始检测按钮，然后再次截图
from PyQt6.QtTest import QTest
from PyQt6.QtCore import QTimer

# 延迟后截图检测中的状态
QTimer.singleShot(1000, lambda: [
    window.start_btn.click(),
    app.processEvents(),
    QTimer.singleShot(2000, lambda: [
        screenshot2 := window.grab(),
        screenshot2.save('/tmp/vision_env_checker_running.png'),
        print("✅ 运行中截图已保存: /tmp/vision_env_checker_running.png"),
        app.quit()
    ])
])

app.exec()
