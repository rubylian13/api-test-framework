"""
Logger 設定
提供結構化 log，方便 debug 失敗的 request
"""
import logging
import sys


def setup_logger(level: str = "INFO") -> None:
    fmt = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # 壓低 urllib3 的 debug log
    logging.getLogger("urllib3").setLevel(logging.WARNING)
