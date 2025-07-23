/**
 * SKU尺寸同步功能JavaScript
 * 实现从SPU自动继承尺寸模板的功能
 */

(function($) {
    'use strict';

    // 等待DOM加载完成
    $(document).ready(function() {
        
        // 初始化SKU尺寸同步功能
        function initSKUDimensionSync() {
            console.log('初始化SKU尺寸同步功能');
            
                         // 监听SPU字段的变化
             $(document).on('change', '#id_spu', function() {
                 const spuId = $(this).val();
                 
                 // 重置状态
                 $('.sync-dimensions-btn').hide().removeClass('btn-success').addClass('btn-info');
                 $('.sync-help').text('正在检查SPU是否有尺寸模板...');
                 window.spuDimensionTemplates = [];
                 
                 if (spuId) {
                     loadSPUDimensionTemplates(spuId);
                 } else {
                     $('.sync-help').text('请先选择SPU');
                 }
             });
            
            // 添加同步按钮
            addSyncButton();
            
            // 页面加载时检查是否需要自动同步
            const spuId = $('#id_spu').val();
            if (spuId) {
                checkAutoSync(spuId);
            }
        }
        
                 // 添加同步按钮到尺寸区域
         function addSyncButton() {
             const $dimensionGroup = $('.productsdimension_set-group');
             if ($dimensionGroup.length && !$dimensionGroup.find('.sync-dimensions-btn').length) {
                 const syncButton = `
                     <div class="sync-dimensions-container" style="margin: 10px 0;">
                         <button type="button" class="sync-dimensions-btn btn btn-info btn-sm" 
                                 style="background: #17a2b8; color: white; border: none; padding: 6px 12px; border-radius: 4px; display: none;">
                             🔄 从SPU同步尺寸模板
                         </button>
                         <span class="sync-help" style="margin-left: 10px; font-size: 12px; color: #6c757d;">
                             正在检查SPU是否有尺寸模板...
                         </span>
                     </div>
                 `;
                 
                 $dimensionGroup.find('h2').after(syncButton);
                 
                 // 绑定同步按钮事件
                 $('.sync-dimensions-btn').on('click', function() {
                     const spuId = $('#id_spu').val();
                     if (spuId) {
                         syncDimensionsFromSPU(spuId);
                     } else {
                         alert('请先选择SPU后再同步尺寸模板');
                     }
                 });
             }
         }
        
                 // 检查是否需要自动同步
         function checkAutoSync(spuId) {
             // 先加载SPU的尺寸模板，只有在SPU有尺寸模板时才考虑同步
             loadSPUDimensionTemplates(spuId);
         }
         
         // 检查是否要提示同步（仅在SPU有尺寸模板且SKU没有尺寸时）
         function checkSyncPrompt() {
             const templates = window.spuDimensionTemplates || [];
             const existingDimensions = $('.productsdimension_set-group .dynamic-productsdimension_set').length;
             
             // 只有当SPU有尺寸模板且SKU没有尺寸配置时才提示
             if (templates.length > 0 && existingDimensions === 0) {
                 setTimeout(function() {
                     if (confirm(`检测到SPU有 ${templates.length} 个尺寸模板，当前SKU还没有尺寸配置，是否要从SPU同步尺寸模板？`)) {
                         syncDimensionsFromSPU($('#id_spu').val());
                     }
                 }, 500);
             }
         }
        
        // 加载SPU的尺寸模板
        function loadSPUDimensionTemplates(spuId) {
            console.log('正在加载SPU尺寸模板，SPU ID:', spuId);
            
            // 这里需要通过AJAX调用后端API获取SPU的尺寸模板
            // 由于当前环境限制，我们先提供前端框架
            
            $.ajax({
                url: '/products/api/spu-dimension-templates/',
                method: 'GET',
                data: {
                    'spu_id': spuId
                },
                success: function(data) {
                    if (data.templates && data.templates.length > 0) {
                        handleSPUDimensionTemplates(data.templates);
                    }
                },
                                 error: function(xhr, status, error) {
                     console.log('加载SPU尺寸模板失败:', error);
                     // 如果API不存在，默认认为SPU没有尺寸模板
                     handleSPUDimensionTemplates([]);
                     $('.sync-help').text('无法连接到API服务或SPU没有尺寸模板');
                 }
            });
        }
        
                 // 处理SPU尺寸模板数据
         function handleSPUDimensionTemplates(templates) {
             console.log('处理SPU尺寸模板:', templates);
             
             // 存储模板数据供同步使用
             window.spuDimensionTemplates = templates;
             
             if (templates.length > 0) {
                 // SPU有尺寸模板时，更新同步按钮状态
                 $('.sync-dimensions-btn').removeClass('btn-info').addClass('btn-success')
                     .text('🔄 同步尺寸模板 (' + templates.length + '个)')
                     .show();
                     
                 // 检查是否需要提示同步
                 checkSyncPrompt();
             } else {
                 // SPU没有尺寸模板时，隐藏同步按钮
                 $('.sync-dimensions-btn').hide();
                 $('.sync-help').text('当前SPU没有配置尺寸模板');
             }
         }
        
                 // 处理模拟的SPU尺寸模板数据（用于演示）
         function handleMockSPUDimensionTemplates() {
             // 模拟没有尺寸模板的情况（更真实）
             const mockTemplates = [];
             
             // 如果需要测试有尺寸模板的情况，可以取消下面的注释
             /*
             const mockTemplates = [
                 {
                     dimension_type: 'height',
                     default_value: 1800,
                     unit: 'mm',
                     min_value: 1000,
                     max_value: 2400,
                     is_key_dimension: true,
                     is_required: true,
                     order: 1
                 },
                 {
                     dimension_type: 'width',
                     default_value: 600,
                     unit: 'mm',
                     min_value: 300,
                     max_value: 1200,
                     is_key_dimension: true,
                     is_required: true,
                     order: 2
                 }
             ];
             */
             
             handleSPUDimensionTemplates(mockTemplates);
         }
        
        // 从SPU同步尺寸到SKU
        function syncDimensionsFromSPU(spuId) {
            console.log('开始同步SPU尺寸到SKU');
            
            const templates = window.spuDimensionTemplates || [];
            
            if (templates.length === 0) {
                alert('当前SPU没有配置尺寸模板，无法同步');
                return;
            }
            
            // 确认是否要清除现有尺寸并重新同步
            const existingDimensions = $('.productsdimension_set-group .dynamic-productsdimension_set').length;
            if (existingDimensions > 0) {
                if (!confirm(`当前SKU已有 ${existingDimensions} 个尺寸配置，同步将清除现有配置并从SPU重新创建，确定要继续吗？`)) {
                    return;
                }
                
                // 清除现有的尺寸行
                $('.productsdimension_set-group .dynamic-productsdimension_set').remove();
            }
            
            // 添加新的尺寸行
            templates.forEach(function(template, index) {
                addDimensionRow(template, index);
            });
            
            // 更新总行数
            updateTotalForms();
            
            // 显示成功消息
            showSuccessMessage(`已成功从SPU同步 ${templates.length} 个尺寸模板`);
        }
        
        // 添加尺寸行
        function addDimensionRow(template, index) {
            // 点击添加按钮来获取新的表单行
            $('.add-row a').click();
            
            // 等待DOM更新后填充数据
            setTimeout(function() {
                const $lastRow = $('.productsdimension_set-group .dynamic-productsdimension_set').last();
                
                if ($lastRow.length) {
                    // 填充模板数据
                    $lastRow.find('select[name$="dimension_type"]').val(template.dimension_type);
                    $lastRow.find('input[name$="standard_value"]').val(template.default_value);
                    $lastRow.find('select[name$="unit"]').val(template.unit);
                    $lastRow.find('input[name$="min_value"]').val(template.min_value || '');
                    $lastRow.find('input[name$="max_value"]').val(template.max_value || '');
                    $lastRow.find('input[name$="is_key_dimension"]').prop('checked', template.is_key_dimension || false);
                    
                    // 设置备注信息
                    const remarks = `从SPU同步 - ${template.is_required ? '必需字段' : '可选字段'}`;
                    $lastRow.find('input[name$="remarks"]').val(remarks);
                }
            }, 100);
        }
        
        // 更新表单总数
        function updateTotalForms() {
            const totalForms = $('.productsdimension_set-group .dynamic-productsdimension_set').length;
            $('input[name="productsdimension_set-TOTAL_FORMS"]').val(totalForms);
        }
        
        // 显示成功消息
        function showSuccessMessage(message) {
            const successAlert = `
                <div class="alert alert-success" style="margin: 10px 0; padding: 10px; border: 1px solid #d4edda; background-color: #d1ecf1; color: #155724; border-radius: 4px;">
                    ✅ ${message}
                </div>
            `;
            
            $('.sync-dimensions-container').after(successAlert);
            
            // 3秒后自动隐藏
            setTimeout(function() {
                $('.alert-success').fadeOut();
            }, 3000);
        }
        
        // 添加样式增强
        function addSKUDimensionStyles() {
            const styles = `
                <style>
                .sync-dimensions-container {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 10px 0;
                }
                .sync-dimensions-btn:hover {
                    background: #138496 !important;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .productsdimension_set-group .synced-dimension {
                    background-color: #f0fff0;
                    border-left: 3px solid #28a745;
                }
                </style>
            `;
            
            if (!$('#sku-dimension-sync-styles').length) {
                $('head').append(styles);
                $('<div id="sku-dimension-sync-styles"></div>').appendTo('head');
            }
        }
        
        // 检查是否在SKU编辑页面
        if (window.location.pathname.includes('/products/sku/')) {
            initSKUDimensionSync();
            addSKUDimensionStyles();
        }
    });

})(django.jQuery); 