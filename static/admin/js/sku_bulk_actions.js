/**
 * SKU批量操作增强脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    // 只在SKU列表页面执行
    if (!window.location.pathname.includes('/products/sku/')) {
        return;
    }

    initBulkActions();
    initStatusDisplay();
    initSelectionCounter();
});

function initBulkActions() {
    const actionSelect = document.querySelector('select[name="action"]');
    const goButton = document.querySelector('.actions .button');
    
    if (!actionSelect || !goButton) return;

    // 为批量操作添加确认对话框
    goButton.addEventListener('click', function(e) {
        const selectedAction = actionSelect.value;
        const selectedItems = document.querySelectorAll('input[name="_selected_action"]:checked');
        
        if (selectedItems.length === 0) {
            e.preventDefault();
            alert('请先选择要操作的SKU');
            return;
        }

        // 为特定操作添加确认对话框
        const confirmActions = {
            'bulk_set_inactive_action': '确定要将选中的SKU设置为停售状态吗？',
            'bulk_set_out_of_stock_action': '确定要将选中的SKU设置为缺货状态并清零库存吗？',
            'bulk_set_active_action': '确定要将选中的SKU设置为在售状态吗？'
        };

        if (confirmActions[selectedAction]) {
            if (!confirm(`${confirmActions[selectedAction]}\n\n选中数量：${selectedItems.length} 个SKU`)) {
                e.preventDefault();
                return;
            }
        }

        // 添加加载状态
        if (selectedAction.includes('bulk_')) {
            const actionsDiv = document.querySelector('.actions');
            actionsDiv.classList.add('loading');
            goButton.disabled = true;
            goButton.textContent = '处理中...';
        }
    });

    // 为操作选择添加描述
    addActionDescriptions();
}

function addActionDescriptions() {
    const actionSelect = document.querySelector('select[name="action"]');
    if (!actionSelect) return;

    const descriptions = {
        'bulk_update_status_action': '高级批量状态修改，支持同时更新库存和添加备注',
        'bulk_set_active_action': '快速将选中SKU设置为在售状态',
        'bulk_set_inactive_action': '快速将选中SKU设置为停售状态',
        'bulk_set_out_of_stock_action': '快速将选中SKU设置为缺货状态并清零库存',
        'sync_from_spu_action': '从关联的SPU同步属性、尺寸模板和加价规则'
    };

    // 创建描述显示元素
    const helpDiv = document.createElement('div');
    helpDiv.className = 'help';
    helpDiv.style.display = 'none';
    actionSelect.parentNode.appendChild(helpDiv);

    actionSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        if (descriptions[selectedValue]) {
            helpDiv.textContent = descriptions[selectedValue];
            helpDiv.style.display = 'block';
        } else {
            helpDiv.style.display = 'none';
        }
    });
}

function initStatusDisplay() {
    // 为状态列添加数据属性，便于CSS样式化
    const statusCells = document.querySelectorAll('.field-status');
    statusCells.forEach(cell => {
        const row = cell.closest('tr');
        const statusText = cell.textContent.trim().toLowerCase();
        
        // 状态映射
        const statusMap = {
            '在售': 'active',
            '停售': 'inactive', 
            '缺货': 'out_of_stock',
            '停产': 'discontinued',
            '预售': 'pre_order'
        };

        const statusKey = Object.keys(statusMap).find(key => 
            statusText.includes(key.toLowerCase())
        );

        if (statusKey && row) {
            row.setAttribute('data-status', statusMap[statusKey]);
        }
    });
}

function initSelectionCounter() {
    // 创建选择计数器
    const actionsDiv = document.querySelector('.actions');
    if (!actionsDiv) return;

    const counter = document.createElement('span');
    counter.className = 'selection-counter';
    counter.style.cssText = `
        margin-left: 15px;
        padding: 5px 10px;
        background: #e9ecef;
        border-radius: 3px;
        font-size: 12px;
        color: #495057;
        font-weight: 500;
    `;
    
    actionsDiv.appendChild(counter);

    // 更新计数器
    function updateCounter() {
        const selectedItems = document.querySelectorAll('input[name="_selected_action"]:checked');
        const totalItems = document.querySelectorAll('input[name="_selected_action"]');
        
        if (selectedItems.length === 0) {
            counter.textContent = `共 ${totalItems.length} 个SKU`;
            counter.style.background = '#e9ecef';
            counter.style.color = '#495057';
        } else {
            counter.textContent = `已选择 ${selectedItems.length} / ${totalItems.length} 个SKU`;
            counter.style.background = '#fff3cd';
            counter.style.color = '#856404';
        }
    }

    // 监听选择变化
    const selectAllCheckbox = document.querySelector('#action-toggle');
    const itemCheckboxes = document.querySelectorAll('input[name="_selected_action"]');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', updateCounter);
    }

    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateCounter);
    });

    // 初始化计数器
    updateCounter();
}

// 批量操作成功后的处理
function handleBulkActionSuccess(message) {
    // 显示成功消息
    showNotification(message, 'success');
    
    // 刷新页面或更新显示
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease-out;
    `;

    // 根据类型设置颜色
    const colors = {
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8'
    };

    notification.style.background = colors[type] || colors.info;
    notification.textContent = message;

    // 添加关闭按钮
    const closeBtn = document.createElement('span');
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
        float: right;
        margin-left: 15px;
        cursor: pointer;
        font-size: 18px;
        line-height: 1;
    `;
    closeBtn.onclick = () => notification.remove();
    notification.appendChild(closeBtn);

    document.body.appendChild(notification);

    // 自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification {
        animation: slideIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);
