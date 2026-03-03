"""
环境检测服务模块
基于原有 C# EnvironmentCheckerService 重构
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


class CheckerService:
    """环境检测服务"""
    
    def __init__(self):
        self.results: List[CheckItem] = []
        
    def check_vision_plus_installation(self) -> CheckItem:
        """检查 VisionPlus 软件是否安装"""
        is_installed = False
        
        # 检查进程
        try:
            for proc in psutil.process_iter(['name']):
                if 'VisionPlus' in proc.info['name'] or 'visionplus' in proc.info['name'].lower():
                    is_installed = True
                    break
        except:
            pass
        
        # 检查常见安装路径
        if not is_installed:
            possible_paths = [
                r"C:\Program Files\VisionPlus",
                r"C:\Program Files (x86)\VisionPlus",
                r"C:\VisionPlus",
                "/opt/visionplus",
                "/usr/local/visionplus",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    is_installed = True
                    break
        
        return CheckItem(
            title="VisionPlus软件安装检查",
            description="VisionPlus软件已正确安装" if is_installed else "未检测到VisionPlus软件",
            status=CheckStatus.SUCCESS if is_installed else CheckStatus.ERROR
        )
    
    def check_system_requirements(self) -> CheckItem:
        """检查系统配置要求"""
        meets_requirements = True
        issues = []
        
        try:
            # 检查内存（至少4GB）
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024 ** 3)
            if total_gb < 4:
                meets_requirements = False
                issues.append(f"内存不足: {total_gb:.1f}GB (需要≥4GB)")
            
            # 检查磁盘空间（至少10GB可用）
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024 ** 3)
            if free_gb < 10:
                meets_requirements = False
                issues.append(f"磁盘空间不足: {free_gb:.1f}GB可用 (需要≥10GB)")
            
            # 检查CPU核心数
            cpu_count = psutil.cpu_count(logical=False)
            if cpu_count < 2:
                meets_requirements = False
                issues.append(f"CPU核心数不足: {cpu_count}核 (建议≥4核)")
                
        except Exception as e:
            return CheckItem(
                title="系统配置要求检查",
                description=f"无法检测系统配置: {str(e)}",
                status=CheckStatus.ERROR
            )
        
        if meets_requirements:
            description = f"✓ 内存: {total_gb:.1f}GB | ✓ 磁盘: {free_gb:.1f}GB可用 | ✓ CPU: {cpu_count}核"
            status = CheckStatus.SUCCESS
        else:
            description = "; ".join(issues)
            status = CheckStatus.WARNING
            
        return CheckItem(
            title="系统配置要求检查",
            description=description,
            status=status
        )
    
    def check_network_ip_config(self) -> CheckItem:
        """检查网卡IP配置"""
        has_conflict = False
        ip_addresses = []
        
        try:
            # 获取所有网络接口
            interfaces = psutil.net_if_addrs()
            for interface_name, addrs in interfaces.items():
                for addr in addrs:
                    # 只检查 IPv4 地址
                    if addr.family == 2:  # AF_INET
                        ip_addresses.append(addr.address)
            
            # 检查是否有重复IP（简化检查，实际IP冲突需要更复杂的检测）
            if len(ip_addresses) != len(set(ip_addresses)):
                has_conflict = True
                
        except Exception as e:
            return CheckItem(
                title="网卡IP配置检查",
                description=f"检测失败: {str(e)}",
                status=CheckStatus.ERROR
            )
        
        return CheckItem(
            title="网卡IP配置检查",
            description=f"IP配置正常，发现 {len(ip_addresses)} 个网络接口" if not has_conflict else "检测到IP地址可能冲突",
            status=CheckStatus.ERROR if has_conflict else CheckStatus.SUCCESS
        )
    
    def check_network_driver(self) -> CheckItem:
        """检查网卡驱动"""
        all_drivers_ok = True
        up_count = 0
        total_count = 0
        
        try:
            # 获取网络接口统计
            interfaces = psutil.net_if_stats()
            for name, stats in interfaces.items():
                # 排除回环接口
                if 'lo' not in name.lower() and 'loopback' not in name.lower():
                    total_count += 1
                    if stats.isup:
                        up_count += 1
            
            if total_count == 0:
                all_drivers_ok = False
            elif up_count < total_count:
                all_drivers_ok = False
                
        except Exception as e:
            return CheckItem(
                title="网卡驱动检查",
                description=f"检测失败: {str(e)}",
                status=CheckStatus.ERROR
            )
        
        return CheckItem(
            title="网卡驱动检查",
            description=f"网卡驱动正常 ({up_count}/{total_count} 个接口在线)" if all_drivers_ok else f"部分网卡异常 ({up_count}/{total_count} 个接口在线)",
            status=CheckStatus.SUCCESS if all_drivers_ok else CheckStatus.WARNING
        )
    
    def check_network_parameters(self) -> CheckItem:
        """检查网卡参数配置"""
        needs_adjustment = False
        issues = []
        
        try:
            # 检查 MTU 设置
            interfaces = psutil.net_if_stats()
            for name, stats in interfaces.items():
                if 'lo' not in name.lower():
                    # 检查网卡速度
                    if hasattr(stats, 'speed') and stats.speed:
                        if stats.speed < 100:  # 小于100Mbps
                            needs_adjustment = True
                            issues.append(f"{name}: 速度较低 ({stats.speed}Mbps)")
        except:
            pass
        
        return CheckItem(
            title="网卡参数配置检查",
            description="; ".join(issues) if needs_adjustment else "网卡参数配置正常",
            status=CheckStatus.WARNING if needs_adjustment else CheckStatus.SUCCESS
        )
    
    def check_firewall(self) -> CheckItem:
        """检查防火墙状态"""
        firewall_enabled = False
        
        try:
            if platform.system() == "Windows":
                # Windows 防火墙检查
                result = subprocess.run(
                    ["netsh", "advfirewall", "show", "currentprofile"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                firewall_enabled = "State ON" in result.stdout or "状态 启用" in result.stdout
            elif platform.system() == "Linux":
                # 检查 ufw 或 firewalld
                for cmd in ["ufw", "firewalld", "iptables"]:
                    result = subprocess.run(
                        ["systemctl", "is-active", cmd],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if result.returncode == 0:
                        firewall_enabled = True
                        break
        except:
            pass
        
        return CheckItem(
            title="防火墙检查",
            description="防火墙已启用，建议关闭或配置例外" if firewall_enabled else "防火墙未启用",
            status=CheckStatus.WARNING if firewall_enabled else CheckStatus.SUCCESS
        )
    
    def check_antivirus(self) -> CheckItem:
        """检查杀毒软件"""
        antivirus_list = []
        
        try:
            if platform.system() == "Windows":
                # 检查 Windows Security Center
                result = subprocess.run(
                    ["powershell", "-Command", 
                     "Get-WmiObject -Namespace 'root\\SecurityCenter2' -Class AntiVirusProduct | Select-Object displayName"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                # 简单解析输出
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and '---' not in line and 'displayName' not in line:
                        antivirus_list.append(line.strip())
            
            # 检查常见进程
            antivirus_processes = ['360', 'avast', 'avira', 'mcafee', 'kaspersky', 
                                  'symantec', 'norton', 'trend', 'eset', 'comodo']
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                for av in antivirus_processes:
                    if av in proc_name:
                        antivirus_list.append(proc.info['name'])
                        break
                        
        except:
            pass
        
        has_antivirus = len(antivirus_list) > 0
        unique_antivirus = list(set(antivirus_list))[:3]  # 最多显示3个
        
        return CheckItem(
            title="杀毒软件检查",
            description=f"检测到: {', '.join(unique_antivirus)}" if has_antivirus else "未检测到第三方杀毒软件",
            status=CheckStatus.WARNING if has_antivirus else CheckStatus.SUCCESS
        )
    
    def check_camera_drivers(self) -> CheckItem:
        """检查相机驱动（新增）"""
        camera_types = []
        
        try:
            if platform.system() == "Windows":
                # 检查常见的相机 SDK 是否安装
                sdk_paths = [
                    (r"C:\Program Files\Basler\pylon 5", "Basler Pylon"),
                    (r"C:\Program Files\Basler\pylon 6", "Basler Pylon 6"),
                    (r"C:\Program Files\HIKVISION\MVS", "海康 MVS"),
                    (r"C:\Program Files (x86)\HIKVISION\MVS", "海康 MVS"),
                    (r"C:\Program Files\Daheng Imavision\GalaxySDK", "大华 Galaxy"),
                    (r"C:\Program Files\FLIR Systems\Spinnaker", "FLIR Spinnaker"),
                ]
                
                for path, name in sdk_paths:
                    if os.path.exists(path):
                        camera_types.append(name)
        except:
            pass
        
        has_camera_sdk = len(camera_types) > 0
        
        return CheckItem(
            title="相机驱动检查",
            description=f"已安装: {', '.join(camera_types)}" if has_camera_sdk else "未检测到相机SDK，建议安装Basler/海康/大华等驱动",
            status=CheckStatus.SUCCESS if has_camera_sdk else CheckStatus.WARNING
        )
    
    def check_cuda(self) -> CheckItem:
        """检查 CUDA 环境（新增）"""
        cuda_version = None
        
        try:
            # 尝试运行 nvcc
            result = subprocess.run(
                ["nvcc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 解析 CUDA 版本
                match = re.search(r"release (\d+\.\d+)", result.stdout)
                if match:
                    cuda_version = match.group(1)
        except:
            pass
        
        # 检查环境变量
        if not cuda_version:
            cuda_path = os.environ.get('CUDA_PATH', '')
            if cuda_path and os.path.exists(cuda_path):
                cuda_version = "已安装（版本未知）"
        
        return CheckItem(
            title="CUDA环境检查",
            description=f"CUDA {cuda_version} 已安装" if cuda_version else "未检测到CUDA，深度学习功能可能受限",
            status=CheckStatus.SUCCESS if cuda_version else CheckStatus.WARNING
        )
    
    def check_gpu(self) -> CheckItem:
        """检查 GPU（新增）"""
        gpu_info = []
        
        try:
            if platform.system() == "Windows":
                # 使用 wmic 获取 GPU 信息
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题
                for line in lines:
                    if line.strip():
                        gpu_info.append(line.strip())
            else:
                # Linux 使用 lspci
                result = subprocess.run(
                    ["lspci"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'VGA' in line or '3D controller' in line:
                        gpu_info.append(line.split(':')[-1].strip())
        except:
            pass
        
        has_gpu = len(gpu_info) > 0 and not all('Intel' in g for g in gpu_info)
        
        return CheckItem(
            title="GPU检查",
            description=f"检测到: {gpu_info[0]}" if gpu_info else "未检测到独立GPU",
            status=CheckStatus.SUCCESS if has_gpu else CheckStatus.WARNING
        )
    
    def export_report(self, file_path: str):
        """导出检测报告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("   工业视觉运行环境检测报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {platform.system()} {platform.release()}\n")
            f.write(f"平台: {platform.machine()}\n\n")
            
            f.write("-" * 60 + "\n")
            f.write("检测结果:\n")
            f.write("-" * 60 + "\n\n")
            
            for i, item in enumerate(self.results, 1):
                f.write(f"[{i}] {item.title}\n")
                f.write(f"    状态: {item.status.value}\n")
                f.write(f"    描述: {item.description}\n\n")
            
            # 统计
            success = sum(1 for r in self.results if r.status == CheckStatus.SUCCESS)
            warning = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
            error = sum(1 for r in self.results if r.status == CheckStatus.ERROR)
            
            f.write("-" * 60 + "\n")
            f.write("统计:\n")
            f.write(f"  通过: {success} 项\n")
            f.write(f"  警告: {warning} 项\n")
            f.write(f"  错误: {error} 项\n")
            f.write("=" * 60 + "\n")
