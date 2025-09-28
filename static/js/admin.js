/**
 * 管理員頁面主 JavaScript
 * 初始化管理員界面
 */

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('管理員界面初始化中...');
    
    // 初始化管理員面板
    adminPanel = new AdminPanel();
    
    // 嘗試連接 WebSocket（將在後續任務中實現）
    // adminPanel.connectWebSocket();
    
    console.log('管理員界面初始化完成');
});

// 全局錯誤處理
window.addEventListener('error', function(event) {
    console.error('管理員界面錯誤:', event.error);
});

// 全局未處理的Promise拒絕
window.addEventListener('unhandledrejection', function(event) {
    console.error('管理員界面未處理的Promise拒絕:', event.reason);
});