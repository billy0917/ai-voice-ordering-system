/**
 * 管理員面板組件
 * 處理訂單管理和實時更新
 */
class AdminPanel {
    constructor() {
        this.orders = [];
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.initializeElements();
        this.bindEvents();
        this.loadOrders();
        this.updateTime();
        
        // 每30秒更新一次時間
        setInterval(() => this.updateTime(), 30000);
        
        // 每5秒刷新一次訂單（如果沒有WebSocket連接）
        setInterval(() => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                this.loadOrders();
            }
        }, 5000);
    }
    
    initializeElements() {
        // 統計元素
        this.todayOrdersEl = document.getElementById('todayOrders');
        this.pendingOrdersEl = document.getElementById('pendingOrders');
        this.preparingOrdersEl = document.getElementById('preparingOrders');
        this.completedOrdersEl = document.getElementById('completedOrders');
        
        // 控制元素
        this.statusFilter = document.getElementById('statusFilter');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.ordersContainer = document.getElementById('ordersContainer');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.currentTime = document.getElementById('currentTime');
    }
    
    bindEvents() {
        if (this.statusFilter) {
            this.statusFilter.addEventListener('change', () => {
                this.filterOrders();
            });
        }
        
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => {
                this.loadOrders();
            });
        }
    }
    
    async loadOrders() {
        try {
            const response = await fetch('/api/order/active');
            const result = await response.json();
            
            if (result.success) {
                this.orders = result.orders;
                this.updateStatistics();
                this.displayOrders();
            } else {
                console.error('載入訂單失敗:', result.error);
            }
            
        } catch (error) {
            console.error('載入訂單錯誤:', error);
        }
    }
    
    updateStatistics() {
        const today = new Date().toDateString();
        
        // 計算統計數據
        const todayOrders = this.orders.filter(order => 
            new Date(order.created_at).toDateString() === today
        ).length;
        
        const pendingOrders = this.orders.filter(order => 
            order.status === 'pending'
        ).length;
        
        const preparingOrders = this.orders.filter(order => 
            order.status === 'preparing'
        ).length;
        
        const completedOrders = this.orders.filter(order => 
            order.status === 'ready'
        ).length;
        
        // 更新顯示
        if (this.todayOrdersEl) this.todayOrdersEl.textContent = todayOrders;
        if (this.pendingOrdersEl) this.pendingOrdersEl.textContent = pendingOrders;
        if (this.preparingOrdersEl) this.preparingOrdersEl.textContent = preparingOrders;
        if (this.completedOrdersEl) this.completedOrdersEl.textContent = completedOrders;
    }
    
    displayOrders() {
        if (!this.ordersContainer) return;
        
        const filteredOrders = this.getFilteredOrders();
        
        if (filteredOrders.length === 0) {
            this.ordersContainer.innerHTML = `
                <div class="no-orders">
                    <p>暫無符合條件的訂單</p>
                </div>
            `;
            return;
        }
        
        // 按創建時間排序（最新的在前）
        filteredOrders.sort((a, b) => 
            new Date(b.created_at) - new Date(a.created_at)
        );
        
        const html = filteredOrders.map(order => 
            this.createOrderCard(order)
        ).join('');
        
        this.ordersContainer.innerHTML = html;
        
        // 綁定訂單卡片事件
        this.bindOrderCardEvents();
    }
    
    getFilteredOrders() {
        const filterValue = this.statusFilter ? this.statusFilter.value : 'all';
        
        if (filterValue === 'all') {
            return this.orders;
        }
        
        return this.orders.filter(order => order.status === filterValue);
    }
    
    createOrderCard(order) {
        const createdTime = new Date(order.created_at).toLocaleString('zh-HK');
        const itemsHtml = order.items.map(item => `
            <div class="order-item-admin">
                <div class="item-info">
                    <div class="item-name-admin">${this.escapeHtml(item.name)}</div>
                    <div class="item-details-admin">
                        ${this.formatCustomizations(item.customizations)}
                    </div>
                </div>
                <div class="item-quantity">x${item.quantity}</div>
                <div class="item-price-admin">$${item.total_price.toFixed(2)}</div>
            </div>
        `).join('');
        
        const specialRequestsHtml = order.special_requests && order.special_requests.length > 0 ? `
            <div class="special-requests">
                <h4>特殊要求</h4>
                <ul>
                    ${order.special_requests.map(req => 
                        `<li>${this.escapeHtml(req)}</li>`
                    ).join('')}
                </ul>
            </div>
        ` : '';
        
        const transcriptionHtml = order.transcription ? `
            <div class="transcription-info">
                <h4>語音轉錄</h4>
                <div class="transcription-text">"${this.escapeHtml(order.transcription)}"</div>
                <div class="confidence-score">信心度: ${Math.round(order.confidence_score * 100)}%</div>
            </div>
        ` : '';
        
        return `
            <div class="order-card status-${order.status}" data-order-id="${order.id}">
                <div class="order-header">
                    <div class="order-id">訂單 #${order.id.substring(0, 8)}</div>
                    <div class="order-time">${createdTime}</div>
                    <div class="order-status ${order.status}">${this.getStatusText(order.status)}</div>
                </div>
                
                ${transcriptionHtml}
                ${specialRequestsHtml}
                
                <div class="order-items">
                    ${itemsHtml}
                </div>
                
                <div class="order-total-admin">
                    總計: $${order.total_amount.toFixed(2)}
                </div>
                
                <div class="order-actions-admin">
                    ${this.createStatusButtons(order)}
                </div>
            </div>
        `;
    }
    
    createStatusButtons(order) {
        const buttons = [];
        
        switch (order.status) {
            case 'pending':
                buttons.push(`
                    <button class="btn btn-primary btn-small" 
                            onclick="adminPanel.updateOrderStatus('${order.id}', 'confirmed')">
                        確認訂單
                    </button>
                    <button class="btn btn-secondary btn-small" 
                            onclick="adminPanel.updateOrderStatus('${order.id}', 'cancelled')">
                        取消訂單
                    </button>
                `);
                break;
                
            case 'confirmed':
                buttons.push(`
                    <button class="btn btn-primary btn-small" 
                            onclick="adminPanel.updateOrderStatus('${order.id}', 'preparing')">
                        開始準備
                    </button>
                `);
                break;
                
            case 'preparing':
                buttons.push(`
                    <button class="btn btn-success btn-small" 
                            onclick="adminPanel.updateOrderStatus('${order.id}', 'ready')">
                        完成訂單
                    </button>
                `);
                break;
                
            case 'ready':
                buttons.push(`
                    <button class="btn btn-success btn-small" 
                            onclick="adminPanel.updateOrderStatus('${order.id}', 'delivered')">
                        已送達
                    </button>
                `);
                break;
        }
        
        return buttons.join('');
    }
    
    async updateOrderStatus(orderId, newStatus) {
        try {
            const response = await fetch(`/api/order/${orderId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 更新本地訂單狀態
                const order = this.orders.find(o => o.id === orderId);
                if (order) {
                    order.status = newStatus;
                    order.updated_at = new Date().toISOString();
                }
                
                // 重新顯示訂單
                this.updateStatistics();
                this.displayOrders();
                
                console.log(`訂單 ${orderId} 狀態更新為 ${newStatus}`);
            } else {
                alert(result.error || '更新訂單狀態失敗');
            }
            
        } catch (error) {
            console.error('更新訂單狀態錯誤:', error);
            alert('網絡錯誤，請重試');
        }
    }
    
    bindOrderCardEvents() {
        // 這裡可以添加其他訂單卡片相關的事件綁定
        // 例如點擊展開詳情等
    }
    
    filterOrders() {
        this.displayOrders();
    }
    
    connectWebSocket() {
        // WebSocket 連接將在後續任務中實現
        this.updateConnectionStatus('connecting');
        
        setTimeout(() => {
            this.updateConnectionStatus('disconnected');
        }, 2000);
    }
    
    updateConnectionStatus(status) {
        if (!this.connectionStatus) return;
        
        this.connectionStatus.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                this.connectionStatus.textContent = '已連接';
                break;
            case 'connecting':
                this.connectionStatus.textContent = '連接中...';
                break;
            case 'disconnected':
                this.connectionStatus.textContent = '未連接';
                break;
        }
    }
    
    updateTime() {
        if (this.currentTime) {
            const now = new Date();
            this.currentTime.textContent = now.toLocaleString('zh-HK');
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
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 全局實例
let adminPanel;