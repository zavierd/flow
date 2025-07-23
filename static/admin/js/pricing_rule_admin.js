/**
 * 产品加价规则管理的自定义JavaScript
 */

(function($) {
    'use strict';

    $(document).ready(function() {
        // 当SPU选择改变时，更新SKU选项
        $('#id_spu').change(function() {
            var spuId = $(this).val();
            var skuSelect = $('#id_sku');
            
            if (spuId) {
                // 获取该SPU下的所有SKU
                $.ajax({
                    url: '/admin/products/get_sku_by_spu/',
                    data: {
                        'spu_id': spuId
                    },
                    success: function(data) {
                        skuSelect.empty();
                        skuSelect.append('<option value="">---------</option>');
                        
                        $.each(data.skus, function(index, sku) {
                            skuSelect.append(
                                '<option value="' + sku.id + '">' + 
                                sku.name + ' (' + sku.code + ')' + 
                                '</option>'
                            );
                        });
                    },
                    error: function() {
                        console.log('获取SKU列表失败');
                    }
                });
            } else {
                skuSelect.empty();
                skuSelect.append('<option value="">---------</option>');
            }
        });

        // 根据计算方法显示/隐藏相关字段
        function toggleFieldsByCalculationMethod() {
            var method = $('#id_calculation_method').val();
            var priceIncrementRow = $('.field-price_increment');
            var multiplierRow = $('.field-multiplier');
            var unitIncrementRow = $('.field-unit_increment');
            
            // 重置所有字段显示
            priceIncrementRow.show();
            multiplierRow.show();
            unitIncrementRow.show();
            
            switch(method) {
                case 'fixed':
                    multiplierRow.hide();
                    unitIncrementRow.hide();
                    break;
                case 'percentage':
                    multiplierRow.hide();
                    break;
                case 'multiplier':
                    priceIncrementRow.hide();
                    break;
                case 'step':
                    // 显示所有字段
                    break;
            }
        }

        // 初始化字段显示
        toggleFieldsByCalculationMethod();
        
        // 监听计算方法变化
        $('#id_calculation_method').change(toggleFieldsByCalculationMethod);

        // 添加规则范围提示
        function updateRuleScopeHint() {
            var skuValue = $('#id_sku').val();
            var hintElement = $('#rule-scope-hint');
            
            if (hintElement.length === 0) {
                // 创建提示元素
                hintElement = $('<div id="rule-scope-hint" style="margin-top: 10px; padding: 10px; border-radius: 4px; font-size: 12px;"></div>');
                $('.field-sku').append(hintElement);
            }
            
            if (skuValue) {
                hintElement.html(
                    '<span style="color: #e74c3c; font-weight: bold;">SKU专属规则</span> - ' +
                    '此规则仅应用于选定的SKU，优先级高于SPU通用规则'
                ).css('background-color', '#ffe6e6');
            } else {
                hintElement.html(
                    '<span style="color: #3498db;">SPU通用规则</span> - ' +
                    '此规则应用于该SPU下的所有SKU（除非有SKU专属规则）'
                ).css('background-color', '#e6f3ff');
            }
        }

        // 初始化和监听SKU选择变化
        updateRuleScopeHint();
        $('#id_sku').change(updateRuleScopeHint);

        // 添加字段验证
        $('form').submit(function(e) {
            var thresholdValue = parseFloat($('#id_threshold_value').val());
            var priceIncrement = parseFloat($('#id_price_increment').val());
            var unitIncrement = parseFloat($('#id_unit_increment').val());
            
            var errors = [];
            
            if (thresholdValue <= 0) {
                errors.push('阈值必须大于0');
            }
            
            if (priceIncrement <= 0) {
                errors.push('价格增量必须大于0');
            }
            
            if (unitIncrement <= 0) {
                errors.push('单位增量必须大于0');
            }
            
            if (errors.length > 0) {
                alert('请修正以下错误：\n' + errors.join('\n'));
                e.preventDefault();
                return false;
            }
        });
    });

})(django.jQuery); 