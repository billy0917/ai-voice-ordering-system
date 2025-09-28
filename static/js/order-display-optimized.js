/**
 * 訂單顯示組件 - 優化版本
 * 修復訂單內容顯示不全的問題
 */
class OrderDisplayOptimized {
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
        
        // 確保內容完全可見
        this.ensureContentVisible();
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
                <div class="glass-morphism rounded-2xl p-4 mb-3" style="min-height: auto;">
                    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center space-x-3 mb-2">
                                <div class="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                                    ${item.quantity}
                                </div>
                                <h4 class="text-white font-semibold text-lg break-words leading-tight">${this.escapeHtml(item.name)}</h4>
                            </div>
                            ${this.formatCustomizations(item.customizations) ? 
                                `<div class="ml-11 text-gray-300 text-sm">
                                    <div class="flex items-start space-x-2">
                                        <i class="fas fa-cog text-xs mt-1 flex-shrink-0"></i>
                                        <span class="break-words leading-relaxed">${this.formatCustomizations(item.customizations)}</span>
                                    </div>
                                </div>` : 
                                ''
                            }
                        </div>
                        <div class="text-right flex-shrink-0 sm:ml-4">
                            <div class="text-white font-bold text-lg">$${itemTotal.toFixed(1)}</div>
                            <div class="text-gray-300 text-sm">$${item.unit_price.toFixed(1)} 每份</div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        // 顯示特殊要求
        if (order.special_requests && order.special_requests.length > 0) {
            html += `
                <div class="glass-morphism rounded-2xl p-4 mb-3 border-l-4 border-amber-400">
                    <div class="flex items-start space-x-3">
                        <div class="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-exclamation-circle text-white text-sm"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <h4 class="text-white font-semibold mb-2">特殊要求</h4>
                            <div class="text-gray-300 text-sm space-y-1">
                                ${order.special_requests.map(req => 
                                    `<div class="flex items-start space-x-2">
                                        <i class="fas fa-check text-amber-400 text-xs mt-1 flex-shrink-0"></i>
                                        <span class="break-words">${this.escapeHtml(req)}</span>
                                    </div>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 顯示總價
        html += `
            <div class="glass-card rounded-2xl p-4 border-2 border-emerald-400/30 bg-emerald-500/20 mb-3">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center">
                            <i class="fas fa-calculator text-white"></i>
                        </div>
                        <span class="text-white text-xl font-semibold">總計</span>
                    </div>
                    <span class="text-emerald-300 text-2xl font-bold">$${total.toFixed(1)}</span>
                </div>
            </div>
        `;
        
        this.orderDisplay.innerHTML = html;
        
        // 確保滾動到頂部
        this.orderDisplay.scrollTop = 0;
    }
    
    displayUpselling(suggestions) {
        if (!this.upsellingSuggestions || !suggestions.length) return;
        
        let html = '';
        
        suggestions.forEach((suggestion, index) => {
            html += `
                <div class="glass-morphism rounded-xl p-3 mb-2">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div class="flex-1 min-w-0">
                            <p class="text-white text-sm font-medium break-words leading-relaxed">${this.escapeHtml(suggestion.message)}</p>
                        </div>
                        <div class="flex items-center justify-between sm:justify-end space-x-3 flex-shrink-0">
                            <span class="text-amber-300 font-bold text-sm">+$${suggestion.price.toFixed(1)}</span>
                            <button class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-2 rounded-full transition-colors duration-200 upselling-accept" 
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
    
    ensureContentVisible() {
        // 確保訂單區域完全可見
        if (this.orderSection && !this.orderSection.classList.contains('hidden')) {
            // 移除可能導致內容被截斷的樣式
            this.orderSection.style.maxHeight = 'none';
            this.orderSection.style.height = 'auto';
            
            // 確保orderDisplay有足夠的空間
            if (this.orderDisplay) {
                this.orderDisplay.style.maxHeight = '500px'; // 增加最大高度
                this.orderDisplay.style.overflowY = 'auto';
                
                // 添加自定義滾動條樣式
                this.orderDisplay.classList.add('custom-scrollbar');
            }
            
            // 滾動到訂單區域
            setTimeout(() => {
                this.orderSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
            }, 100);
        }
    }
    
    bindUpsellEvents() {
        const acceptBtns = this.upsellingSuggestions.querySelectorAll('.upselling-accept');
        acceptBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.closest('.upselling-accept').dataset.suggestionIndex);
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
            this.showProcessing('正在確認訂單...');
            
            const response = await fetch('/api/order/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentOrder.order)
            });
            
            const result = await response.json();
            this.hideProcessing();
            
            if (result.success) {
                this.showOrderStatus(result.order);
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
            <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                <div class="glass-card rounded-3xl p-6 max-w-md w-full max-h-screen overflow-y-auto">
                    <div class="text-center mb-6">
                        <div class="w-16 h-16 bg-slate-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-cog text-white text-2xl"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-white mb-2">修改訂單</h3>
                        <p class="text-gray-300">請選擇您想要的修改方式</p>
                    </div>
                    <div class="space-y-3">
        `;
        
        options.forEach((option) => {
            html += `
                <button class="w-full flex items-center space-x-4 p-4 glass-morphism rounded-2xl hover:bg-white/20 transition-colors duration-200 modify-option-btn" 
                        data-action="${option.action}">
                    <div class="w-10 h-10 bg-slate-600 rounded-full flex items-center justify-center flex-shrink-0">
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
        
        const overlay = document.createElement('div');
        overlay.innerHTML = html;
        overlay.className = 'modify-overlay-container';
        document.body.appendChild(overlay);
        
        const buttons = overlay.querySelectorAll('.modify-option-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('.modify-option-btn').dataset.action;
                this.handleModifyAction(action);
                document.body.removeChild(overlay);
            });
        });
        
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
                break;
        }
    }
    
    restartOrder() {
        this.hideOrderSection();
        this.hideOrderStatus();
        this.currentOrder = null;
        
        if (window.voiceRecorder) {
            window.voiceRecorder.hideTranscriptionResult();
        }
        
        this.showNotification('success', '已清空訂單，請重新點餐');
    }
    
    editCurrentOrder() {
        this.showNotification('info', '編輯功能開發中，請使用重新錄音或添加項目');
    }
    
    addMoreItems() {
        this.hideOrderSection();
        
        if (window.voiceRecorder) {
            window.voiceRecorder.hideTranscriptionResult();
        }
        
        this.showNotification('info', '請繼續語音點餐，新項目將添加到現有訂單');
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
            success: 'from-emerald-500 to-emerald-600',
            error: 'from-red-500 to-red-600',
            info: 'from-slate-500 to-slate-600',
            warning: 'from-amber-500 to-amber-600'
        };
        
        notification.className = `glass-card rounded-2xl p-4 mb-3 animate-slide-up`;
        notification.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-gradient-to-r ${colors[type]} rounded-full flex items-center justify-center flex-shrink-0">
                    <i class="${icons[type]} text-white text-sm"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-white text-sm font-medium break-words">${message}</p>
                </div>
                <button class="text-white/60 hover:text-white transition-colors duration-200 flex-shrink-0" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times text-sm"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        
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

// 替換原來的OrderDisplay類
window.OrderDisplay = OrderDisplayOptimized;

// 確保向後兼容
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OrderDisplayOptimized;
}