#!/usr/bin/env python3
"""
Vision Env Checker - 工业视觉运行环境检测工具
V2.0 - 一键检测 + 快捷修复
"""

import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QProgressBar, QGroupBox, QHeaderView, QMessageBox,
    QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QColor, QFont, QDesktopServices

from services.checker_service import CheckerService, CheckItem, CheckStatus


class CheckWorker(QThread):
    """后台检测工作线程"""
    item_checked = pyqtSignal(object)
    completed = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, checker_service):
        super().__init__()
        self.checker = checker_service
        
    def run(self):
        """执行检测"""
        checks = [
            ("软件安装环境", self.checker.check_vision_plus_installation),
            ("相机驱动", self.checker.check_camera_drivers),
            ("防火墙状态", self.checker.check_firewall),
            ("网卡休眠设置", self.checker.check_network_adapter_power_management),
            ("Windows更新", self.checker.check_windows_update),
            ("网卡巨型帧", self.checker.check_jumbo_frame),
            ("网卡缓冲区", self.checker.check_network_buffer),
        ]
        
        total = len(checks)
        for i, (name, check_func) in enumerate(checks):
            self.msleep(300)
            try:
                item = check_func()
                item.index = i + 1
                self.item_checked.emit(item)
            except Exception as e:
                error_item = CheckItem(
                    title=name,
                    description=f"检测出错: {str(e)}",
                    status=CheckStatus.ERROR,
                    index=i+1
                )
                self.item_checked.emit(error_item)
            self.progress.emit(int((i + 1) / total * 100))
        
        self.msleep(200)
        self.completed.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Env Checker - 视觉环境检测工具 v2.0")
        self.setGeometry(100, 100, 1100, 800)
        
        self.checker_service = CheckerService()
        self.check_worker = None
        self.current_check_item = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题区域
        title_label = QLabel("🔧 工业视觉运行环境检测工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        subtitle = QLabel("一键检测软件环境、驱动、网卡设置 | 支持快捷修复")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        main_layout.addWidget(subtitle)
        
        # 主按钮区域
        btn_layout = QHBoxLayout()
        
        self.check_btn = QPushButton("🔍 一键检测")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 40px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.check_btn.clicked.connect(self.start_check)
        btn_layout.addWidget(self.check_btn)
        
        self.fix_btn = QPushButton("🔧 一键修复")
        self.fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 40px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #229954; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.fix_btn.setEnabled(False)
        self.fix_btn.clicked.connect(self.quick_fix)
        btn_layout.addWidget(self.fix_btn)
        
        self.open_settings_btn = QPushButton("⚙️ 打开设置")
        self.open_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 40px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #d35400; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.open_settings_btn.setEnabled(False)
        self.open_settings_btn.clicked.connect(self.open_current_settings)
        btn_layout.addWidget(self.open_settings_btn)
        
        main_layout.addLayout(btn_layout)
        
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
                height: 30px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 分割器（检测结果 + 详情）
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 检测结果表格
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["序号", "检测项", "状态", "描述", "操作"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.result_table.setColumnWidth(0, 50)
        self.result_table.setColumnWidth(2, 80)
        self.result_table.setColumnWidth(4, 100)
        self.result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.result_table.itemSelectionChanged.connect(self.on_item_selected)
        self.result_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #2c3e50;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        result_layout.addWidget(self.result_table)
        splitter.addWidget(result_group)
        
        # 详情区域
        detail_group = QGroupBox("详细信息和修复建议")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 10px;
                font-size: 12px;
                line-height: 1.6;
            }
        """)
        self.detail_text.setText("点击「一键检测」开始检查环境...\n\n"
            "检测项包括：\n"
            "• 软件安装环境（VisionPlus等）\n"
            "• 相机驱动（Basler/海康/大华等）\n"
            "• 防火墙状态\n"
            "• 网卡休眠设置\n"
            "• Windows更新设置\n"
            "• 网卡巨型帧设置\n"
            "• 网卡缓冲区设置\n\n"
            "检测到问题后，可以使用「打开设置」快速跳转到系统设置界面。")
        detail_layout.addWidget(self.detail_text)
        splitter.addWidget(detail_group)
        
        splitter.setSizes([400, 200])
        main_layout.addWidget(splitter)
        
        # 底部状态栏
        self.status_label = QLabel("就绪 - 点击「一键检测」开始检查")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px; font-size: 11px;")
        main_layout.addWidget(self.status_label)
        
    def start_check(self):
        """开始检测"""
        self.result_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.check_btn.setEnabled(False)
        self.fix_btn.setEnabled(False)
        self.open_settings_btn.setEnabled(False)
        self.status_label.setText("🔍 正在检测中...")
        self.status_label.setStyleSheet("color: #3498db; padding: 5px;")
        self.detail_text.setText("检测进行中，请稍候...")
        
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
        self.result_table.setItem(row, 0, QTableWidgetItem(str(item.index)))
        
        # 检测项
        title_item = QTableWidgetItem(item.title)
        title_item.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.result_table.setItem(row, 1, title_item)
        
        # 状态
        status_item = QTableWidgetItem(item.status.value)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if item.status == CheckStatus.SUCCESS:
            status_item.setBackground(QColor("#d4edda"))
            status_item.setForeground(QColor("#155724"))
        elif item.status == CheckStatus.WARNING:
            status_item.setBackground(QColor("#fff3cd"))
            status_item.setForeground(QColor("#856404"))
        else:
            status_item.setBackground(QColor("#f8d7da"))
            status_item.setForeground(QColor("#721c24"))
        self.result_table.setItem(row, 2, status_item)
        
        # 描述
        desc_item = QTableWidgetItem(item.description)
        desc_item.setToolTip(item.description)
        self.result_table.setItem(row, 3, desc_item)
        
        # 修复按钮
        if item.status != CheckStatus.SUCCESS and item.fix_command:
            fix_btn = QPushButton("🔧 修复")
            fix_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-size: 10px;
                    padding: 3px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover { background-color: #c0392b; }
            """)
            fix_btn.clicked.connect(lambda checked, cmd=item.fix_command: self.run_fix_command(cmd))
            self.result_table.setCellWidget(row, 4, fix_btn)
        else:
            self.result_table.setItem(row, 4, QTableWidgetItem("-"))
        
        # 存储检测项数据
        self.checker_service.results.append(item)
        self.result_table.scrollToBottom()
        
    def on_progress_update(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def on_check_completed(self):
        """检测完成"""
        self.check_btn.setEnabled(True)
        self.open_settings_btn.setEnabled(True)
        
        # 检查是否有需要修复的项
        has_issues = any(r.status != CheckStatus.SUCCESS for r in self.checker_service.results)
        self.fix_btn.setEnabled(has_issues)
        
        self.status_label.setText("✅ 检测完成！")
        self.status_label.setStyleSheet("color: #27ae60; padding: 5px;")
        
        # 生成摘要
        success = sum(1 for r in self.checker_service.results if r.status == CheckStatus.SUCCESS)
        warning = sum(1 for r in self.checker_service.results if r.status == CheckStatus.WARNING)
        error = sum(1 for r in self.checker_service.results if r.status == CheckStatus.ERROR)
        
        summary = f"""
<b>检测完成！</b><br><br>
<b>统计：</b><br>
✅ 通过: {success} 项<br>
⚠️ 警告: {warning} 项<br>
❌ 错误: {error} 项<br><br>
"""
        if has_issues:
            summary += "<b>建议：</b>点击下方表格中的项目查看详情，或使用「一键修复」自动修复。"
        else:
            summary += "<b>恭喜！</b>所有检查项均通过，环境配置正常。"
            
        self.detail_text.setHtml(summary)
        
    def on_item_selected(self):
        """当表格项被选中时"""
        selected_items = self.result_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            if row < len(self.checker_service.results):
                item = self.checker_service.results[row]
                self.current_check_item = item
                
                detail = f"""
<b>检测项：</b>{item.title}<br>
<b>状态：</b>{item.status.value}<br>
<b>描述：</b>{item.description}<br><br>
"""
                if item.fix_suggestion:
                    detail += f"<b>修复建议：</b><br>{item.fix_suggestion}<br><br>"
                    
                if item.fix_command:
                    detail += f"<b>修复命令：</b><code>{item.fix_command}</code>"
                    self.open_settings_btn.setEnabled(True)
                else:
                    self.open_settings_btn.setEnabled(False)
                    
                self.detail_text.setHtml(detail)
                
    def open_current_settings(self):
        """打开当前选中项的设置"""
        if self.current_check_item and self.current_check_item.settings_url:
            try:
                if self.current_check_item.settings_url.startswith("http"):
                    QDesktopServices.openUrl(QUrl(self.current_check_item.settings_url))
                else:
                    # Windows 系统命令
                    subprocess.Popen(self.current_check_item.settings_url, shell=True)
                self.status_label.setText(f"已打开设置: {self.current_check_item.title}")
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开设置: {str(e)}")
                
    def quick_fix(self):
        """一键修复所有问题"""
        reply = QMessageBox.question(
            self, 
            "确认修复", 
            "将尝试自动修复所有检测到的问题。\n\n是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            fixed_count = 0
            failed_items = []
            
            for item in self.checker_service.results:
                if item.status != CheckStatus.SUCCESS and item.fix_command:
                    try:
                        result = self.run_fix_command(item.fix_command, silent=True)
                        if result:
                            fixed_count += 1
                        else:
                            failed_items.append(item.title)
                    except:
                        failed_items.append(item.title)
            
            if fixed_count > 0:
                msg = f"成功修复 {fixed_count} 个问题！"
                if failed_items:
                    msg += f"\n\n以下项目需要手动修复：\n" + "\n".join(failed_items)
                QMessageBox.information(self, "修复完成", msg)
                # 重新检测
                self.start_check()
            else:
                QMessageBox.information(
                    self, 
                    "修复提示", 
                    "没有可以自动修复的项目，或修复失败。\n\n"
                    "请手动点击表格中的「修复」按钮逐个处理。"
                )
                
    def run_fix_command(self, command: str, silent: bool = False) -> bool:
        """运行修复命令"""
        try:
            if command.startswith("control ") or command.startswith("ms-settings:"):
                # Windows 系统设置
                subprocess.Popen(command, shell=True)
                if not silent:
                    QMessageBox.information(self, "已打开", "系统设置界面已打开，请手动调整。")
                return True
            else:
                # 其他命令
                result = subprocess.run(command, shell=True, capture=True, text=True)
                return result.returncode == 0
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "修复失败", f"无法执行修复: {str(e)}")
            return False


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
