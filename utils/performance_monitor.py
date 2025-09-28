"""
性能監控工具 - 監控系統資源使用情況
"""
import psutil
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """系統性能監控類"""
    
    def __init__(self):
        """初始化性能監控器"""
        self.start_time = time.time()
        self.baseline_memory = psutil.virtual_memory().used
        self.baseline_cpu = psutil.cpu_percent()
        
    def get_system_stats(self) -> Dict[str, Any]:
        """獲取系統統計信息"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # 內存使用情況
            memory = psutil.virtual_memory()
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            memory_percent = memory.percent
            
            # 磁盤使用情況
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            disk_percent = (disk.used / disk.total) * 100
            
            # 網絡統計
            network = psutil.net_io_counters()
            
            stats = {
                'timestamp': time.time(),
                'uptime': time.time() - self.start_time,
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'used_mb': round(memory_used_mb, 2),
                    'total_mb': round(memory_total_mb, 2),
                    'percent': memory_percent,
                    'available_mb': round(memory.available / (1024 * 1024), 2)
                },
                'disk': {
                    'used_gb': round(disk_used_gb, 2),
                    'total_gb': round(disk_total_gb, 2),
                    'percent': round(disk_percent, 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"獲取系統統計信息失敗: {e}")
            return {}
    
    def get_process_stats(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """獲取進程統計信息"""
        try:
            if pid is None:
                import os
                pid = os.getpid()
            
            process = psutil.Process(pid)
            
            # 進程信息
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            # 線程信息
            threads = process.num_threads()
            
            # 文件描述符
            try:
                open_files = len(process.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                open_files = 0
            
            stats = {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': cpu_percent,
                'memory': {
                    'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                    'vms_mb': round(memory_info.vms / (1024 * 1024), 2),
                    'percent': process.memory_percent()
                },
                'threads': threads,
                'open_files': open_files,
                'create_time': process.create_time()
            }
            
            return stats
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"獲取進程統計信息失敗: {e}")
            return {}
    
    def check_gpu_usage(self) -> Dict[str, Any]:
        """檢查GPU使用情況（如果可用）"""
        gpu_stats = {
            'available': False,
            'usage': 0,
            'memory_used': 0,
            'memory_total': 0,
            'temperature': 0
        }
        
        try:
            # 嘗試使用 nvidia-ml-py
            import pynvml
            pynvml.nvmlInit()
            
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # GPU 使用率
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_stats['usage'] = utilization.gpu
                
                # 內存使用情況
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_stats['memory_used'] = memory_info.used // (1024 * 1024)  # MB
                gpu_stats['memory_total'] = memory_info.total // (1024 * 1024)  # MB
                
                # 溫度
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    gpu_stats['temperature'] = temperature
                except:
                    pass
                
                gpu_stats['available'] = True
                
        except ImportError:
            logger.info("pynvml 未安裝，無法監控GPU")
        except Exception as e:
            logger.warning(f"GPU 監控失敗: {e}")
        
        return gpu_stats
    
    def log_performance_summary(self):
        """記錄性能摘要"""
        try:
            system_stats = self.get_system_stats()
            process_stats = self.get_process_stats()
            gpu_stats = self.check_gpu_usage()
            
            logger.info("=== 性能監控摘要 ===")
            logger.info(f"CPU 使用率: {system_stats.get('cpu', {}).get('percent', 0):.1f}%")
            logger.info(f"內存使用率: {system_stats.get('memory', {}).get('percent', 0):.1f}%")
            logger.info(f"進程內存: {process_stats.get('memory', {}).get('rss_mb', 0):.1f} MB")
            logger.info(f"進程線程數: {process_stats.get('threads', 0)}")
            
            if gpu_stats['available']:
                logger.info(f"GPU 使用率: {gpu_stats['usage']}%")
                logger.info(f"GPU 內存: {gpu_stats['memory_used']}/{gpu_stats['memory_total']} MB")
                logger.info(f"GPU 溫度: {gpu_stats['temperature']}°C")
            else:
                logger.info("GPU: 不可用或未檢測到")
            
            logger.info("==================")
            
        except Exception as e:
            logger.error(f"記錄性能摘要失敗: {e}")
    
    def get_optimization_suggestions(self) -> list:
        """獲取性能優化建議"""
        suggestions = []
        
        try:
            system_stats = self.get_system_stats()
            process_stats = self.get_process_stats()
            gpu_stats = self.check_gpu_usage()
            
            # CPU 優化建議
            cpu_percent = system_stats.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                suggestions.append("CPU 使用率過高，建議減少並發處理或優化算法")
            
            # 內存優化建議
            memory_percent = system_stats.get('memory', {}).get('percent', 0)
            if memory_percent > 85:
                suggestions.append("內存使用率過高，建議清理緩存或減少內存占用")
            
            process_memory = process_stats.get('memory', {}).get('rss_mb', 0)
            if process_memory > 500:
                suggestions.append("進程內存占用較高，建議檢查內存洩漏")
            
            # GPU 優化建議
            if gpu_stats['available']:
                gpu_usage = gpu_stats['usage']
                if gpu_usage > 90:
                    suggestions.append("GPU 使用率過高，建議優化GPU計算或減少並發")
                elif gpu_usage < 10 and gpu_stats['memory_used'] > 100:
                    suggestions.append("GPU 內存占用但使用率低，可能存在內存洩漏")
            
            # 線程優化建議
            threads = process_stats.get('threads', 0)
            if threads > 50:
                suggestions.append("線程數過多，建議使用線程池或異步處理")
            
            if not suggestions:
                suggestions.append("系統性能良好，無需特別優化")
            
        except Exception as e:
            logger.error(f"生成優化建議失敗: {e}")
            suggestions.append("無法生成優化建議，請檢查系統狀態")
        
        return suggestions

# 全局性能監控實例
performance_monitor = PerformanceMonitor()