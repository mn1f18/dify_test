import os
from config import MAX_FILE_SIZE

def check_file_size(file_path):
    """检查文件大小是否符合限制"""
    size_in_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_in_mb <= MAX_FILE_SIZE

def get_file_type(file_path):
    """获取文件类型"""
    extension = os.path.splitext(file_path)[1].upper().replace('.', '')
    return extension 