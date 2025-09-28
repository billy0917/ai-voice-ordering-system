/**
 * 訂單顯示組件 - 現代化玻璃擬態設計版本
 * 處理訂單內容的顯示和交互
 */
class OrderDisplay {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentOrder = null;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        this.orderSection = document.getElementById('orderSection');
        this.orderDisplay = document.getElementById('orderDisplay');
        this.upsellingSection = document.getElementById('upsellingSection');
        this.upsellingSuggestions = document.getElementById('upsellingSuggestions');
        this.confirmBtn = document.getElementById('confirmBtn');
        this.modifyBtn = document.getElementById('modifyBtn');
        this.statusSection = document.getElementById('statusSection');
        this.orderNumber = document.getElementById('orderNumber');
        this.currentStatus = document.getElementById('currentStatus');
        this.estimatedTime = document.getElementById('estimatedTime');
    }
    
    bindEvents() {
        if (this.confirmBtn) {
            this.confirmBtn.addEventListener('click', () => {
                this.confirmOrder();
            });
        }
        
        if (this.modifyBtn) {
            this.modifyBtn.addEventListener('click', () => {
                this.modifyOrder();
            });
        }
    }
    
    async updateOrder(orderData) {
        this.currentOrder = orderData;
        
        if (!orderData || !orderData.order) {
            this.hideOrderSection();
            return;
        }
        
        // 顯示訂單內容
        this.displayOrderItems(orderData.order);
        
        // 顯示追加銷售建議
        if (orderData.upselling && orderData.upselling.suggestions.length > 0) {
            this.displayUpselling(orderData.upselling.suggestions);
        } else {
            this.hideUpselling();
        }
        
        // 顯示訂單區域
        this.showOrderSection();
    }
    
    displayOrderItems(order) {
        if (!this.orderDisplay || !order.items) return;
        
        let html = '';
        let total = 0;
        
        // 顯示每個訂單項目
        order.items.forEach((item, index) => {
            const itemTotal = item.unit_price * item.quantity;
            total += itemTotal;
            
            html += `
                <div class="glass-morphism rounded-2xl p-4 hover:bg-white/20 transition-all duration-300 animate-slide-up" style="animation-delay: ${index * 0.1}s">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="flex items-center space-x-3 mb-2">
                                <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg">
                                    ${item.quantity}
                                </div>
                                <h4 class="text-white font-semibold text-lg">${this.escapeHtml(item.name)}</h4>
                            </div>
                            ${this.formatCustomizations(item.customizations) ? 
                                `<div class="ml-11 text-blue-200 text-sm flex items-center space-x-2">
                                    <i class="fas fa-cog text-xs"></i>
                                    <span>${this.formatCustomizations(item.customizations)}</span>
                                </div>` : 
                                ''
                            }
                        </div>
                        <div class="text-right ml-4">
                            <div class="text-white font-bold text-lg">$${itemTotal.toFixed(1)}</div>
                            <div class="text-blue-200 text-sm">$${item.unit_price.toFixed(1)} 每份</div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        // 顯示特殊要求
        if (order.special_requests && order.special_requests.length > 0) {
            html += `
                <div class="glass-morphism rounded-2xl p-4 border-l-4 border-yellow-400 animate-slide-up">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center">
                            <i class="fas fa-exclamation-circle text-white text-sm"></i>
                        </div>
                        <div class="flex-1">
                            <h4 class="text-white font-semibold mb-2">特殊要求</h4>
                            <ul class="text-blue-200 text-sm space-y-1">
                                ${order.special_requests.map(req => 
                                    `<li class="flex items-center space-x-2">
                                        <i class="fas fa-check text-yellow-400 text-xs"></i>
                                        <span>${this.escapeHtml(req)}</span>
                                    </li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 顯示總價
        html += `
            <div class="glass-card rounded-2xl p-6 border-2 border-green-400/30 bg-gradient-to-r from-green-500/20 to-green-600/20 animate-slide-up">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
                            <i class="fas fa-calculator text-white"></i>
                        </div>
                        <span class="text-white text-xl font-semibold">總計</span>
                    </div>
                    <span class="text-green-300 text-2xl font-bold">$${total.toFixed(1)}</span>
                </div>
            </div>
        `;
        
        this.orderDisplay.innerHTML = html;
    }
    
    displayUpselling(suggestions) {
        if (!this.upsellingSuggestions || !suggestions.length) return;
        
        let html = '';
        
        suggestions.forEach((suggestion, index) => {
            html += `
                <div class="glass-morphism rounded-xl p-3 hover:bg-white/20 transition-all duration-300 animate-slide-up" style="animation-delay: ${index * 0.1}s">
                    <div class="flex items-center justify-between">
                        <div class="flex-1 mr-3">
                            <p class="text-white text-sm font-medium">${this.escapeHtml(suggestion.message)}</p>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="text-yellow-300 font-bold text-sm">+$${suggestion.price.toFixed(1)}</span>
                            <button class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white text-xs px-3 py-1 rounded-full transition-all duration-300 transform hover:scale-105 upselling-accept" 
                                    data-suggestion-index="${index}">
                                <i class="fas fa-plus mr-1"></i>接受
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        this.upsellingSuggestions.innerHTML = html;
        
        // 綁定追加銷售按鈕事件
        this.bindUpsellEvents();
        
        // 顯示追加銷售區域
        this.showUpselling();
    }
    
    bindUpsellEvents() {
        // 接受追加銷售
        const acceptBtns = this.upsellingSuggestions.querySelectorAll('.upselling-accept');
        acceptBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.suggestionIndex);
                this.acceptUpselling(index);
            });
        });
    }
    
    async acceptUpselling(index) {
        if (!this.currentOrder || !this.currentOrder.upselling) return;
        
        const suggestion = this.currentOrder.upselling.suggestions[index];
        if (!suggestion) return;
        
        try {
            console.log('接受追加銷售:', suggestion);
            
            // 添加到當前訂單
            if (!this.currentOrder.order.items) {
                this.currentOrder.order.items = [];
            }
            
            this.currentOrder.order.items.push({
                name: suggestion.item,
                quantity: 1,
                unit_price: suggestion.price,
                customizations: {}
            });
            
            // 移除這個建議
            this.currentOrder.upselling.suggestions.splice(index, 1);
            
            // 重新顯示訂單
            this.updateOrder(this.currentOrder);
            
            // 顯示成功通知
            this.showNotification('success', `已添加 ${suggestion.item} 到您的訂單`);
            
        } catch (error) {
            console.error('處理追加銷售失敗:', error);
            this.showNotification('error', '處理追加銷售時發生錯誤');
        }
    }
    
    async confirmOrder() {
        if (!this.currentOrder || !this.currentOrder.order) {
            this.showNotification('error', '沒有可確認的訂單');
            return;
        }
        
        try {
            // 顯示處理中狀態
            this.showProcessing('正在確認訂單...');
            
            // 發送訂單到後端
            const response = await fetch('/api/order/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentOrder.order)
            });
            
            const result = await response.json();
            
            // 隱藏處理狀態
            this.hideProcessing();
            
            if (result.success) {
                // 顯示訂單狀態
                this.showOrderStatus(result.order);
                
                // 隱藏訂單編輯區域
                this.hideOrderSection();
                
                this.showNotification('success', '訂單確認成功！');
            } else {
                this.showNotification('error', result.error || '確認訂單失敗');
            }
            
        } catch (error) {
            console.error('確認訂單失敗:', error);
            this.hideProcessing();
            this.showNotification('error', '網絡錯誤，請重試');
        }
    }
    
    modifyOrder() {
        // 顯示修改選項
        this.showModifyOptions();
    }
    
    showModifyOptions() {
        const options = [
            { text: '重新錄音點餐', action: 'restart', icon: 'fas fa-microphone' },
            { text: '編輯當前訂單', action: 'edit', icon: 'fas fa-edit' },
            { text: '添加更多項目', action: 'add', icon: 'fas fa-plus' },
            { text: '取消修改', action: 'cancel', icon: 'fas fa-times' }
        ];
        
        let html = `
            <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                <div class="glass-card rounded-3xl p-8 max-w-md mx-4 animate-slide-up">
                    <div class="text-center mb-6">
                        <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-cog text-white text-2xl"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-2">修改訂單</h3>
                        <p class="text-blue-200">請選擇您想要的修改方式</p>
                    </div>
                    <div class="space-y-3">
        `;
        
        options.forEach((option, index) => {
            html += `
                <button class="w-full flex items-center space-x-4 p-4 glass-morphism rounded-2xl hover:bg-white/20 transition-all duration-300 transform hover:scale-105 modify-option-btn animate-slide-up" 
                        data-action="${option.action}" style="animation-delay: ${index * 0.1}s">
                    <div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center">
                        <i class="${option.icon} text-white"></i>
                    </div>
                    <span class="text-white font-medium">${option.text}</span>
                </button>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        // 添加到頁面
        const overlay = document.createElement('div');
        overlay.innerHTML = html;
        overlay.className = 'modify-overlay-container';
        document.body.appendChild(overlay);
        
        // 綁定事件
        const buttons = overlay.querySelectorAll('.modify-option-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('.modify-option-btn').dataset.action;
                this.handleModifyAction(action);
                document.body.removeChild(overlay);
            });
        });
        
        // 點擊背景關閉
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay.firstElementChild) {
                document.body.removeChild(overlay);
            }
        });
    }
    
    handleModifyAction(action) {
        switch (action) {
            case 'restart':
                this.restartOrder();
                break;
            case 'edit':
                this.editCurrentOrder();
                break;
            case 'add':
                this.addMoreItems();
                break;
            case 'cancel':
                // 什麼都不做，保持當前狀態
                break;
        }
    }
    
    restartOrder() {
        // 重新開始點餐流程
        this.hideOrderSection();
        this.hideOrderStatus();
        this.currentOrder = null;
        
        // 清除轉錄結果
        if (window.voiceRecorder) {
            window.voiceRecorder.hideTranscriptionResult();
        }
        
        this.showNotification('success', '已清空訂單，請重新點餐');
    }
    
    editCurrentOrder() {
        if (!this.currentOrder || !this.currentOrder.order) return;
        
        // 顯示編輯界面
        this.showOrderEditor();
    }
    
    addMoreItems() {
        // 隱藏當前訂單顯示，但保留數據
        this.hideOrderSection();
        
        // 清除轉錄結果，準備新的語音輸入
        if (window.voiceRecorder) {
            window.voiceRecorder.hideTranscriptionResult();
        }
        
        this.showNotification('info', '請繼續語音點餐，新項目將添加到現有訂單');
    }
    
    showOrderEditor() {
        // 編輯器實現（簡化版本）
        this.showNotification('info', '編輯功能開發中，請使用重新錄音或添加項目');
    }
    
    showOrderStatus(order) {
        if (!this.statusSection) return;
        
        if (this.orderNumber) {
            this.orderNumber.textContent = order.id.substring(0, 8);
        }
        
        if (this.currentStatus) {
            this.currentStatus.textContent = this.getStatusText(order.status);
        }
        
        if (this.estimatedTime) {
            const estimatedMinutes = this.calculateEstimatedTime(order);
            this.estimatedTime.textContent = `${estimatedMinutes} 分鐘`;
        }
        
        this.statusSection.classList.remove('hidden');
    }
    
    hideOrderStatus() {
        if (this.statusSection) {
            this.statusSection.classList.add('hidden');
        }
    }
    
    showOrderSection() {
        if (this.orderSection) {
            this.orderSection.classList.remove('hidden');
        }
    }
    
    hideOrderSection() {
        if (this.orderSection) {
            this.orderSection.classList.add('hidden');
        }
    }
    
    showUpselling() {
        if (this.upsellingSection) {
            this.upsellingSection.classList.remove('hidden');
        }
    }
    
    hideUpselling() {
        if (this.upsellingSection) {
            this.upsellingSection.classList.add('hidden');
        }
    }
    
    formatCustomizations(customizations) {
        if (!customizations || Object.keys(customizations).length === 0) {
            return '';
        }
        
        return Object.entries(customizations)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');
    }
    
    getStatusText(status) {
        const statusMap = {
            'pending': '待確認',
            'confirmed': '已確認',
            'preparing': '準備中',
            'ready': '完成',
            'delivered': '已送達',
            'cancelled': '已取消'
        };
        
        return statusMap[status] || status;
    }
    
    calculateEstimatedTime(order) {
        const itemCount = order.items ? order.items.length : 0;
        return Math.max(5, itemCount * 2);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 通知系統
    showNotification(type, message) {
        const container = document.getElementById('notificationContainer');
        if (!container) return;
        
        const notification = document.createElement('div');
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle'
        };
        
        const colors = {
            success: 'from-green-500 to-green-600',
            error: 'from-red-500 to-red-600',
            info: 'from-blue-500 to-blue-600',
            warning: 'from-yellow-500 to-yellow-600'
        };
        
        notification.className = `glass-card rounded-2xl p-4 mb-3 animate-slide-up transform transition-all duration-300`;
        notification.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-gradient-to-r ${colors[type]} rounded-full flex items-center justify-center flex-shrink-0">
                    <i class="${icons[type]} text-white text-sm"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-white text-sm font-medium">${message}</p>
                </div>
                <button class="text-white/60 hover:text-white transition-colors duration-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times text-sm"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // 自動移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // 處理中狀態
    showProcessing(message) {
        const overlay = document.getElementById('processingOverlay');
        const text = document.getElementById('processingText');
        
        if (overlay) {
            overlay.classList.remove('hidden');
        }
        
        if (text) {
            text.textContent = message;
        }
    }
    
    hideProcessing() {
        const overlay = document.getElementById('processingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
}