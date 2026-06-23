#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
病人危险行为警报模拟器
功能：模拟传感器发送病人危险行为警报到后端系统
"""

import json
import time
import random
import logging
import argparse
import threading
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 配置类 ====================

@dataclass
class SensorConfig:
    """传感器配置"""
    # 后端服务器配置
    server_url: str = "http://localhost:8080"
    api_endpoint: str = "/api/sensor/signal"
    timeout: int = 10
    retry_times: int = 3
    retry_delay: float = 2.0

    # 数据生成配置
    patient_ids: List[int] = None
    send_interval: float = 5.0  # 发送间隔（秒）
    abnormal_ratio: float = 0.3  # 异常行为比例 (0.0-1.0)
    max_concurrent: int = 3  # 最大并发实例数

    def __post_init__(self):
        if self.patient_ids is None:
            self.patient_ids = [1, 2, 3, 4, 5]


# ==================== 危险行为定义 ====================

class DangerousBehavior:
    """危险行为模式定义"""

    # 行为类型及默认严重程度映射
    BEHAVIOR_TYPES = {
        # 行为类型: (描述模板列表, 默认严重程度, 权重)
        "跌倒": (
            ["患者在病房内跌倒", "检测到患者突然倒地", "患者从床上跌落",
             "患者在卫生间跌倒", "患者在走廊跌倒"],
            3,  # 严重程度
            15  # 权重（出现概率）
        ),
        "心率异常": (
            ["患者心率超过120次/分钟", "患者心率低于50次/分钟",
             "检测到心律不齐", "心率突然升高至危险水平",
             "心率持续异常超过5分钟"],
            2,
            25
        ),
        "离床": (
            ["患者离开床位", "患者夜间离床", "患者长时间离开床位",
             "检测到患者起身"],
            1,
            30
        ),
        "长时间静止": (
            ["患者保持静止超过30分钟", "检测到患者无活动",
             "患者卧床时间异常", "患者长时间未翻身"],
            2,
            20
        ),
        "呼吸异常": (
            ["患者呼吸频率异常", "检测到呼吸暂停",
             "患者呼吸急促", "呼吸频率低于8次/分钟"],
            3,
            10
        ),
        "体温异常": (
            ["患者体温超过38.5°C", "患者体温低于35°C",
             "检测到持续发热", "体温急剧上升"],
            2,
            10
        ),
        "血压异常": (
            ["患者血压超过180/110mmHg", "患者血压低于90/60mmHg",
             "检测到血压剧烈波动"],
            2,
            15
        ),
        "紧急呼叫": (
            ["患者按下紧急呼叫按钮", "患者发出求救信号",
             "手动紧急报警触发"],
            3,
            5
        )
    }

    # 正常行为类型
    NORMAL_BEHAVIORS = [
        ("正常活动", "患者进行正常日常活动"),
        ("睡眠", "患者处于睡眠状态"),
        ("进食", "患者正在进食"),
        ("如厕", "患者前往卫生间"),
        ("活动", "患者在病房内活动")
    ]

    @classmethod
    def get_random_behavior(cls, is_abnormal: bool) -> tuple:
        """
        获取随机行为
        :param is_abnormal: 是否为异常行为
        :return: (行为类型, 描述, 严重程度)
        """
        if is_abnormal:
            # 根据权重选择异常行为类型
            behaviors = list(cls.BEHAVIOR_TYPES.items())
            types = [b[0] for b in behaviors]
            weights = [b[1][2] for b in behaviors]
            selected_type = random.choices(types, weights=weights)[0]

            descriptions, severity, _ = cls.BEHAVIOR_TYPES[selected_type]
            description = random.choice(descriptions)
            return selected_type, description, severity
        else:
            behavior, description = random.choice(cls.NORMAL_BEHAVIORS)
            return behavior, description, 0

    @classmethod
    def get_all_behavior_types(cls) -> List[str]:
        """获取所有行为类型"""
        return list(cls.BEHAVIOR_TYPES.keys())


# ==================== 日志记录器 ====================

def setup_logger(name: str = "SensorSimulator", log_file: Optional[str] = None) -> logging.Logger:
    """
    配置日志记录器
    :param name: 日志记录器名称
    :param log_file: 日志文件路径
    :return: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 清除已有的处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# ==================== 传感器数据类 ====================

@dataclass
class SensorAlert:
    """传感器警报数据"""
    patient_id: int
    behavior_type: str
    description: str
    is_abnormal: bool
    severity: int
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "patientId": self.patient_id,
            "behaviorType": self.behavior_type,
            "description": self.description,
            "isAbnormal": self.is_abnormal,
            "severity": self.severity
        }

    def to_display_string(self) -> str:
        """转换为显示字符串"""
        return (
            f"[{self.timestamp}] "
            f"病人ID: {self.patient_id} | "
            f"行为: {self.behavior_type} | "
            f"描述: {self.description} | "
            f"严重程度: {self.severity} | "
            f"状态: {'异常' if self.is_abnormal else '正常'}"
        )


# ==================== 传感器模拟器类 ====================

