/**
 * SPU尺寸模板管理JavaScript
 * 用于增强SPU尺寸模板的用户体验
 */

(function($) {
    'use strict';

    // 等待DOM加载完成
    $(document).ready(function() {
        
        // 尺寸类型和单位的对应关系
        const dimensionUnits = {
            'height': ['mm', 'cm', 'm'],
            'width': ['mm', 'cm', 'm'],
            'depth': ['mm', 'cm', 'm'],
            'length': ['mm', 'cm', 'm'],
            'diameter': ['mm', 'cm', 'm'],
            'thickness': ['mm', 'cm'],
            'weight': ['g', 'kg'],
            'area': ['m²', 'cm²'],
            'volume': ['m³', 'cm³', 'L']
        };

        // 初始化尺寸模板功能
        function initSPUDimensionTemplate() {
            console.log('初始化SPU尺寸模板功能');
            
            // 为尺寸类型选择添加change事件
            $(document).on('change', '.field-dimension_type select', function() {
                const dimensionType = $(this).val();
                const $row = $(this).closest('tr');
                const $unitSelect = $row.find('.field-unit select');
                
                if (dimensionType && dimensionUnits[dimensionType]) {
                    // 清空现有选项
                    $unitSelect.empty();
                    
                    // 添加默认选项
                    $unitSelect.append('<option value="">---------</option>');
                    
                    // 添加相应的单位选项
                    dimensionUnits[dimensionType].forEach(function(unit) {
                        $unitSelect.append(`<option value="${unit}">${unit}</option>`);
                    });
                    
                    // 设置默认单位
                    if (dimensionUnits[dimensionType].length > 0) {
                        $unitSelect.val(dimensionUnits[dimensionType][0]);
                    }
                }
            });
            
            // 为新增行添加序号自动排序
            $(document).on('click', '.add-row a', function() {
                setTimeout(function() {
                    updateDimensionOrder();
                }, 100);
            });
            
            // 自动更新排序
            function updateDimensionOrder() {
                $('.field-order input').each(function(index) {
                    if ($(this).val() === '' || $(this).val() === '0') {
                        $(this).val(index + 1);
                    }
                });
            }
            
            // 验证尺寸值的合理性
            $(document).on('blur', '.field-default_value input, .field-min_value input, .field-max_value input', function() {
                validateDimensionValues($(this).closest('tr'));
            });
            
            function validateDimensionValues($row) {
                const defaultValue = parseFloat($row.find('.field-default_value input').val()) || 0;
                const minValue = parseFloat($row.find('.field-min_value input').val()) || 0;
                const maxValue = parseFloat($row.find('.field-max_value input').val()) || 0;
                
                // 检查最小值和最大值的合理性
                if (minValue > 0 && maxValue > 0 && minValue >= maxValue) {
                    alert('最小值不能大于或等于最大值');
                    $row.find('.field-min_value input').focus();
                    return false;
                }
                
                // 检查默认值是否在合理范围内
                if (defaultValue > 0) {
                    if (minValue > 0 && defaultValue < minValue) {
                        alert('默认值不能小于最小值');
                        $row.find('.field-default_value input').focus();
                        return false;
                    }
                    if (maxValue > 0 && defaultValue > maxValue) {
                        alert('默认值不能大于最大值');
                        $row.find('.field-default_value input').focus();
                        return false;
                    }
                }
                
                return true;
            }
            
            // 添加样式增强
            addSPUDimensionStyles();
        }
        
        // 添加自定义样式
        function addSPUDimensionStyles() {
            const styles = `
                <style>
                .spudimensiontemplate_set-group .table {
                    border-collapse: collapse;
                }
                .spudimensiontemplate_set-group .table th,
                .spudimensiontemplate_set-group .table td {
                    padding: 8px;
                    border: 1px solid #ddd;
                }
                .spudimensiontemplate_set-group .field-dimension_type {
                    min-width: 100px;
                }
                .spudimensiontemplate_set-group .field-default_value input,
                .spudimensiontemplate_set-group .field-min_value input,
                .spudimensiontemplate_set-group .field-max_value input {
                    width: 80px;
                }
                .spudimensiontemplate_set-group .field-unit {
                    min-width: 60px;
                }
                .spudimensiontemplate_set-group .field-order input {
                    width: 50px;
                }
                .dimension-template-help {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 10px 0;
                    font-size: 12px;
                    color: #6c757d;
                }
                </style>
            `;
            
            if (!$('#spu-dimension-template-styles').length) {
                $('head').append(styles);
                $('<div id="spu-dimension-template-styles"></div>').appendTo('head');
            }
        }
        
        // 添加帮助信息
        function addDimensionTemplateHelp() {
            const helpText = `
                <div class="dimension-template-help">
                    <strong>📏 尺寸模板配置说明：</strong><br/>
                    • <strong>尺寸类型</strong>：选择尺寸维度，系统会自动推荐相应的单位<br/>
                    • <strong>默认值</strong>：创建SKU时的默认尺寸值<br/>
                    • <strong>最小值/最大值</strong>：SKU可调整的尺寸范围<br/>
                    • <strong>关键尺寸</strong>：标记为影响价格计算的重要尺寸<br/>
                    • <strong>必需字段</strong>：创建SKU时必须填写的尺寸
                </div>
            `;
            
            const $dimensionGroup = $('.spudimensiontemplate_set-group');
            if ($dimensionGroup.length && !$dimensionGroup.find('.dimension-template-help').length) {
                $dimensionGroup.find('h2').after(helpText);
            }
        }
        
        // 检查是否在SPU编辑页面
        if (window.location.pathname.includes('/products/spu/')) {
            initSPUDimensionTemplate();
            
            // 延迟添加帮助信息，确保DOM完全加载
            setTimeout(function() {
                addDimensionTemplateHelp();
            }, 500);
        }
    });

})(django.jQuery); 