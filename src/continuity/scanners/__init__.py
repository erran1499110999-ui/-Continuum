"""只读扫描器：文件类型识别与目录扫描。"""

from .filetype import identify_file
from .scan import ScanError, ScanFile, ScanReport, scan_directory

__all__ = ["identify_file", "ScanError", "ScanFile", "ScanReport", "scan_directory"]
