/* Brand Admin JavaScript */

// 删除Logo功能
function deleteLogo(brandId) {
    if (!confirm('确定要删除这个Logo吗？此操作不可恢复。')) {
        return;
    }
    
    // 显示加载状态
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '删除中...';
    button.disabled = true;
    
    // 发送AJAX请求
    fetch(`/admin/products/brand/delete-logo/${brandId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 显示成功消息
            showMessage('Logo删除成功！', 'success');
            
            // 刷新页面以显示更新后的状态
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showMessage(data.message || 'Logo删除失败', 'error');
            // 恢复按钮状态
            button.textContent = originalText;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('网络错误，请重试', 'error');
        // 恢复按钮状态
        button.textContent = originalText;
        button.disabled = false;
    });
}

// 显示消息
function showMessage(message, type) {
    // 移除现有消息
    const existingMessage = document.querySelector('.logo-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 创建新消息
    const messageDiv = document.createElement('div');
    messageDiv.className = `logo-message ${type}`;
    messageDiv.textContent = message;
    
    // 插入到Logo预览容器后面
    const previewContainer = document.querySelector('.logo-preview-container');
    if (previewContainer) {
        previewContainer.parentNode.insertBefore(messageDiv, previewContainer.nextSibling);
    } else {
        // 如果没有预览容器，插入到Logo字段后面
        const logoField = document.querySelector('.field-get_logo_preview');
        if (logoField) {
            logoField.appendChild(messageDiv);
        }
    }
    
    // 5秒后自动移除消息
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 文件上传预览功能
document.addEventListener('DOMContentLoaded', function() {
    const logoInput = document.querySelector('input[name="logo"]');
    
    if (logoInput) {
        logoInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // 验证文件类型
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!allowedTypes.includes(file.type)) {
                    showMessage('请选择JPG、PNG或GIF格式的图片文件', 'error');
                    this.value = '';
                    return;
                }
                
                // 验证文件大小（限制为5MB）
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    showMessage('文件大小不能超过5MB', 'error');
                    this.value = '';
                    return;
                }
                
                // 创建预览
                const reader = new FileReader();
                reader.onload = function(e) {
                    // 移除现有预览
                    const existingPreview = document.querySelector('.temp-logo-preview');
                    if (existingPreview) {
                        existingPreview.remove();
                    }
                    
                    // 创建新预览
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'temp-logo-preview';
                    previewDiv.innerHTML = `
                        <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; border: 1px solid #b3d9ff; margin: 10px 0;">
                            <p style="margin: 0 0 10px 0; color: #0066cc; font-weight: bold;">新Logo预览：</p>
                            <img src="${e.target.result}" style="max-width: 150px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px; object-fit: cover;" />
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                                文件名: ${file.name}<br>
                                大小: ${formatFileSize(file.size)}
                            </p>
                        </div>
                    `;
                    
                    // 插入预览
                    logoInput.parentNode.appendChild(previewDiv);
                    
                    showMessage('Logo已选择，请保存以完成上传', 'success');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' B';
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(1) + ' KB';
    } else {
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
}

// 表单提交时的额外验证
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            const nameField = document.querySelector('input[name="name"]');
            const codeField = document.querySelector('input[name="code"]');
            
            // 验证品牌名称
            if (nameField && nameField.value.trim().length < 2) {
                showMessage('品牌名称至少需要2个字符', 'error');
                nameField.focus();
                event.preventDefault();
                return false;
            }
            
            // 验证品牌编码
            if (codeField && !/^[A-Za-z0-9_-]+$/.test(codeField.value)) {
                showMessage('品牌编码只能包含字母、数字、下划线和短横线', 'error');
                codeField.focus();
                event.preventDefault();
                return false;
            }
            
            return true;
        });
    }
}); 