class SensorSimulator:
    """传感器模拟器"""

    def __init__(self, config: SensorConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or setup_logger()
        self.running = False
        self.threads: List[threading.Thread] = []
        self.stats = {
            "total_sent": 0,
            "success_count": 0,
            "failure_count": 0,
            "abnormal_count": 0,
            "normal_count": 0
        }
        self.stats_lock = threading.Lock()

    def _send_request(self, alert: SensorAlert) -> tuple:
        """
        发送HTTP请求
        :param alert: 传感器警报
        :return: (是否成功, 响应消息)
        """
        url = f"{self.config.server_url}{self.config.api_endpoint}"
        payload = alert.to_dict()

        for attempt in range(self.config.retry_times):
            try:
                self.logger.debug(f"发送请求 (尝试 {attempt + 1}/{self.config.retry_times}): {payload}")

                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.config.timeout
                )

                if response.status_code == 200:
                    return True, "成功"
                else:
                    self.logger.warning(
                        f"请求失败 - 状态码: {response.status_code}, "
                        f"响应: {response.text[:100]}"
                    )
                    return False, f"HTTP {response.status_code}"

            except requests.exceptions.Timeout:
                self.logger.warning(f"请求超时 (尝试 {attempt + 1}/{self.config.retry_times})")
                if attempt < self.config.retry_times - 1:
                    time.sleep(self.config.retry_delay)

            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"连接错误: {str(e)}")
                if attempt < self.config.retry_times - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, f"连接失败: {str(e)}"

            except requests.exceptions.RequestException as e:
                self.logger.error(f"请求异常: {str(e)}")
                return False, f"请求异常: {str(e)}"

            except Exception as e:
                self.logger.error(f"未知错误: {str(e)}")
                return False, f"未知错误: {str(e)}"

        return False, "重试次数耗尽"

    def _update_stats(self, success: bool, is_abnormal: bool):
        """更新统计信息"""
        with self.stats_lock:
            self.stats["total_sent"] += 1
            if success:
                self.stats["success_count"] += 1
            else:
                self.stats["failure_count"] += 1
            if is_abnormal:
                self.stats["abnormal_count"] += 1
            else:
                self.stats["normal_count"] += 1

    def _generate_alert(self, patient_id: Optional[int] = None) -> SensorAlert:
        """生成警报数据"""
        # 决定是否生成异常行为
        is_abnormal = random.random() < self.config.abnormal_ratio

        # 获取行为类型和描述
        behavior_type, description, severity = DangerousBehavior.get_random_behavior(is_abnormal)

        # 如果指定了病人ID则使用，否则随机选择
        pid = patient_id if patient_id else random.choice(self.config.patient_ids)

        return SensorAlert(
            patient_id=pid,
            behavior_type=behavior_type,
            description=description,
            is_abnormal=is_abnormal,
            severity=severity
        )

    def simulate_single(self, patient_id: Optional[int] = None) -> bool:
        """
        执行单次模拟
        :param patient_id: 指定的病人ID
        :return: 是否成功
        """
        alert = self._generate_alert(patient_id)

        self.logger.info(alert.to_display_string())

        success, message = self._send_request(alert)
        self._update_stats(success, alert.is_abnormal)

        if not success:
            self.logger.error(f"发送失败: {message}")

        return success

    def simulate_continuous(self, duration: Optional[int] = None):
        """
        连续模拟
        :param duration: 持续时间（秒），None表示无限
        """
        self.running = True
        start_time = time.time()
        patient_index = 0

        self.logger.info(f"开始连续模拟 - 间隔: {self.config.send_interval}秒")

        while self.running:
            # 循环选择病人ID
            patient_id = self.config.patient_ids[patient_index % len(self.config.patient_ids)]
            patient_index += 1

            self.simulate_single(patient_id)

            # 检查是否达到指定时长
            if duration and (time.time() - start_time) >= duration:
                self.stop()
                break

            # 等待下次发送
            time.sleep(self.config.send_interval)

        self._print_stats()

    def simulate_multi_instance(self, num_instances: int, alerts_per_instance: int):
        """
        多实例模拟
        :param num_instances: 实例数量
        :param alerts_per_instance: 每个实例发送的警报数量
        """
        self.logger.info(f"启动 {num_instances} 个并发实例，每个发送 {alerts_per_instance} 条警报")

        with ThreadPoolExecutor(max_workers=num_instances) as executor:
            futures = []

            for i in range(num_instances):
                # 为每个实例分配病人ID
                patient_id = self.config.patient_ids[i % len(self.config.patient_ids)]

                future = executor.submit(self._simulate_batch, patient_id, alerts_per_instance)
                futures.append(future)

            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"实例执行出错: {str(e)}")

        self._print_stats()

    def _simulate_batch(self, patient_id: int, count: int):
        """批量模拟（供多线程调用）"""
        for _ in range(count):
            if not self.running:
                break
            self.simulate_single(patient_id)
            time.sleep(random.uniform(0.5, 2.0))  # 随机间隔

    def simulate_burst(self, count: int, patient_id: Optional[int] = None):
        """
        突发模拟（短时间内发送多条警报）
        :param count: 发送数量
        :param patient_id: 指定的病人ID
        """
        self.logger.info(f"启动突发模式 - 发送 {count} 条警报")

        for i in range(count):
            self.simulate_single(patient_id)
            # 突发模式下间隔较短
            time.sleep(random.uniform(0.1, 0.5))

        self._print_stats()

    def stop(self):
        """停止模拟"""
        self.running = False
        self.logger.info("停止模拟")

    def _print_stats(self):
        """打印统计信息"""
        self.logger.info("=" * 50)
        self.logger.info("统计信息:")
        self.logger.info(f"  总发送数: {self.stats['total_sent']}")
        self.logger.info(f"  成功数: {self.stats['success_count']}")
        self.logger.info(f"  失败数: {self.stats['failure_count']}")
        self.logger.info(f"  异常警报: {self.stats['abnormal_count']}")
        self.logger.info(f"  正常警报: {self.stats['normal_count']}")
        self.logger.info("=" * 50)


