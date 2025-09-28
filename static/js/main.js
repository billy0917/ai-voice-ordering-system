/**
 * 主應用程序 JavaScript
 * 初始化和協調各個組件
 */

// 全局變量
let voiceRecorder = null;
let orderDisplay = null;

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('零差錯 AI 語音點餐系統初始化中...');
    
    // 檢查瀏覽器支援
    if (!VoiceRecorder.isSupported()) {
        showError('您的瀏覽器不支援語音錄製功能，請使用現代瀏覽器');
        return;
    }
    
    // 初始化組件
    initializeComponents();
    
    console.log('系統初始化完成');
});

function initializeComponents() {
    // 初始化語音錄製器
    voiceRecorder = new VoiceRecorder({
        onTranscriptionReceived: handleTranscriptionReceived,
        onError: handleVoiceError,
        onRecordingStart: handleRecordingStart,
        onRecordingStop: handleRecordingStop
    });
    
    // 初始化訂單顯示器
    orderDisplay = new OrderDisplay('orderDisplay');
    
    // 將組件設為全局可訪問（用於調試）
    window.voiceRecorder = voiceRecorder;
    window.orderDisplay = orderDisplay;
}

async function handleTranscriptionReceived(transcriptionResult) {
    console.log('收到語音轉錄結果:', transcriptionResult);
    
    // 檢查轉錄信心度
    if (transcriptionResult.confidence < 0.85) {
        showWarning('語音識別信心度較低，建議重新錄音以獲得更好的效果');
    }
    
    // 如果轉錄成功，解析訂單
    if (transcriptionResult.success && transcriptionResult.transcription) {
        await parseOrder(transcriptionResult.transcription);
    }
}

async function parseOrder(transcription) {
    try {
        console.log('解析訂單:', transcription);
        
        // 顯示處理中狀態
        showProcessingStatus('正在解析您的訂單...');
        
        // 調用訂單解析API
        const response = await fetch('/api/order/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcription: transcription,
                context: 'tea_restaurant'
            })
        });
        
        const result = await response.json();
        
        // 隱藏處理狀態
        hideProcessingStatus();
        
        if (result.success) {
            // 檢查是否有現有訂單需要合併
            if (orderDisplay.currentOrder && orderDisplay.currentOrder.order) {
                // 合併新項目到現有訂單
                mergeOrderItems(result);
            } else {
                // 顯示新訂單
                orderDisplay.updateOrder(result);
            }
        } else {
            showError(result.error || result.message || '訂單解析失敗，請重試');
        }
        
    } catch (error) {
        console.error('解析訂單錯誤:', error);
        hideProcessingStatus();
        showError('網絡錯誤，請檢查連接後重試');
    }
}

function mergeOrderItems(newOrderResult) {
    if (!orderDisplay.currentOrder || !newOrderResult.order) return;
    
    // 將新項目添加到現有訂單
    const existingItems = orderDisplay.currentOrder.order.items || [];
    const newItems = newOrderResult.order.items || [];
    
    // 合併項目
    const mergedItems = [...existingItems, ...newItems];
    
    // 合併特殊要求
    const existingRequests = orderDisplay.currentOrder.order.special_requests || [];
    const newRequests = newOrderResult.order.special_requests || [];
    const mergedRequests = [...existingRequests, ...newRequests];
    
    // 更新訂單
    orderDisplay.currentOrder.order.items = mergedItems;
    orderDisplay.currentOrder.order.special_requests = mergedRequests;
    
    // 重新計算總價
    orderDisplay.currentOrder.order.total = mergedItems.reduce(
        (sum, item) => sum + (item.unit_price * item.quantity), 0
    );
    
    // 合併追加銷售建議
    if (newOrderResult.upselling && newOrderResult.upselling.suggestions) {
        if (!orderDisplay.currentOrder.upselling) {
            orderDisplay.currentOrder.upselling = { suggestions: [] };
        }
        
        // 添加新的建議，避免重複
        const existingSuggestions = orderDisplay.currentOrder.upselling.suggestions || [];
        const newSuggestions = newOrderResult.upselling.suggestions || [];
        
        newSuggestions.forEach(newSugg => {
            const exists = existingSuggestions.some(existing => 
                existing.item === newSugg.item
            );
            if (!exists) {
                existingSuggestions.push(newSugg);
            }
        });
        
        orderDisplay.currentOrder.upselling.suggestions = existingSuggestions;
    }
    
    // 重新顯示訂單
    orderDisplay.updateOrder(orderDisplay.currentOrder);
    
    // 顯示成功消息
    showSuccess(`已添加 ${newItems.length} 個新項目到您的訂單`);
}

function handleVoiceError(error) {
    console.error('語音錄製錯誤:', error);
    showError(error);
}

function handleRecordingStart() {
    console.log('開始錄音');
    // 可以在這裡添加錄音開始的UI反饋
}

function handleRecordingStop() {
    console.log('停止錄音');
    // 可以在這裡添加錄音停止的UI反饋
}

function showProcessingStatus(message) {
    if (orderDisplay && orderDisplay.showProcessing) {
        orderDisplay.showProcessing(message);
    }
}

function hideProcessingStatus() {
    if (orderDisplay && orderDisplay.hideProcessing) {
        orderDisplay.hideProcessing();
    }
}

function showError(message) {
    console.error('錯誤:', message);
    if (orderDisplay && orderDisplay.showNotification) {
        orderDisplay.showNotification('error', message);
    }
}

function showWarning(message) {
    console.warn('警告:', message);
    if (orderDisplay && orderDisplay.showNotification) {
        orderDisplay.showNotification('warning', message);
    }
}

function showSuccess(message) {
    console.log('成功:', message);
    if (orderDisplay && orderDisplay.showNotification) {
        orderDisplay.showNotification('success', message);
    }
}

// 添加一些CSS樣式到頁面
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .processing-status {
            animation: fadeIn 0.3s ease-in;
        }
        
        .processing-content {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff40;
            border-top: 2px solid #ffffff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
        
        .hidden {
            display: none !important;
        }
        
        .error-message,
        .warning-message,
        .success-message {
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    
    document.head.appendChild(style);
}

// 添加樣式
addDynamicStyles();

// 全局錯誤處理
window.addEventListener('error', function(event) {
    console.error('全局錯誤:', event.error);
    showError('系統發生錯誤，請刷新頁面重試');
});

// 全局未處理的Promise拒絕
window.addEventListener('unhandledrejection', function(event) {
    console.error('未處理的Promise拒絕:', event.reason);
    showError('系統發生錯誤，請重試');
});

// 導出一些函數供全局使用
window.showError = showError;
window.showWarning = showWarning;
window.showSuccess = showSuccess;
window.mergeOrderItems = mergeOrderItems;
window.parseOrder = parseOrder;
window.handleTranscriptionReceived = handleTranscriptionReceived;