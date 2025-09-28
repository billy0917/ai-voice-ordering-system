"""
主要路由 - 靜態頁面和基礎功能
"""
from flask import Blueprint, render_template, send_from_directory, current_app
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主頁面"""
    return send_from_directory('static', 'index.html')

@main_bp.route('/admin')
def admin():
    """管理員頁面"""
    return send_from_directory('static', 'admin.html')

@main_bp.route('/speech-test')
def speech_test():
    """語音識別測試頁面"""
    return send_from_directory('static', 'speech-test.html')

@main_bp.route('/clear-cache')
def clear_cache():
    """清除緩存說明頁面"""
    return send_from_directory('static', 'clear-cache.html')

# 靜態文件路由
@main_bp.route('/css/<path:filename>')
def css_files(filename):
    """CSS 文件路由"""
    return send_from_directory('static/css', filename)

@main_bp.route('/js/<path:filename>')
def js_files(filename):
    """JavaScript 文件路由"""
    return send_from_directory('static/js', filename)

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """其他靜態文件路由"""
    return send_from_directory('static', filename)

@main_bp.route('/health')
def health_check():
    """健康檢查端點"""
    return {
        'status': 'healthy',
        'service': '零差錯 AI 語音點餐系統',
        'version': '1.0.0'
    }

@main_bp.route('/debug/static')
def debug_static():
    """調試靜態文件配置"""
    static_files = []
    static_dir = os.path.join(current_app.root_path, 'static')
    
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), static_dir)
            static_files.append(rel_path.replace('\\', '/'))
    
    return {
        'static_folder': current_app.static_folder,
        'static_url_path': current_app.static_url_path,
        'root_path': current_app.root_path,
        'static_files': static_files
    }