# ==================== 主程序入口 ====================

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="病人危险行为警报模拟器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 单次发送警报
  python sensor_simulator.py --single

  # 连续模拟（间隔5秒）
  python sensor_simulator.py --continuous --interval 5

  # 多实例并发模拟
  python sensor_simulator.py --multi --instances 3 --alerts-per-instance 10

  # 突发模式（发送20条警报）
  python sensor_simulator.py --burst --count 20 --patient-id 1

  # 指定后端服务器地址
  python sensor_simulator.py --continuous --server http://192.168.1.100:8080

  # 指定病人ID列表
  python sensor_simulator.py --continuous --patient-ids 1,2,3,4,5

  # 调整异常行为比例（30%%异常）
  python sensor_simulator.py --continuous --abnormal-ratio 0.3
        """
    )

    # 模式选择
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--single", action="store_true", help="单次发送模式")
    mode_group.add_argument("--continuous", action="store_true", help="连续模拟模式")
    mode_group.add_argument("--multi", action="store_true", help="多实例并发模式")
    mode_group.add_argument("--burst", action="store_true", help="突发模式")

    # 服务器配置
    parser.add_argument("--server", type=str, default="http://localhost:8080",
                        help="后端服务器地址 (默认: http://localhost:8080)")
    parser.add_argument("--timeout", type=int, default=10,
                        help="请求超时时间（秒）(默认: 10)")

    # 数据生成配置
    parser.add_argument("--patient-ids", type=str, default="1,2,3,4,5",
                        help="病人ID列表，逗号分隔 (默认: 1,2,3,4,5)")
    parser.add_argument("--patient-id", type=int, default=None,
                        help="指定单个病人ID（用于单次/突发模式）")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="发送间隔（秒）(默认: 5.0)")
    parser.add_argument("--abnormal-ratio", type=float, default=0.3,
                        help="异常行为比例 0.0-1.0 (默认: 0.3)")
    parser.add_argument("--duration", type=int, default=None,
                        help="连续模式持续时间（秒），不指定则无限运行")

    # 多实例配置
    parser.add_argument("--instances", type=int, default=3,
                        help="并发实例数量 (默认: 3)")
    parser.add_argument("--alerts-per-instance", type=int, default=10,
                        help="每个实例发送的警报数量 (默认: 10)")

    # 突发模式配置
    parser.add_argument("--count", type=int, default=20,
                        help="突发模式发送数量 (默认: 20)")

    # 日志配置
    parser.add_argument("--log-file", type=str, default=None,
                        help="日志文件路径 (默认: 不写入文件)")
    parser.add_argument("--verbose", action="store_true",
                        help="显示详细调试信息")

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()

    # 解析病人ID列表
    patient_ids = [int(pid.strip()) for pid in args.patient_ids.split(",")]

    # 创建配置
    config = SensorConfig(
        server_url=args.server,
        patient_ids=patient_ids,
        send_interval=args.interval,
        abnormal_ratio=args.abnormal_ratio,
        timeout=args.timeout,
        max_concurrent=args.instances
    )

    # 配置日志
    logger = setup_logger(log_file=args.log_file)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # 创建模拟器
    simulator = SensorSimulator(config, logger)

    # 打印配置信息
    logger.info("=" * 50)
    logger.info("病人危险行为警报模拟器")
    logger.info("=" * 50)
    logger.info(f"服务器地址: {config.server_url}{config.api_endpoint}")
    logger.info(f"病人ID列表: {patient_ids}")
    logger.info(f"异常行为比例: {config.abnormal_ratio * 100:.1f}%")
    logger.info(f"请求超时: {config.timeout}秒")
    logger.info("=" * 50)

    try:
        if args.single:
            # 单次模式
            simulator.simulate_single(args.patient_id)

        elif args.continuous:
            # 连续模式
            try:
                simulator.simulate_continuous(args.duration)
            except KeyboardInterrupt:
                simulator.stop()

        elif args.multi:
            # 多实例模式
            simulator.simulate_multi_instance(args.instances, args.alerts_per_instance)

        elif args.burst:
            # 突发模式
            simulator.simulate_burst(args.count, args.patient_id)

    except KeyboardInterrupt:
        logger.info("用户中断执行")
        simulator.stop()
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
