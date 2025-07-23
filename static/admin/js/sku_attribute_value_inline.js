// SKU属性值内联编辑JavaScript

(function($) {
    'use strict';

    // 初始化函数
    function initSKUAttributeValueInline() {
        // 为属性选择器添加变化监听
        $(document).on('change', '.inline-group select[name*="attribute"]', function() {
            updateAttributeValueOptions(this);
        });

        // 初始化现有行
        $('.inline-group select[name*="attribute"]').each(function() {
            if ($(this).val()) {
                updateAttributeValueOptions(this);
            }
        });
    }

    // 更新属性值选项
    function updateAttributeValueOptions(attributeSelect) {
        const $attributeSelect = $(attributeSelect);
        const selectedAttributeId = $attributeSelect.val();
        const $row = $attributeSelect.closest('tr');
        const $valueSelect = $row.find('select[name*="attribute_value"]');
        const currentValueId = $valueSelect.val(); // 保存当前选中的值

        if (!selectedAttributeId) {
            $valueSelect.html('<option value="">--- 请先选择属性 ---</option>');
            return;
        }

        // 显示加载状态
        $valueSelect.html('<option value="">加载中...</option>');
        $valueSelect.prop('disabled', true);

        // 获取属性值选项
        $.ajax({
            url: '/admin/products/attribute/' + selectedAttributeId + '/values/',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                let options = '<option value="">--- 请选择属性值 ---</option>';
                
                if (data.values && data.values.length > 0) {
                    data.values.forEach(function(value) {
                        const displayName = value.display_name || value.value;
                        const selected = (currentValueId && currentValueId == value.id) ? ' selected' : '';
                        options += `<option value="${value.id}"${selected}>${displayName}</option>`;
                    });
                } else {
                    options = '<option value="">该属性暂无可用值</option>';
                }
                
                $valueSelect.html(options);
                $valueSelect.prop('disabled', false);
                
                // 如果之前有选中值且仍然有效，保持选中状态
                if (currentValueId && $valueSelect.find(`option[value="${currentValueId}"]`).length > 0) {
                    $valueSelect.val(currentValueId);
                }
            },
            error: function() {
                $valueSelect.html('<option value="">加载失败，请重试</option>');
                $valueSelect.prop('disabled', false);
            }
        });
    }

    // 页面加载完成后初始化
    $(document).ready(function() {
        initSKUAttributeValueInline();
    });

    // 监听Django admin的添加行事件
    $(document).on('click', '.add-row a', function() {
        setTimeout(function() {
            initSKUAttributeValueInline();
        }, 100);
    });

})(django.jQuery); 