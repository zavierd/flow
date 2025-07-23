// SPU 属性内联编辑 JavaScript 功能

(function($) {
    'use strict';

    // 当文档准备就绪时执行
    $(document).ready(function() {
        initSPUAttributeInline();
    });

    function initSPUAttributeInline() {
        // 初始化属性选择变化监听
        initAttributeChangeListener();
        
        // 初始化表单验证
        initFormValidation();
        
        // 初始化工具提示
        initTooltips();
        
        // 初始化拖拽排序
        initDragSort();
        
        // 初始化动态属性加载
        initDynamicAttributeLoading();
        
        // 初始化分类属性推荐
        initCategoryAttributeRecommendations();
        
        // 初始化现有行的默认值字段
        initExistingRowsDefaultValue();
        
        // 监听新增行事件
        $(document).on('formset:added', function(event, $row) {
            // 为新增的行初始化功能
            initRowFeatures($row);
        });
    }

    function initDynamicAttributeLoading() {
        // 监听分类选择变化
        var $categoryField = $('#id_category');
        if ($categoryField.length) {
            $categoryField.on('change', function() {
                var categoryId = $(this).val();
                if (categoryId) {
                    loadCategoryRecommendations(categoryId);
                    updateAttributeOptions(categoryId);
                }
            });
            
            // 如果已有分类，初始加载
            if ($categoryField.val()) {
                loadCategoryRecommendations($categoryField.val());
            }
        }
        
        // 添加属性搜索功能
        addAttributeSearchBox();
        
        // 添加快速添加推荐属性按钮
        addQuickAddButtons();
    }

    function loadCategoryRecommendations(categoryId) {
        var url = getAdminUrl('category-attributes/' + categoryId + '/');
        
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            beforeSend: function() {
                showRecommendationsLoading();
            },
            success: function(data) {
                if (data.success) {
                    displayRecommendations(data);
                } else {
                    showMessage('获取推荐属性失败: ' + data.error, 'error');
                }
            },
            error: function(xhr, status, error) {
                console.error('加载分类推荐属性失败:', error);
                showMessage('加载推荐属性失败', 'error');
            },
            complete: function() {
                hideRecommendationsLoading();
            }
        });
    }

    function updateAttributeOptions(categoryId) {
        // 获取当前SPU的ID（如果是编辑模式）
        var spuId = getSpuId();
        
        var url = getAdminUrl('attribute-api/');
        var params = {
            category_id: categoryId,
            exclude_spu: spuId,
            limit: 50
        };
        
        $.ajax({
            url: url,
            method: 'GET',
            data: params,
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    updateAttributeSelectOptions(data.data);
                } else {
                    console.error('获取属性列表失败:', data.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('加载属性列表失败:', error);
            }
        });
    }

    function updateAttributeSelectOptions(attributes) {
        // 更新所有属性选择框的选项
        $('.field-attribute select').each(function() {
            var $select = $(this);
            var currentValue = $select.val();
            
            // 保存当前选项
            var $currentOption = $select.find('option:selected').clone();
            
            // 清空选项
            $select.empty();
            
            // 添加空选项
            $select.append('<option value="">---------</option>');
            
            // 添加分类常用属性
            var commonAttributes = attributes.filter(attr => attr.is_category_common);
            if (commonAttributes.length > 0) {
                var $commonGroup = $('<optgroup label="分类常用属性"></optgroup>');
                commonAttributes.forEach(function(attr) {
                    var $option = createAttributeOption(attr);
                    $commonGroup.append($option);
                });
                $select.append($commonGroup);
            }
            
            // 添加其他属性
            var otherAttributes = attributes.filter(attr => !attr.is_category_common);
            if (otherAttributes.length > 0) {
                var $otherGroup = $('<optgroup label="其他可用属性"></optgroup>');
                otherAttributes.forEach(function(attr) {
                    var $option = createAttributeOption(attr);
                    $otherGroup.append($option);
                });
                $select.append($otherGroup);
            }
            
            // 恢复当前选择
            if (currentValue) {
                $select.val(currentValue);
                if (!$select.val()) {
                    // 如果当前值不在新选项中，添加回去
                    $select.append($currentOption);
                    $select.val(currentValue);
                }
            }
        });
    }

    function createAttributeOption(attr) {
        var $option = $('<option></option>');
        $option.val(attr.id);
        $option.text(attr.display_label);
        $option.attr('data-type', attr.type);
        $option.attr('data-unit', attr.unit);
        $option.attr('data-values-count', attr.values_count);
        return $option;
    }

    function displayRecommendations(data) {
        var $container = getOrCreateRecommendationsContainer();
        
        if (data.recommendations.length === 0) {
            $container.html('<div class="no-recommendations">该分类暂无推荐属性</div>');
            return;
        }
        
        var html = '<div class="recommendations-header">';
        html += '<h4>推荐属性 <small>(' + data.category.name + ')</small></h4>';
        html += '<p class="recommendations-info">基于 ' + data.total_spus + ' 个SPU的使用情况分析</p>';
        html += '</div>';
        
        html += '<div class="recommendations-list">';
        
        data.recommendations.forEach(function(rec) {
            var levelClass = 'recommendation-' + rec.recommendation_level;
            var levelText = {
                'high': '强烈推荐',
                'medium': '推荐',
                'low': '可选',
                'optional': '备选'
            }[rec.recommendation_level] || '推荐';
            
            html += '<div class="recommendation-item ' + levelClass + '">';
            html += '<div class="recommendation-header">';
            html += '<span class="recommendation-name">' + rec.name + '</span>';
            html += '<span class="recommendation-type">[' + rec.type_display + ']</span>';
            if (rec.unit) {
                html += '<span class="recommendation-unit">(' + rec.unit + ')</span>';
            }
            html += '<span class="recommendation-level">' + levelText + '</span>';
            html += '</div>';
            html += '<div class="recommendation-stats">';
            html += '<span class="usage-count">' + rec.usage_count + ' 次使用</span>';
            html += '<span class="usage-percentage">' + rec.usage_percentage + '%</span>';
            html += '</div>';
            html += '<div class="recommendation-actions">';
            html += '<button type="button" class="btn-add-recommendation" data-attribute-id="' + rec.attribute_id + '" data-name="' + rec.name + '">添加</button>';
            html += '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        
        $container.html(html);
        
        // 绑定添加推荐属性事件
        $container.find('.btn-add-recommendation').on('click', function() {
            var attributeId = $(this).data('attribute-id');
            var attributeName = $(this).data('name');
            addRecommendedAttribute(attributeId, attributeName);
        });
    }

    function addRecommendedAttribute(attributeId, attributeName) {
        // 检查是否已经添加过
        var isAlreadyAdded = false;
        $('.field-attribute select').each(function() {
            if ($(this).val() == attributeId) {
                isAlreadyAdded = true;
                return false;
            }
        });
        
        if (isAlreadyAdded) {
            showMessage('属性 "' + attributeName + '" 已经添加', 'warning');
            return;
        }
        
        // 查找空的行或添加新行
        var $emptyRow = null;
        $('.inline-group .form-row:not(.add-row)').each(function() {
            var $row = $(this);
            var $select = $row.find('.field-attribute select');
            if (!$select.val() && !$row.find('.delete input[type="checkbox"]').is(':checked')) {
                $emptyRow = $row;
                return false;
            }
        });
        
        if (!$emptyRow) {
            // 添加新行
            $('.add-row a').click();
            // 等待新行添加完成
            setTimeout(function() {
                $emptyRow = $('.inline-group .form-row:not(.add-row):last');
                setAttributeForRow($emptyRow, attributeId);
            }, 100);
        } else {
            setAttributeForRow($emptyRow, attributeId);
        }
        
        showMessage('已添加推荐属性: ' + attributeName, 'success');
    }

    function setAttributeForRow($row, attributeId) {
        var $select = $row.find('.field-attribute select');
        $select.val(attributeId).trigger('change');
        
        // 设置默认排序
        var $orderInput = $row.find('.field-order input');
        if ($orderInput.length && !$orderInput.val()) {
            var maxOrder = 0;
            $('.field-order input').each(function() {
                var val = parseInt($(this).val()) || 0;
                if (val > maxOrder) {
                    maxOrder = val;
                }
            });
            $orderInput.val(maxOrder + 1);
        }
    }

    function addAttributeSearchBox() {
        var $searchContainer = $('<div class="attribute-search-container">');
        $searchContainer.html(`
            <div class="search-header">
                <h4>属性搜索</h4>
                <button type="button" class="btn-toggle-search">展开</button>
            </div>
            <div class="search-body" style="display: none;">
                <div class="search-form">
                    <input type="text" id="attribute-search-input" placeholder="搜索属性名称或编码..." />
                    <select id="attribute-type-filter">
                        <option value="">所有类型</option>
                        <option value="text">文本</option>
                        <option value="number">数字</option>
                        <option value="select">单选</option>
                        <option value="multiselect">多选</option>
                        <option value="boolean">布尔值</option>
                        <option value="date">日期</option>
                        <option value="color">颜色</option>
                        <option value="image">图片</option>
                    </select>
                    <button type="button" id="btn-search-attributes">搜索</button>
                </div>
                <div class="search-results"></div>
            </div>
        `);
        
        $('.inline-group').before($searchContainer);
        
        // 绑定事件
        $searchContainer.find('.btn-toggle-search').on('click', function() {
            var $body = $searchContainer.find('.search-body');
            $body.toggle();
            $(this).text($body.is(':visible') ? '收起' : '展开');
        });
        
        var searchTimer;
        $searchContainer.find('#attribute-search-input').on('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(function() {
                performAttributeSearch();
            }, 300);
        });
        
        $searchContainer.find('#attribute-type-filter').on('change', performAttributeSearch);
        $searchContainer.find('#btn-search-attributes').on('click', performAttributeSearch);
    }

    function performAttributeSearch() {
        var searchTerm = $('#attribute-search-input').val().trim();
        var typeFilter = $('#attribute-type-filter').val();
        
        if (!searchTerm && !typeFilter) {
            $('.search-results').empty();
            return;
        }
        
        var url = getAdminUrl('attribute-api/');
        var spuId = getSpuId();
        var params = {
            search: searchTerm,
            type: typeFilter,
            exclude_spu: spuId,
            limit: 20
        };
        
        $.ajax({
            url: url,
            method: 'GET',
            data: params,
            dataType: 'json',
            beforeSend: function() {
                $('.search-results').html('<div class="loading">搜索中...</div>');
            },
            success: function(data) {
                if (data.success) {
                    displaySearchResults(data.data);
                } else {
                    $('.search-results').html('<div class="error">搜索失败: ' + data.error + '</div>');
                }
            },
            error: function() {
                $('.search-results').html('<div class="error">搜索请求失败</div>');
            }
        });
    }

    function displaySearchResults(attributes) {
        var $results = $('.search-results');
        
        if (attributes.length === 0) {
            $results.html('<div class="no-results">未找到匹配的属性</div>');
            return;
        }
        
        var html = '<div class="search-results-list">';
        attributes.forEach(function(attr) {
            html += '<div class="search-result-item">';
            html += '<div class="result-info">';
            html += '<span class="result-name">' + attr.name + '</span>';
            html += '<span class="result-type">[' + attr.type_display + ']</span>';
            if (attr.unit) {
                html += '<span class="result-unit">(' + attr.unit + ')</span>';
            }
            html += '<span class="result-code">' + attr.code + '</span>';
            html += '</div>';
            if (attr.description) {
                html += '<div class="result-description">' + attr.description + '</div>';
            }
            if (attr.preview_values && attr.preview_values.length > 0) {
                html += '<div class="result-values">';
                attr.preview_values.forEach(function(value) {
                    if (attr.type === 'color' && value.color_code) {
                        html += '<span class="value-preview color-preview" style="background-color: ' + value.color_code + '" title="' + value.display_name + '"></span>';
                    } else {
                        html += '<span class="value-preview text-preview">' + value.display_name + '</span>';
                    }
                });
                if (attr.has_more_values) {
                    html += '<span class="more-values">...</span>';
                }
                html += '</div>';
            }
            html += '<div class="result-actions">';
            html += '<button type="button" class="btn-add-search-result" data-attribute-id="' + attr.id + '" data-name="' + attr.name + '">添加</button>';
            html += '</div>';
            html += '</div>';
        });
        html += '</div>';
        
        $results.html(html);
        
        // 绑定添加事件
        $results.find('.btn-add-search-result').on('click', function() {
            var attributeId = $(this).data('attribute-id');
            var attributeName = $(this).data('name');
            addRecommendedAttribute(attributeId, attributeName);
        });
    }

    function getOrCreateRecommendationsContainer() {
        var $container = $('.attribute-recommendations');
        if ($container.length === 0) {
            $container = $('<div class="attribute-recommendations">');
            $('.inline-group').before($container);
        }
        return $container;
    }

    function showRecommendationsLoading() {
        var $container = getOrCreateRecommendationsContainer();
        $container.html('<div class="recommendations-loading">正在加载推荐属性...</div>');
    }

    function hideRecommendationsLoading() {
        // Loading状态会被实际内容替换，这里不需要特别处理
    }

    function getSpuId() {
        // 从URL中提取SPU ID（编辑模式）
        var urlMatch = window.location.pathname.match(/\/(\d+)\/change\//);
        return urlMatch ? urlMatch[1] : null;
    }

    function getAdminUrl(path) {
        // 优先使用统一的AdminUrlConfig模块
        if (typeof window.AdminUrlConfig !== 'undefined') {
            return window.AdminUrlConfig.getAdminUrl(path);
        }
        
        // 备用方案：保持原有逻辑
        console.warn('⚠️ AdminUrlConfig未加载，使用备用URL构建方案');
        var adminUrlBase = window.location.pathname.replace(/\/change\/$/, '').replace(/\/add\/$/, '');
        if (adminUrlBase.endsWith('/spu')) {
            adminUrlBase = adminUrlBase.replace('/spu', '/spu/');
        }
        return adminUrlBase + path;
    }

    function initCategoryAttributeRecommendations() {
        // 初始化分类属性推荐功能
        var $categoryField = $('#id_category');
        if ($categoryField.length && $categoryField.val()) {
            loadCategoryRecommendations($categoryField.val());
        }
    }

    function initExistingRowsDefaultValue() {
        // 为现有行初始化默认值字段
        $('.inline-group .form-row:not(.add-row)').each(function() {
            var $row = $(this);
            var $attributeSelect = $row.find('.field-attribute select');
            
            if ($attributeSelect.length && $attributeSelect.val()) {
                // 延迟一点执行，确保页面完全加载
                setTimeout(function() {
                    updateDefaultValueField($row, $attributeSelect.val());
                }, 100);
            }
        });
    }

    function initAttributeChangeListener() {
        // 监听属性选择框的变化
        $(document).on('change', '.field-attribute select', function() {
            var $select = $(this);
            var $row = $select.closest('.form-row');
            var attributeId = $select.val();
            
            if (attributeId) {
                // 显示加载动画
                showLoading($row);
                
                // 获取属性详细信息
                fetchAttributeDetails(attributeId, $row);
                
                // 更新默认值字段为下拉选择器
                updateDefaultValueField($row, attributeId);
            } else {
                // 清空属性信息显示
                clearAttributeInfo($row);
                
                // 恢复默认值字段为文本输入框
                resetDefaultValueField($row);
            }
        });
    }

    function fetchAttributeDetails(attributeId, $row) {
        var url = getAdminUrl('attribute-values/' + attributeId + '/');
        
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    updateAttributeInfoDisplay($row, data.attribute, data.values);
                }
            },
            error: function() {
                console.error('获取属性详情失败');
            },
            complete: function() {
                hideLoading($row);
            }
        });
    }

    function updateAttributeInfoDisplay($row, attribute, values) {
        // 更新属性信息显示列
        var $infoCell = $row.find('.field-get_attribute_info');
        if ($infoCell.length) {
            // 这里可以动态更新属性信息显示
            // 实际显示内容由后端模板方法生成，这里可以添加额外的前端增强
        }
        
        // 更新属性值预览列
        var $previewCell = $row.find('.field-get_values_preview');
        if ($previewCell.length && values.length > 0) {
            // 可以在这里添加更丰富的前端预览显示
        }
    }

    function updateDefaultValueField($row, attributeId) {
        // 获取属性值并更新默认值字段为下拉选择器
        var url = getAdminUrl('attribute-values/' + attributeId + '/');
        
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                if (data.success && data.values && data.values.length > 0) {
                    var $defaultValueField = $row.find('.field-default_value input');
                    if ($defaultValueField.length) {
                        var currentValue = $defaultValueField.val();
                        
                        // 创建下拉选择器
                        var $select = $('<select name="' + $defaultValueField.attr('name') + '" id="' + $defaultValueField.attr('id') + '">');
                        $select.addClass($defaultValueField.attr('class'));
                        
                        // 添加空选项
                        $select.append('<option value="">--- 请选择 ---</option>');
                        
                        // 添加属性值选项
                        data.values.forEach(function(value) {
                            var displayName = value.display_name || value.value;
                            var $option = $('<option value="' + value.value + '">' + displayName + '</option>');
                            if (value.value === currentValue) {
                                $option.attr('selected', 'selected');
                            }
                            $select.append($option);
                        });
                        
                        // 替换输入框
                        $defaultValueField.replaceWith($select);
                        
                        // 更新帮助文本
                        var $helpText = $row.find('.field-default_value .help');
                        if ($helpText.length) {
                            $helpText.text('从' + data.attribute.name + '的可用值中选择默认值');
                        }
                    }
                }
            },
            error: function() {
                console.error('获取属性值失败');
            }
        });
    }

    function resetDefaultValueField($row) {
        // 恢复默认值字段为文本输入框
        var $defaultValueField = $row.find('.field-default_value select');
        if ($defaultValueField.length) {
            var currentValue = $defaultValueField.val();
            
            // 创建文本输入框
            var $input = $('<input type="text" name="' + $defaultValueField.attr('name') + '" id="' + $defaultValueField.attr('id') + '" maxlength="200">');
            $input.addClass($defaultValueField.attr('class'));
            $input.val(currentValue);
            
            // 替换下拉选择器
            $defaultValueField.replaceWith($input);
            
            // 恢复帮助文本
            var $helpText = $row.find('.field-default_value .help');
            if ($helpText.length) {
                $helpText.text('创建SKU时的默认属性值');
            }
        }
    }

    function clearAttributeInfo($row) {
        // 清空属性信息显示
        var $infoCell = $row.find('.field-get_attribute_info');
        if ($infoCell.length) {
            $infoCell.html('-');
        }
        
        var $previewCell = $row.find('.field-get_values_preview');
        if ($previewCell.length) {
            $previewCell.html('-');
        }
    }

    function showLoading($row) {
        var $loadingIndicator = $('<span class="loading-spinner"></span>');
        $row.find('.field-attribute').append($loadingIndicator);
    }

    function hideLoading($row) {
        $row.find('.loading-spinner').remove();
    }

    function initFormValidation() {
        // 表单提交前验证
        $('form').on('submit', function(e) {
            if (!validateAttributes()) {
                e.preventDefault();
                showValidationErrors();
                return false;
            }
        });
    }

    function validateAttributes() {
        var attributes = [];
        var hasError = false;
        
        $('.field-attribute select').each(function() {
            var $select = $(this);
            var $row = $select.closest('.form-row');
            var isDeleted = $row.find('.delete input[type="checkbox"]').is(':checked');
            
            if (!isDeleted && $select.val()) {
                var attributeId = $select.val();
                if (attributes.indexOf(attributeId) !== -1) {
                    // 发现重复属性
                    $select.addClass('error');
                    hasError = true;
                } else {
                    attributes.push(attributeId);
                    $select.removeClass('error');
                }
            }
        });
        
        return !hasError;
    }

    function showValidationErrors() {
        // 显示验证错误消息
        var $errorMsg = $('.duplicate-attribute-error');
        if ($errorMsg.length === 0) {
            $errorMsg = $('<div class="duplicate-attribute-error errorlist">检测到重复的属性关联，请检查并修正。</div>');
            $('.inline-group').prepend($errorMsg);
        }
        
        // 3秒后自动隐藏错误消息
        setTimeout(function() {
            $errorMsg.fadeOut();
        }, 3000);
    }

    function initTooltips() {
        // 初始化工具提示
        $(document).on('mouseenter', '[title]', function() {
            var $element = $(this);
            var title = $element.attr('title');
            
            if (title && !$element.data('tooltip-initialized')) {
                $element.tooltip({
                    placement: 'top',
                    trigger: 'hover',
                    delay: { show: 500, hide: 100 }
                });
                $element.data('tooltip-initialized', true);
            }
        });
    }

    function initDragSort() {
        // 初始化拖拽排序功能
        if ($.fn.sortable) {
            $('.inline-group .tabular').sortable({
                items: '.form-row:not(.add-row)',
                handle: '.field-order input',
                placeholder: 'sortable-placeholder',
                helper: 'clone',
                start: function(e, ui) {
                    ui.placeholder.height(ui.item.height());
                },
                update: function(e, ui) {
                    updateOrderNumbers();
                }
            });
        }
    }

    function updateOrderNumbers() {
        // 更新排序号
        $('.inline-group .form-row:not(.add-row)').each(function(index) {
            var $row = $(this);
            var $orderInput = $row.find('.field-order input');
            if ($orderInput.length) {
                $orderInput.val(index + 1);
            }
        });
    }

    function initRowFeatures($row) {
        // 为新行初始化功能
        initAttributeChangeListener();
        initTooltips();
        
        // 设置默认排序号
        var $orderInput = $row.find('.field-order input');
        if ($orderInput.length && !$orderInput.val()) {
            var maxOrder = 0;
            $('.field-order input').each(function() {
                var val = parseInt($(this).val()) || 0;
                if (val > maxOrder) {
                    maxOrder = val;
                }
            });
            $orderInput.val(maxOrder + 1);
        }
        
        // 检查新行是否已经选择了属性，如果是则更新默认值字段
        var $attributeSelect = $row.find('.field-attribute select');
        if ($attributeSelect.length && $attributeSelect.val()) {
            updateDefaultValueField($row, $attributeSelect.val());
        }
    }

    function showMessage(text, type) {
        var $message = $('<div class="alert alert-' + type + ' fade show">' + text + '</div>');
        $('.inline-group').prepend($message);
        
        setTimeout(function() {
            $message.fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }

    // 导出全局函数供其他脚本使用
    window.SPUAttributeInline = {
        updateOrderNumbers: updateOrderNumbers,
        validateAttributes: validateAttributes,
        showMessage: showMessage,
        addRecommendedAttribute: addRecommendedAttribute,
        performAttributeSearch: performAttributeSearch,
        updateDefaultValueField: updateDefaultValueField,
        resetDefaultValueField: resetDefaultValueField
    };

})(django.jQuery); 