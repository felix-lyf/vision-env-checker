#!/usr/bin/env python3
"""
Vision Env Checker - 工业视觉运行环境检测工具
基于原有 C# WPF 项目重构，支持跨平台
"""

import sys
import platform
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QProgressBar, QGroupBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from services.checker_service import CheckerService, CheckItem, CheckStatus


class CheckWorker(QThread):
    """后台检测工作线程"""
    item_checked = pyqtSignal(object)  # 发送检测项结果
    completed = pyqtSignal()  # 检测完成信号
    progress = pyqtSignal(int)  # 进度信号
    
    def __init__(self, checker_service):
        super().__init__()
        self.checker = checker_service
        
    def run(self):
        """执行检测"""
        checks = [
            self.checker.check_vision_plus_installation,
            self.checker.check_system_requirements,
            self.checker.check_gpu,
            self.checker.check_cuda,
            self.checker.check_camera_drivers,
            self.checker.check_network_ip_config,
            self.checker.check_network_driver,
            self.checker.check_network_parameters,
            self.checker.check_firewall,
            self.checker.check_antivirus,
        ]
        
        total = len(checks)
        for i, check_func in enumerate(checks):
            self.msleep(500)  # 模拟检测延迟
            item = check_func()
            self.item_checked.emit(item)
            self.progress.emit(int((i + 1) / total * 100))
        
        self.msleep(300)
        self.completed.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Env Checker - 工业视觉运行环境检测工具 v1.0")
        self.setGeometry(100, 100, 900, 700)
        
        self.checker_service = CheckerService()
        self.check_worker = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题区域
        title_label = QLabel("🔍 工业视觉运行环境检测工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 系统信息区域
        info_group = QGroupBox("系统信息")
        info_layout = QHBoxLayout(info_group)
        
        self.system_info_label = QLabel(f"""
            <b>操作系统:</b> {platform.system()} {platform.release()}<br>
            <b>平台:</b> {platform.machine()}<br>
            <b>Python:</b> {platform.python_version()}
        """)
        self.system_info_label.setStyleSheet("font-size: 12px; padding: 5px;")
        info_layout.addWidget(self.system_info_label)
        main_layout.addWidget(info_group)
        
        # 检测结果表格
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["序号", "检测项", "状态", "描述"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.result_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #ddd;
            }
        """)
        result_layout.addWidget(self.result_table)
        main_layout.addWidget(result_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 开始检测")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_btn.clicked.connect(self.start_check)
        button_layout.addWidget(self.start_btn)
        
        self.export_btn = QPushButton("📄 导出报告")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                padding: 12px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空结果")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                padding: 12px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # 状态栏
        self.status_label = QLabel("就绪 - 点击「开始检测」按钮开始环境检查")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
    def start_check(self):
        """开始检测"""
        self.result_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.status_label.setText("正在检测中，请稍候...")
        self.status_label.setStyleSheet("color: #3498db; padding: 5px;")
        
        # 创建并启动工作线程
        self.check_worker = CheckWorker(self.checker_service)
        self.check_worker.item_checked.connect(self.on_item_checked)
        self.check_worker.completed.connect(self.on_check_completed)
        self.check_worker.progress.connect(self.on_progress_update)
        self.check_worker.start()
        
    def on_item_checked(self, item: CheckItem):
        """处理单个检测项完成"""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        # 序号
        self.result_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # 检测项
        title_item = QTableWidgetItem(item.title)
        title_item.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.result_table.setItem(row, 1, title_item)
        
        # 状态
        status_item = QTableWidgetItem(item.status.value)
        if item.status == CheckStatus.SUCCESS:
            status_item.setBackground(QColor("#d4edda"))
            status_item.setForeground(QColor("#155724"))
        elif item.status == CheckStatus.WARNING:
            status_item.setBackground(QColor("#fff3cd"))
            status_item.setForeground(QColor("#856404"))
        else:  # ERROR
            status_item.setBackground(QColor("#f8d7da"))
            status_item.setForeground(QColor("#721c24"))
        self.result_table.setItem(row, 2, status_item)
        
        # 描述
        self.result_table.setItem(row, 3, QTableWidgetItem(item.description))
        
        # 自动滚动到最新行
        self.result_table.scrollToBottom()
        
    def on_progress_update(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def on_check_completed(self):
        """检测完成"""
        self.start_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.status_label.setText("✅ 检测完成！")
        self.status_label.setStyleSheet("color: #27ae60; padding: 5px;")
        
        # 统计结果
        success_count = sum(1 for item in self.checker_service.results 
                          if item.status == CheckStatus.SUCCESS)
        warning_count = sum(1 for item in self.checker_service.results 
                          if item.status == CheckStatus.WARNING)
        error_count = sum(1 for item in self.checker_service.results 
                        if item.status == CheckStatus.ERROR)
        
        QMessageBox.information(
            self, 
            "检测完成", 
            f"检测完成！\n\n"
            f"✅ 通过: {success_count} 项\n"
            f"⚠️ 警告: {warning_count} 项\n"
            f"❌ 错误: {error_count} 项"
        )
        
    def export_report(self):
        """导出检测报告"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存检测报告",
            f"环境检测报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;HTML Files (*.html)"
        )
        
        if file_path:
            try:
                self.checker_service.export_report(file_path)
                QMessageBox.information(self, "导出成功", f"报告已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出报告时出错:\n{str(e)}")
                
    def clear_results(self):
        """清空结果"""
        self.result_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.checker_service.results.clear()
        self.status_label.setText("就绪 - 点击「开始检测」按钮开始环境检查")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        self.export_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
