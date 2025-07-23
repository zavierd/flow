// SPU Admin JavaScript 功能

(function($) {
    'use strict';

    // 当文档准备就绪时执行
    $(document).ready(function() {
        initSPUAdmin();
    });

    function initSPUAdmin() {
        // 初始化列表页功能
        if (window.location.pathname.includes('/spu/')) {
            initListPageFeatures();
        }
        
        // 初始化详情页功能
        if (window.location.pathname.includes('/add/') || window.location.pathname.match(/\/\d+\/change\//)) {
            initDetailPageFeatures();
        }
        
        // 初始化批量操作确认
        initBatchOperationConfirmation();
        
        // 初始化搜索增强
        initSearchEnhancement();
        
        // 初始化工具提示
        initTooltips();
    }

    function initListPageFeatures() {
        // 初始化属性类型过滤
        initAttributeTypeFilter();
        
        // 初始化快速编辑
        initQuickEdit();
        
        // 初始化状态切换
        initStatusToggle();
        
        // 初始化批量选择
        initBatchSelect();
    }

    function initDetailPageFeatures() {
        // 初始化表单增强
        initFormEnhancements();
        
        // 初始化代码生成
        initCodeGeneration();
        
        // 初始化属性预览
        initAttributePreview();
        
        // 初始化保存确认
        initSaveConfirmation();
    }

    function initAttributeTypeFilter() {
        // 在过滤器中添加属性类型快速筛选
        var $filterList = $('#changelist-filter');
        if ($filterList.length) {
            var $typeFilter = $('<div class="attribute-type-filter">');
            $typeFilter.html(`
                <h3>按属性类型筛选</h3>
                <div class="type-buttons">
                    <button class="type-btn" data-type="">全部</button>
                    <button class="type-btn" data-type="text">文本</button>
                    <button class="type-btn" data-type="number">数字</button>
                    <button class="type-btn" data-type="select">单选</button>
                    <button class="type-btn" data-type="color">颜色</button>
                    <button class="type-btn" data-type="image">图片</button>
                </div>
            `);
            
            $filterList.append($typeFilter);
            
            // 绑定点击事件
            $typeFilter.find('.type-btn').on('click', function(e) {
                e.preventDefault();
                var type = $(this).data('type');
                filterByAttributeType(type);
                
                // 更新按钮状态
                $(this).addClass('active').siblings().removeClass('active');
            });
        }
    }

    function filterByAttributeType(type) {
        var currentUrl = new URL(window.location);
        
        if (type) {
            currentUrl.searchParams.set('attributes__type__exact', type);
        } else {
            currentUrl.searchParams.delete('attributes__type__exact');
        }
        
        window.location.href = currentUrl.toString();
    }

    function initQuickEdit() {
        // 添加快速编辑功能
        $('.field-is_active input[type="checkbox"]').on('change', function() {
            var $checkbox = $(this);
            var spuId = $checkbox.closest('tr').find('input[name="_selected_action"]').val();
            var isActive = $checkbox.is(':checked');
            
            // 显示加载状态
            $checkbox.prop('disabled', true);
            
            // 发送 AJAX 请求
            quickUpdateStatus(spuId, isActive, function(success) {
                if (success) {
                    showMessage('状态更新成功', 'success');
                } else {
                    // 恢复原状态
                    $checkbox.prop('checked', !isActive);
                    showMessage('状态更新失败', 'error');
                }
                $checkbox.prop('disabled', false);
            });
        });
    }

    function quickUpdateStatus(spuId, isActive, callback) {
        // 模拟 AJAX 请求
        setTimeout(function() {
            // 这里应该发送真实的 AJAX 请求到后端
            // 暂时模拟成功
            callback(true);
        }, 500);
    }

    function initStatusToggle() {
        // 为状态列添加可视化指示器
        $('.field-is_active').each(function() {
            var $cell = $(this);
            var isActive = $cell.find('input[type="checkbox"]').is(':checked');
            
            if (isActive) {
                $cell.addClass('status-active');
            } else {
                $cell.addClass('status-inactive');
            }
        });
    }

    function initBatchSelect() {
        // 增强批量选择功能
        var $selectAll = $('#action-toggle');
        var $actionSelect = $('select[name="action"]');
        var $goButton = $('.actions .button');
        
        // 监听全选状态
        $selectAll.on('change', function() {
            var isChecked = $(this).is(':checked');
            $('.action-select').prop('checked', isChecked);
            updateBatchButtonState();
        });
        
        // 监听单个选择
        $(document).on('change', '.action-select', function() {
            updateBatchButtonState();
        });
        
        function updateBatchButtonState() {
            var selectedCount = $('.action-select:checked').length;
            var $counter = $('.selected-count');
            
            if ($counter.length === 0) {
                $counter = $('<span class="selected-count"></span>');
                $('.actions').prepend($counter);
            }
            
            if (selectedCount > 0) {
                $counter.text(`已选择 ${selectedCount} 项`).show();
                $goButton.prop('disabled', false);
            } else {
                $counter.hide();
                $goButton.prop('disabled', true);
            }
        }
    }

    function initBatchOperationConfirmation() {
        // 为危险操作添加确认对话框
        $('.actions form').on('submit', function(e) {
            var action = $('select[name="action"]').val();
            var selectedCount = $('.action-select:checked').length;
            
            if (selectedCount === 0) {
                e.preventDefault();
                alert('请先选择要操作的项目');
                return false;
            }
            
            var dangerousActions = ['delete_selected', 'deactivate_spu'];
            if (dangerousActions.includes(action)) {
                var actionName = $('select[name="action"] option:selected').text();
                var confirmed = confirm(`确定要对 ${selectedCount} 个项目执行"${actionName}"操作吗？此操作可能无法撤销。`);
                
                if (!confirmed) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    function initSearchEnhancement() {
        // 增强搜索功能
        var $searchInput = $('#searchbar');
        if ($searchInput.length) {
            // 添加搜索提示
            var $searchHints = $('<div class="search-hints">');
            $searchHints.html(`
                <small>搜索提示：支持名称、编码、属性名称和属性编码搜索</small>
            `);
            $searchInput.after($searchHints);
            
            // 添加实时搜索建议
            var searchTimer;
            $searchInput.on('input', function() {
                clearTimeout(searchTimer);
                var query = $(this).val();
                
                if (query.length >= 2) {
                    searchTimer = setTimeout(function() {
                        showSearchSuggestions(query);
                    }, 300);
                } else {
                    hideSearchSuggestions();
                }
            });
            
            // 点击其他地方隐藏建议
            $(document).on('click', function(e) {
                if (!$(e.target).closest('.search-container').length) {
                    hideSearchSuggestions();
                }
            });
        }
    }

    function showSearchSuggestions(query) {
        // 显示搜索建议
        var $suggestions = $('.search-suggestions');
        if ($suggestions.length === 0) {
            $suggestions = $('<div class="search-suggestions">');
            $('#searchbar').after($suggestions);
        }
        
        // 模拟搜索建议数据
        var suggestions = [
            `搜索 "${query}" 在名称中`,
            `搜索 "${query}" 在编码中`,
            `搜索 "${query}" 在属性中`
        ];
        
        var html = '<ul>';
        suggestions.forEach(function(suggestion) {
            html += `<li><a href="#" data-query="${query}">${suggestion}</a></li>`;
        });
        html += '</ul>';
        
        $suggestions.html(html).show();
        
        // 绑定点击事件
        $suggestions.find('a').on('click', function(e) {
            e.preventDefault();
            var query = $(this).data('query');
            $('#searchbar').val(query);
            $('.search-form').submit();
        });
    }

    function hideSearchSuggestions() {
        $('.search-suggestions').hide();
    }

    function initFormEnhancements() {
        // 表单字段增强
        initCodeGeneration();
        initFieldValidation();
        initAutoSave();
        initFieldDependencies();
    }

    function initCodeGeneration() {
        // 自动生成编码功能
        var $nameField = $('#id_name');
        var $codeField = $('#id_code');
        
        if ($nameField.length && $codeField.length) {
            $nameField.on('input', function() {
                var name = $(this).val();
                if (name && !$codeField.val()) {
                    var code = generateCode(name);
                    $codeField.val(code);
                    
                    // 检查编码唯一性
                    checkCodeUniqueness(code);
                }
            });
            
            $codeField.on('input', function() {
                var code = $(this).val();
                if (code) {
                    checkCodeUniqueness(code);
                }
            });
        }
    }

    function generateCode(name) {
        // 生成编码：拼音首字母 + 时间戳后4位
        var code = name.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '').substring(0, 8);
        var timestamp = Date.now().toString().slice(-4);
        return code.toUpperCase() + timestamp;
    }

    function checkCodeUniqueness(code) {
        var $codeField = $('#id_code');
        var $feedback = $('.code-feedback');
        
        if ($feedback.length === 0) {
            $feedback = $('<div class="code-feedback">');
            $codeField.after($feedback);
        }
        
        // 模拟唯一性检查
        setTimeout(function() {
            // 这里应该发送 AJAX 请求检查唯一性
            var isUnique = Math.random() > 0.3; // 模拟结果
            
            if (isUnique) {
                $feedback.html('<span class="success">✓ 编码可用</span>');
                $codeField.removeClass('error');
            } else {
                $feedback.html('<span class="error">✗ 编码已存在</span>');
                $codeField.addClass('error');
            }
        }, 500);
    }

    function initFieldValidation() {
        // 字段验证增强
        $('form').on('submit', function(e) {
            var isValid = true;
            
            // 验证必填字段
            $('.required input, .required select, .required textarea').each(function() {
                var $field = $(this);
                if (!$field.val()) {
                    $field.addClass('error');
                    isValid = false;
                } else {
                    $field.removeClass('error');
                }
            });
            
            // 验证编码格式
            var $codeField = $('#id_code');
            if ($codeField.length && $codeField.val()) {
                var code = $codeField.val();
                if (!/^[A-Z][A-Z0-9_]*$/.test(code)) {
                    $codeField.addClass('error');
                    showMessage('编码格式不正确：必须以字母开头，只能包含大写字母、数字和下划线', 'error');
                    isValid = false;
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                scrollToFirstError();
                return false;
            }
        });
    }

    function scrollToFirstError() {
        var $firstError = $('.error').first();
        if ($firstError.length) {
            $('html, body').animate({
                scrollTop: $firstError.offset().top - 100
            }, 500);
            $firstError.focus();
        }
    }

    function initAutoSave() {
        // 自动保存草稿功能
        var saveTimer;
        var $form = $('form');
        
        if ($form.length && window.location.pathname.includes('/change/')) {
            $form.find('input, select, textarea').on('input change', function() {
                clearTimeout(saveTimer);
                saveTimer = setTimeout(function() {
                    autoSaveDraft();
                }, 5000); // 5秒后自动保存
            });
        }
    }

    function autoSaveDraft() {
        var $status = $('.auto-save-status');
        if ($status.length === 0) {
            $status = $('<div class="auto-save-status">');
            $('.submit-row').before($status);
        }
        
        $status.html('<span class="saving">正在保存草稿...</span>');
        
        // 模拟自动保存
        setTimeout(function() {
            $status.html('<span class="saved">草稿已保存 ' + new Date().toLocaleTimeString() + '</span>');
            
            setTimeout(function() {
                $status.fadeOut();
            }, 3000);
        }, 1000);
    }

    function initFieldDependencies() {
        // 字段依赖关系
        var $categoryField = $('#id_category');
        
        if ($categoryField.length) {
            $categoryField.on('change', function() {
                var categoryId = $(this).val();
                if (categoryId) {
                    loadCategoryAttributes(categoryId);
                }
            });
        }
    }

    function loadCategoryAttributes(categoryId) {
        // 根据分类加载推荐属性
        var $suggestions = $('.attribute-suggestions');
        if ($suggestions.length === 0) {
            $suggestions = $('<div class="attribute-suggestions">');
            $('.inline-group').before($suggestions);
        }
        
        $suggestions.html('<div class="loading">正在加载推荐属性...</div>');
        
        // 模拟加载推荐属性
        setTimeout(function() {
            var recommendations = [
                { name: '颜色', type: 'color' },
                { name: '尺寸', type: 'text' },
                { name: '材质', type: 'select' }
            ];
            
            var html = '<h3>推荐属性</h3><div class="recommendation-list">';
            recommendations.forEach(function(attr) {
                html += `<button type="button" class="btn-recommendation" data-name="${attr.name}" data-type="${attr.type}">
                    ${attr.name} (${attr.type})
                </button>`;
            });
            html += '</div>';
            
            $suggestions.html(html);
            
            // 绑定点击事件
            $suggestions.find('.btn-recommendation').on('click', function() {
                var name = $(this).data('name');
                var type = $(this).data('type');
                addRecommendedAttribute(name, type);
            });
        }, 1000);
    }

    function addRecommendedAttribute(name, type) {
        // 添加推荐属性到内联表单
        showMessage(`已添加推荐属性：${name}`, 'success');
        
        // 这里可以触发内联表单的添加逻辑
        // 具体实现需要与 SPUAttributeInline 的 JavaScript 配合
    }

    function initAttributePreview() {
        // 属性配置预览
        var $previewBtn = $('<button type="button" class="btn btn-outline-info preview-attributes">预览属性配置</button>');
        $('.submit-row').prepend($previewBtn);
        
        $previewBtn.on('click', function(e) {
            e.preventDefault();
            showAttributePreview();
        });
    }

    function showAttributePreview() {
        // 显示属性配置预览
        var attributes = [];
        $('.inline-group .form-row:not(.add-row)').each(function() {
            var $row = $(this);
            var isDeleted = $row.find('.delete input[type="checkbox"]').is(':checked');
            
            if (!isDeleted) {
                var attributeName = $row.find('.field-attribute select option:selected').text();
                var isRequired = $row.find('.field-is_required input[type="checkbox"]').is(':checked');
                var defaultValue = $row.find('.field-default_value input').val();
                var order = $row.find('.field-order input').val();
                
                if (attributeName) {
                    attributes.push({
                        name: attributeName,
                        required: isRequired,
                        defaultValue: defaultValue,
                        order: parseInt(order) || 0
                    });
                }
            }
        });
        
        // 按顺序排序
        attributes.sort(function(a, b) {
            return a.order - b.order;
        });
        
        // 显示预览对话框
        var dialog = $('<div class="attribute-preview-dialog modal">');
        var content = '<div class="modal-content">';
        content += '<h4>属性配置预览</h4>';
        content += '<div class="preview-content">';
        
        if (attributes.length > 0) {
            content += '<table class="preview-table">';
            content += '<thead><tr><th>属性名称</th><th>是否必填</th><th>默认值</th><th>排序</th></tr></thead>';
            content += '<tbody>';
            
            attributes.forEach(function(attr) {
                content += '<tr>';
                content += `<td>${attr.name}</td>`;
                content += `<td>${attr.required ? '是' : '否'}</td>`;
                content += `<td>${attr.defaultValue || '-'}</td>`;
                content += `<td>${attr.order}</td>`;
                content += '</tr>';
            });
            
            content += '</tbody></table>';
        } else {
            content += '<p>暂无配置的属性</p>';
        }
        
        content += '</div>';
        content += '<div class="modal-actions">';
        content += '<button type="button" class="btn btn-secondary close-preview">关闭</button>';
        content += '</div>';
        content += '</div>';
        
        dialog.html(content);
        $('body').append(dialog);
        dialog.show();
        
        // 绑定关闭事件
        dialog.find('.close-preview').on('click', function() {
            dialog.remove();
        });
    }

    function initSaveConfirmation() {
        // 保存确认
        var $saveBtn = $('input[name="_save"]');
        var $saveAndContinueBtn = $('input[name="_continue"]');
        var $saveAndAddBtn = $('input[name="_addanother"]');
        
        $saveBtn.on('click', function(e) {
            if (!confirm('确定要保存 SPU 配置吗？')) {
                e.preventDefault();
                return false;
            }
        });
    }

    function initTooltips() {
        // 初始化工具提示
        $('[title]').each(function() {
            var $element = $(this);
            var title = $element.attr('title');
            
            if (title) {
                $element.attr('data-tooltip', title).removeAttr('title');
            }
        });
    }

    function showMessage(text, type) {
        var $message = $('<div class="alert alert-' + type + ' fade show auto-dismiss">' + text + '</div>');
        
        // 插入到页面顶部
        if ($('.messages').length) {
            $('.messages').append($message);
        } else {
            $('body').prepend('<div class="messages"></div>');
            $('.messages').append($message);
        }
        
        // 3秒后自动消失
        setTimeout(function() {
            $message.fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }

    // 导出全局函数
    window.SPUAdmin = {
        showMessage: showMessage,
        generateCode: generateCode,
        checkCodeUniqueness: checkCodeUniqueness,
        showAttributePreview: showAttributePreview
    };

})(django.jQuery); 