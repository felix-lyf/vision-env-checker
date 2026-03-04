"""
Vision Env Checker - 检测服务模块 V2.0
一键检测 + 快捷修复
"""

import os
import re
import psutil
import platform
import subprocess
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


class CheckStatus(Enum):
    """检测状态枚举"""
    SUCCESS = "✅ 通过"
    WARNING = "⚠️ 警告"
    ERROR = "❌ 错误"


@dataclass
class CheckItem:
    """检测项数据类"""
    title: str
    description: str
    status: CheckStatus
    index: int = 0
    fix_command: str = ""  # 修复命令
    fix_suggestion: str = ""  # 修复建议
    settings_url: str = ""  # 设置页面URL或命令


class CheckerService:
    """环境检测服务 V2.0"""
    
    def __init__(self):
        self.results: List[CheckItem] = []
        
    def check_vision_plus_installation(self) -> CheckItem:
        """检查 VisionPlus 软件是否安装"""
        is_installed = False
        install_path = ""
        
        # 检查进程
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info.get('name', '') or ''
                if 'VisionPlus' in proc_name or 'visionplus' in proc_name.lower():
                    is_installed = True
                    break
        except:
            pass
        
        # 检查常见安装路径
        if not is_installed:
            possible_paths = [
                (r"C:\Program Files\VisionPlus", "VisionPlus"),
                (r"C:\Program Files (x86)\VisionPlus", "VisionPlus"),
                (r"C:\VisionPlus", "VisionPlus"),
                (r"C:\Program Files\TEVisionPlus", "TEVisionPlus"),
                (r"C:\Program Files (x86)\TEVisionPlus", "TEVisionPlus"),
            ]
            for path, name in possible_paths:
                if os.path.exists(path):
                    is_installed = True
                    install_path = path
                    break
        
        if is_installed:
            return CheckItem(
                title="VisionPlus软件安装",
                description=f"VisionPlus已安装在: {install_path}" if install_path else "VisionPlus已正确安装",
                status=CheckStatus.SUCCESS
            )
        else:
            return CheckItem(
                title="VisionPlus软件安装",
                description="未检测到VisionPlus软件，请安装视觉检测软件",
                status=CheckStatus.ERROR,
                fix_suggestion="请联系管理员安装VisionPlus或TEVisionPlus软件",
                settings_url="explorer.exe C:\\"
            )
    
    def check_camera_drivers(self) -> CheckItem:
        """检查相机驱动是否安装"""
        camera_sdks = []
        missing_drivers = []
        
        # 检查常见相机SDK路径
        sdk_paths = [
            (r"C:\Program Files\Basler\pylon 5", "Basler Pylon 5"),
            (r"C:\Program Files\Basler\pylon 6", "Basler Pylon 6"),
            (r"C:\Program Files\Basler\pylon 7", "Basler Pylon 7"),
            (r"C:\Program Files (x86)\Basler\pylon 5", "Basler Pylon 5"),
            (r"C:\Program Files\HIKVISION\MVS", "海康 MVS"),
            (r"C:\Program Files (x86)\HIKVISION\MVS", "海康 MVS"),
            (r"C:\Program Files\Daheng Imavision\GalaxySDK", "大华 Galaxy"),
            (r"C:\Program Files (x86)\Daheng Imavision\GalaxySDK", "大华 Galaxy"),
            (r"C:\Program Files\FLIR Systems\Spinnaker", "FLIR Spinnaker"),
            (r"C:\Program Files\GenICam", "GenICam"),
        ]
        
        for path, name in sdk_paths:
            if os.path.exists(path):
                if name not in camera_sdks:
                    camera_sdks.append(name)
        
        # 检查设备管理器中的相机设备
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*camera*' -or $_.FriendlyName -like '*Basler*' -or $_.FriendlyName -like '*HIK*'} | Select-Object FriendlyName, Status"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            if "OK" in result.stdout or "正常" in result.stdout:
                pass  # 设备正常
        except:
            pass
        
        if camera_sdks:
            return CheckItem(
                title="相机驱动",
                description=f"已安装: {', '.join(camera_sdks)}",
                status=CheckStatus.SUCCESS
            )
        else:
            return CheckItem(
                title="相机驱动",
                description="未检测到相机SDK，视觉系统可能无法正常工作",
                status=CheckStatus.ERROR,
                fix_suggestion="请安装以下相机驱动之一：\n1. Basler Pylon\n2. 海康 MVS\n3. 大华 Galaxy",
                settings_url="control /name Microsoft.DeviceManager"
            )
    
    def check_firewall(self) -> CheckItem:
        """检查 Windows 防火墙是否关闭"""
        is_enabled = False
        
        try:
            # 检查 Windows 防火墙状态
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"],
                capture_output=True, text=True, timeout=5, shell=True
            )
            output = result.stdout
            
            if "State ON" in output or "状态 启用" in output or "ON" in output:
                is_enabled = True
        except:
            pass
        
        if is_enabled:
            return CheckItem(
                title="Windows防火墙",
                description="防火墙已启用，可能阻止相机通信",
                status=CheckStatus.WARNING,
                fix_suggestion="建议关闭Windows防火墙或添加相机软件例外",
                fix_command="control /name Microsoft.WindowsFirewall",
                settings_url="control /name Microsoft.WindowsFirewall"
            )
        else:
            return CheckItem(
                title="Windows防火墙",
                description="防火墙已关闭，相机通信正常",
                status=CheckStatus.SUCCESS
            )
    
    def check_network_adapter_power_management(self) -> CheckItem:
        """检查网卡电源管理（休眠设置）"""
        is_power_saving_enabled = False
        
        try:
            # 检查网卡电源管理设置
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Get-NetAdapterPowerManagement | Select-Object AllowComputerToTurnOffDevice"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            
            if "Enabled" in result.stdout or "True" in result.stdout:
                is_power_saving_enabled = True
        except:
            pass
        
        if is_power_saving_enabled:
            return CheckItem(
                title="网卡休眠设置",
                description="网卡允许计算机关闭此设备以节约电源，可能导致相机断连",
                status=CheckStatus.ERROR,
                fix_suggestion='请禁用网卡电源管理：\n1. 打开设备管理器\n2. 找到网络适配器\n3. 右键属性 -> 电源管理\n4. 取消勾选"允许计算机关闭此设备以节约电源"',
                fix_command="control /name Microsoft.DeviceManager",
                settings_url="control /name Microsoft.DeviceManager"
            )
        else:
            return CheckItem(
                title="网卡休眠设置",
                description="网卡电源管理已禁用，不会自动休眠",
                status=CheckStatus.SUCCESS
            )
    
    def check_windows_update(self) -> CheckItem:
        """检查 Windows 更新是否关闭"""
        is_update_enabled = True
        
        try:
            # 检查 Windows Update 服务状态
            result = subprocess.run(
                ["sc", "query", "wuauserv"],
                capture_output=True, text=True, timeout=5, shell=True
            )
            
            if "RUNNING" in result.stdout or "START_PENDING" in result.stdout:
                is_update_enabled = True
            elif "STOPPED" in result.stdout:
                is_update_enabled = False
        except:
            pass
        
        if is_update_enabled:
            return CheckItem(
                title="Windows自动更新",
                description="Windows自动更新已启用，可能在运行中自动重启影响生产",
                status=CheckStatus.WARNING,
                fix_suggestion="建议关闭Windows自动更新：\n1. 打开服务管理器\n2. 找到 Windows Update\n3. 设置为禁用",
                fix_command="services.msc",
                settings_url="ms-settings:windowsupdate"
            )
        else:
            return CheckItem(
                title="Windows自动更新",
                description="Windows自动更新已禁用，不会自动重启",
                status=CheckStatus.SUCCESS
            )
    
    def check_jumbo_frame(self) -> CheckItem:
        """检查网卡巨型帧(Jumbo Frame)设置"""
        jumbo_frame_status = "unknown"
        recommended_mtu = 9000
        
        try:
            # 检查网卡 MTU 设置
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-NetAdapterAdvancedProperty | Where-Object {$_.DisplayName -like '*Jumbo*' -or $_.DisplayName -like '*MTU*'} | Select-Object Name, DisplayName, DisplayValue"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            
            output = result.stdout
            if "9014" in output or "9000" in output or "Jumbo Packet" in output:
                jumbo_frame_status = "enabled"
            elif "1514" in output or "1500" in output:
                jumbo_frame_status = "disabled"
        except:
            pass
        
        if jumbo_frame_status == "enabled":
            return CheckItem(
                title="网卡巨型帧",
                description="巨型帧已启用(MTU=9000)，适合GigE相机大数据传输",
                status=CheckStatus.SUCCESS
            )
        elif jumbo_frame_status == "disabled":
            return CheckItem(
                title="网卡巨型帧",
                description="巨型帧未启用(MTU=1500)，GigE相机传输效率较低",
                status=CheckStatus.WARNING,
                fix_suggestion="建议启用巨型帧以提高GigE相机传输效率：\n1. 打开设备管理器\n2. 找到网卡 -> 属性\n3. 高级 -> Jumbo Packet\n4. 设置为 9014 或 9000",
                fix_command="control /name Microsoft.DeviceManager",
                settings_url="control /name Microsoft.DeviceManager"
            )
        else:
            return CheckItem(
                title="网卡巨型帧",
                description="无法检测巨型帧设置，请手动检查网卡高级属性",
                status=CheckStatus.WARNING,
                fix_suggestion="请手动检查网卡高级属性中的 Jumbo Packet 设置",
                settings_url="control /name Microsoft.DeviceManager"
            )
    
    def check_network_buffer(self) -> CheckItem:
        """检查网卡传输接收缓冲区设置"""
        buffer_status = "unknown"
        
        try:
            # 检查网卡缓冲区设置
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-NetAdapterAdvancedProperty | Where-Object {$_.DisplayName -like '*Buffer*' -or $_.DisplayName -like '*Receive Buffers*' -or $_.DisplayName -like '*Transmit Buffers*'} | Select-Object Name, DisplayName, DisplayValue"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            
            output = result.stdout
            # 检查缓冲区是否设置为最大值或较大值
            if output and ("512" in output or "1024" in output or "2048" in output or "Max" in output):
                buffer_status = "optimized"
            elif output:
                buffer_status = "default"
        except:
            pass
        
        if buffer_status == "optimized":
            return CheckItem(
                title="网卡缓冲区",
                description="网卡接收/传输缓冲区已优化设置",
                status=CheckStatus.SUCCESS
            )
        elif buffer_status == "default":
            return CheckItem(
                title="网卡缓冲区",
                description="网卡缓冲区使用默认设置，可能不适合高吞吐量相机",
                status=CheckStatus.WARNING,
                fix_suggestion="建议优化网卡缓冲区：\n1. 打开设备管理器\n2. 找到网卡 -> 属性\n3. 高级 -> Receive Buffers / Transmit Buffers\n4. 设置为最大值（如512或1024）",
                fix_command="control /name Microsoft.DeviceManager",
                settings_url="control /name Microsoft.DeviceManager"
            )
        else:
            return CheckItem(
                title="网卡缓冲区",
                description="无法检测缓冲区设置",
                status=CheckStatus.WARNING,
                fix_suggestion="请手动检查网卡高级属性",
                settings_url="control /name Microsoft.DeviceManager"
            )
    
    def export_report(self, file_path: str):
        """导出检测报告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("        工业视觉运行环境检测报告\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {platform.system()} {platform.release()}\n")
            f.write(f"平台: {platform.machine()}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("检测结果:\n")
            f.write("-" * 70 + "\n\n")
            
            for item in self.results:
                f.write(f"[{item.index}] {item.title}\n")
                f.write(f"    状态: {item.status.value}\n")
                f.write(f"    描述: {item.description}\n")
                if item.fix_suggestion:
                    f.write(f"    建议: {item.fix_suggestion}\n")
                f.write("\n")
            
            # 统计
            success = sum(1 for r in self.results if r.status == CheckStatus.SUCCESS)
            warning = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
            error = sum(1 for r in self.results if r.status == CheckStatus.ERROR)
            
            f.write("-" * 70 + "\n")
            f.write("统计:\n")
            f.write(f"  通过: {success} 项\n")
            f.write(f"  警告: {warning} 项\n")
            f.write(f"  错误: {error} 项\n")
            f.write("=" * 70 + "\n")
