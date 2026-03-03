"""
环境检测核心模块
"""

import platform
import psutil

def get_system_info():
    """获取系统基本信息"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def get_cpu_info():
    """获取CPU信息"""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": cpu_count,
        "cpu_percent": cpu_percent,
        "max_frequency": f"{cpu_freq.max:.2f} MHz" if cpu_freq else "Unknown",
    }

def get_memory_info():
    """获取内存信息"""
    svmem = psutil.virtual_memory()
    return {
        "total": f"{svmem.total / (1024**3):.2f} GB",
        "available": f"{svmem.available / (1024**3):.2f} GB",
        "percent": svmem.percent,
        "used": f"{svmem.used / (1024**3):.2f} GB",
    }

def get_disk_info():
    """获取磁盘信息"""
    partitions = psutil.disk_partitions()
    disk_info = []
    
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "total": f"{usage.total / (1024**3):.2f} GB",
                "used": f"{usage.used / (1024**3):.2f} GB",
                "free": f"{usage.free / (1024**3):.2f} GB",
                "percent": usage.percent,
            })
        except:
            pass
    
    return disk_info

if __name__ == "__main__":
    print("系统信息:", get_system_info())
    print("CPU信息:", get_cpu_info())
    print("内存信息:", get_memory_info())
    print("磁盘信息:", get_disk_info())
