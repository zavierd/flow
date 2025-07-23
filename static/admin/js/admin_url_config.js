/**
 * Admin URL 配置模块
 * 统一处理所有AJAX请求的URL构建，解决localhost和127.0.0.1:8000访问差异问题
 */

(function(window) {
    'use strict';
    
    // URL配置对象
    const AdminUrlConfig = {
        // 基础配置
        config: {
            // 是否启用调试模式
            debug: true,
            // API版本
            apiVersion: 'v1'
        },
        
        /**
         * 获取基础admin路径
         * 处理不同访问方式的路径差异
         */
        getBaseAdminPath: function() {
            const currentPath = window.location.pathname;
            const currentHost = window.location.host;
            
            // 调试信息
            if (this.config.debug) {
                console.log('当前路径:', currentPath);
                console.log('当前主机:', currentHost);
            }
            
            // 情况1: 直接访问Django开发服务器 (127.0.0.1:8000)
            // 路径格式: /admin/products/sku/126/change/
            if (currentHost.includes('127.0.0.1') || currentHost.includes(':8000')) {
                return '/admin/products';
            }
            
            // 情况2: 通过Nginx代理访问 (localhost)
            // 路径格式: /admin/products/sku/126/change/
            if (currentHost.includes('localhost') && !currentHost.includes(':')) {
                // 检查是否在admin路径下
                if (currentPath.includes('/admin/products/')) {
                    return '/admin/products';
                }
                // 如果不在admin路径下，可能是其他访问方式
                return '/products';
            }
            
            // 默认情况：基于当前路径自动检测
            if (currentPath.includes('/admin/products/')) {
                return '/admin/products';
            } else if (currentPath.includes('/products/')) {
                return '/products';
            } else {
                return '/admin/products'; // 默认值
            }
        },
        
        /**
         * 构建API端点URL
         * @param {string} endpoint - API端点路径
         * @param {Object} params - URL参数对象
         * @returns {string} 完整的API URL
         */
        buildApiUrl: function(endpoint, params = {}) {
            const basePath = this.getBaseAdminPath();
            let url = `${basePath}/ajax/${endpoint}`;
            
            // 替换URL中的参数占位符
            Object.keys(params).forEach(key => {
                url = url.replace(`{${key}}`, params[key]);
            });
            
            if (this.config.debug) {
                console.log(`构建API URL: ${endpoint} -> ${url}`);
            }
            
            return url;
        },
        
        /**
         * 预定义的API端点
         */
        endpoints: {
            // SPU相关
            spuAttributes: 'spu/{spuId}/attributes/',
            
            // 属性相关
            attributeValues: 'attribute/{attributeId}/values/',
            attributeApi: 'attribute-api/',
            categoryAttributes: 'category-attributes/{categoryId}/',
            
            // 其他可能的端点
            deleteImage: 'delete-image/{imageId}/',
            uploadImage: 'upload-image/',
            
            // 验证端点
            validateSku: 'validate-sku/',
            updateStatus: 'update-status/{id}/'
        },
        
        /**
         * 获取特定端点的URL
         * @param {string} endpointName - 端点名称
         * @param {Object} params - 参数对象
         * @returns {string} 完整的URL
         */
        getEndpointUrl: function(endpointName, params = {}) {
            const endpoint = this.endpoints[endpointName];
            if (!endpoint) {
                console.error(`未知的端点: ${endpointName}`);
                return null;
            }
            
            return this.buildApiUrl(endpoint, params);
        },
        
        /**
         * 兼容性方法：保持向后兼容
         * @param {string} path - 相对路径
         * @returns {string} 完整的URL
         */
        getAdminUrl: function(path) {
            const basePath = this.getBaseAdminPath();
            const url = `${basePath}/${path}`;
            
            if (this.config.debug) {
                console.log(`兼容性URL构建: ${path} -> ${url}`);
            }
            
            return url;
        },
        
        /**
         * 执行AJAX请求的通用方法
         * @param {string} endpointName - 端点名称
         * @param {Object} params - URL参数
         * @param {Object} ajaxOptions - jQuery AJAX选项
         * @returns {Promise} jQuery Promise对象
         */
        ajax: function(endpointName, params = {}, ajaxOptions = {}) {
            const url = this.getEndpointUrl(endpointName, params);
            
            if (!url) {
                return $.Deferred().reject('无效的端点').promise();
            }
            
            const defaultOptions = {
                url: url,
                method: 'GET',
                dataType: 'json',
                timeout: 10000,
                beforeSend: function(xhr, settings) {
                    if (AdminUrlConfig.config.debug) {
                        console.log(`AJAX请求: ${settings.type} ${settings.url}`);
                    }
                },
                error: function(xhr, status, error) {
                    console.error(`AJAX请求失败: ${url}`, {
                        status: xhr.status,
                        statusText: xhr.statusText,
                        error: error
                    });
                }
            };
            
            const options = $.extend(true, defaultOptions, ajaxOptions);
            return $.ajax(options);
        },
        
        /**
         * 测试所有端点的可用性
         */
        testEndpoints: function() {
            console.log('🧪 测试API端点可用性...');
            console.log('基础路径:', this.getBaseAdminPath());
            
            Object.keys(this.endpoints).forEach(name => {
                const testParams = this.getTestParams(name);
                const url = this.getEndpointUrl(name, testParams);
                console.log(`${name}: ${url}`);
            });
        },
        
        /**
         * 获取测试参数
         */
        getTestParams: function(endpointName) {
            const testParams = {
                spuAttributes: { spuId: 1 },
                attributeValues: { attributeId: 1 },
                categoryAttributes: { categoryId: 1 },
                deleteImage: { imageId: 1 },
                updateStatus: { id: 1 }
            };
            
            return testParams[endpointName] || {};
        }
    };
    
    // 暴露到全局作用域
    window.AdminUrlConfig = AdminUrlConfig;
    
    // 在页面加载完成后初始化
    $(document).ready(function() {
        if (AdminUrlConfig.config.debug) {
            console.log('🔧 AdminUrlConfig 模块已加载');
            AdminUrlConfig.testEndpoints();
        }
    });
    
})(window); 