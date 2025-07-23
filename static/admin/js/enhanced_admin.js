// Enhanced Django Admin JavaScript

(function($) {
    'use strict';

    // 页面加载完成后初始化
    $(document).ready(function() {
        initEnhancedAdmin();
    });

    function initEnhancedAdmin() {
        // 初始化各种功能
        initLoadingStates();
        initTooltips();
        initQuickActions();
        initBulkActions();
        initImagePreviews();
        initSmartSearch();
        initTableEnhancements();
        initFormValidation();
        initKeyboardShortcuts();
    }

    // 加载状态管理
    function initLoadingStates() {
        // 为按钮添加加载状态
        $('input[type="submit"], .button').on('click', function() {
            var $btn = $(this);
            if (!$btn.hasClass('loading')) {
                $btn.addClass('loading').prop('disabled', true);
                
                // 3秒后移除加载状态（防止卡死）
                setTimeout(function() {
                    $btn.removeClass('loading').prop('disabled', false);
                }, 3000);
            }
        });

        // AJAX请求加载状态
        $(document).ajaxStart(function() {
            $('#content').addClass('loading');
        }).ajaxStop(function() {
            $('#content').removeClass('loading');
        });
    }

    // 增强型工具提示 - 支持悬停和点击
    function initTooltips() {
        // 为带有title属性的元素添加增强的工具提示
        $('[title]').each(function() {
            var $this = $(this);
            var title = $this.attr('title');
            $this.attr('data-tooltip', title).removeAttr('title').addClass('tooltip');
        });

        // 悬停显示tooltip
        $(document).on('mouseenter', '.tooltip', function() {
            var $this = $(this);
            var tooltip = $this.attr('data-tooltip');
            if (tooltip) {
                showTooltip($this, tooltip);
            }
        });

        // 悬停离开隐藏tooltip (只在没有被点击固定时)
        $(document).on('mouseleave', '.tooltip', function() {
            var $this = $(this);
            if (!$this.hasClass('tooltip-pinned')) {
                hideTooltip($this);
            }
        });

        // 点击切换tooltip（固定/取消固定）
        $(document).on('click', '.tooltip', function(e) {
            var $this = $(this);
            var tooltip = $this.attr('data-tooltip');
            
            if ($this.hasClass('tooltip-pinned')) {
                // 如果已经固定，则取消固定
                $this.removeClass('tooltip-pinned');
                hideTooltip($this);
            } else {
                // 先隐藏其他所有固定的tooltip
                $('.tooltip-pinned').removeClass('tooltip-pinned');
                $('.tooltip-content').remove();
                
                // 固定当前tooltip
                $this.addClass('tooltip-pinned');
                if (tooltip) {
                    showTooltip($this, tooltip);
                }
            }
            
            // 阻止事件冒泡，避免触发其他点击事件
            e.stopPropagation();
        });

        // 点击页面其他地方时取消所有固定的tooltip
        $(document).on('click', function(e) {
            if (!$(e.target).hasClass('tooltip') && !$(e.target).closest('.tooltip-content').length) {
                $('.tooltip-pinned').removeClass('tooltip-pinned');
                $('.tooltip-content').remove();
            }
        });
    }

    // 显示tooltip
    function showTooltip($element, text) {
        // 移除已存在的tooltip
        hideTooltip($element);
        
        var $tooltip = $('<div class="tooltip-content">' + text + '</div>');
        $('body').append($tooltip);
        
        var offset = $element.offset();
        var elementHeight = $element.outerHeight();
        var elementWidth = $element.outerWidth();
        var tooltipWidth = $tooltip.outerWidth();
        var tooltipHeight = $tooltip.outerHeight();
        
        // 计算最佳位置（优先显示在上方）
        var top = offset.top - tooltipHeight - 8;
        var left = offset.left + (elementWidth / 2) - (tooltipWidth / 2);
        
        // 如果上方空间不够，显示在下方
        if (top < $(window).scrollTop()) {
            top = offset.top + elementHeight + 8;
            $tooltip.addClass('tooltip-below');
        } else {
            $tooltip.addClass('tooltip-above');
        }
        
        // 确保tooltip不超出屏幕边界
        var windowWidth = $(window).width();
        if (left < 10) {
            left = 10;
        } else if (left + tooltipWidth > windowWidth - 10) {
            left = windowWidth - tooltipWidth - 10;
        }
        
        $tooltip.css({
            top: top,
            left: left
        }).fadeIn(200);
        
        // 存储引用以便清理
        $element.data('active-tooltip', $tooltip);
    }

    // 隐藏tooltip
    function hideTooltip($element) {
        var $tooltip = $element.data('active-tooltip');
        if ($tooltip) {
            $tooltip.fadeOut(200, function() {
                $tooltip.remove();
            });
            $element.removeData('active-tooltip');
        }
    }

    // 快速操作
    function initQuickActions() {
        // 快速激活/停用切换
        $('.quick-toggle').on('click', function(e) {
            e.preventDefault();
            var $this = $(this);
            var url = $this.data('url');
            var field = $this.data('field');
            
            $.post(url, {
                field: field,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            }).done(function(data) {
                if (data.success) {
                    location.reload();
                } else {
                    alert('操作失败：' + data.message);
                }
            }).fail(function() {
                alert('网络错误，请重试');
            });
        });
    }

    // 批量操作增强
    function initBulkActions() {
        // 全选功能增强
        $('#action-toggle').on('change', function() {
            var checked = this.checked;
            $('.action-select').prop('checked', checked);
            updateBulkActionBar();
        });

        $('.action-select').on('change', function() {
            updateBulkActionBar();
        });

        function updateBulkActionBar() {
            var selectedCount = $('.action-select:checked').length;
            var $bar = $('.actions');
            
            if (selectedCount > 0) {
                $bar.addClass('has-selection');
                $bar.find('.selection-count').text('已选择 ' + selectedCount + ' 项');
            } else {
                $bar.removeClass('has-selection');
            }
        }
    }

    // 图片预览功能
    function initImagePreviews() {
        // 为文件输入添加预览功能
        $('input[type="file"]').on('change', function() {
            var file = this.files[0];
            var $preview = $(this).siblings('.image-preview');
            
            if (file && file.type.startsWith('image/')) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    if ($preview.length === 0) {
                        $preview = $('<div class="image-preview"></div>');
                        $(this).after($preview);
                    }
                    $preview.html('<img src="' + e.target.result + '" style="max-width: 200px; max-height: 200px; border-radius: 4px; margin-top: 10px;">');
                }.bind(this);
                reader.readAsDataURL(file);
            }
        });
    }

    // 智能搜索
    function initSmartSearch() {
        var $searchInput = $('#searchbar');
        if ($searchInput.length) {
            var searchTimeout;
            
            $searchInput.on('input', function() {
                clearTimeout(searchTimeout);
                var query = $(this).val();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(function() {
                        performSmartSearch(query);
                    }, 300);
                }
            });
        }

        function performSmartSearch(query) {
            // 高亮搜索词
            highlightSearchTerms(query);
        }

        function highlightSearchTerms(query) {
            var terms = query.split(/\s+/);
            terms.forEach(function(term) {
                if (term.length >= 2) {
                    $('#result_list tbody tr').each(function() {
                        var $row = $(this);
                        var text = $row.text();
                        if (text.toLowerCase().indexOf(term.toLowerCase()) !== -1) {
                            $row.addClass('search-match');
                        } else {
                            $row.removeClass('search-match');
                        }
                    });
                }
            });
        }
    }

    // 表格增强
    function initTableEnhancements() {
        // 表格行悬停效果增强
        $('#result_list tbody tr').hover(
            function() {
                $(this).addClass('hover');
            },
            function() {
                $(this).removeClass('hover');
            }
        );

        // 表格排序增强
        $('.sortable').on('click', function() {
            var $this = $(this);
            $this.siblings().removeClass('sorted ascending descending');
            
            if ($this.hasClass('sorted ascending')) {
                $this.removeClass('ascending').addClass('descending');
            } else {
                $this.removeClass('descending').addClass('sorted ascending');
            }
        });

        // 可调整列宽
        initResizableColumns();
    }

    function initResizableColumns() {
        $('#result_list th').each(function() {
            var $th = $(this);
            var $resizer = $('<div class="column-resizer"></div>');
            $th.append($resizer);
            
            $resizer.on('mousedown', function(e) {
                var startX = e.pageX;
                var startWidth = $th.width();
                
                $(document).on('mousemove.resize', function(e) {
                    var newWidth = startWidth + (e.pageX - startX);
                    $th.css('width', Math.max(50, newWidth) + 'px');
                });
                
                $(document).on('mouseup.resize', function() {
                    $(document).off('.resize');
                });
                
                e.preventDefault();
            });
        });
    }

    // 表单验证增强
    function initFormValidation() {
        // 实时验证
        $('form input, form select, form textarea').on('blur', function() {
            validateField($(this));
        });

        function validateField($field) {
            var value = $field.val();
            var fieldType = $field.attr('type');
            var required = $field.prop('required');
            var $errorMsg = $field.siblings('.field-error');

            // 移除现有错误消息
            $errorMsg.remove();
            $field.removeClass('error');

            // 必填验证
            if (required && !value) {
                showFieldError($field, '此字段为必填项');
                return false;
            }

            // 邮箱验证
            if (fieldType === 'email' && value) {
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    showFieldError($field, '请输入有效的邮箱地址');
                    return false;
                }
            }

            // URL验证
            if (fieldType === 'url' && value) {
                var urlRegex = /^https?:\/\/.+/;
                if (!urlRegex.test(value)) {
                    showFieldError($field, '请输入有效的URL（包含http://或https://）');
                    return false;
                }
            }

            return true;
        }

        function showFieldError($field, message) {
            $field.addClass('error');
            var $error = $('<div class="field-error" style="color: #dc3545; font-size: 12px; margin-top: 5px;">' + message + '</div>');
            $field.after($error);
        }
    }

    // 键盘快捷键
    function initKeyboardShortcuts() {
        $(document).on('keydown', function(e) {
            // Ctrl+S 保存
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                $('input[type="submit"][name="_save"]').click();
            }
            
            // Ctrl+Enter 保存并继续编辑
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                $('input[type="submit"][name="_continue"]').click();
            }
            
            // Escape 取消
            if (e.key === 'Escape') {
                var $cancel = $('.cancel-link, [href*="changelist"]');
                if ($cancel.length) {
                    window.location.href = $cancel.attr('href');
                }
            }
        });
    }

    // 数据统计图表
    function initCharts() {
        // 简单的统计图表
        $('.stats-chart').each(function() {
            var $chart = $(this);
            var data = JSON.parse($chart.attr('data-chart'));
            
            // 这里可以集成Chart.js或其他图表库
            renderSimpleChart($chart, data);
        });
    }

    function renderSimpleChart($container, data) {
        // 简单的柱状图实现
        var max = Math.max.apply(Math, data.values);
        var html = '<div class="simple-chart">';
        
        data.labels.forEach(function(label, i) {
            var height = (data.values[i] / max) * 100;
            html += '<div class="chart-bar">';
            html += '<div class="bar" style="height: ' + height + '%"></div>';
            html += '<div class="label">' + label + '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        $container.html(html);
    }

    // 通知系统
    function showNotification(message, type) {
        type = type || 'info';
        var $notification = $('<div class="notification notification-' + type + '">' + message + '</div>');
        
        $('body').append($notification);
        
        setTimeout(function() {
            $notification.addClass('show');
        }, 100);
        
        setTimeout(function() {
            $notification.removeClass('show');
            setTimeout(function() {
                $notification.remove();
            }, 300);
        }, 3000);
    }

    // 导出全局函数
    window.enhancedAdmin = {
        showNotification: showNotification,
        validateField: function($field) {
            return initFormValidation.validateField($field);
        }
    };

})(django.jQuery);

// 页面性能监控
(function() {
    'use strict';
    
    // 监控页面加载时间
    window.addEventListener('load', function() {
        var loadTime = performance.now();
        console.log('页面加载时间: ' + Math.round(loadTime) + 'ms');
        
        // 如果加载时间超过3秒，显示优化建议
        if (loadTime > 3000) {
            setTimeout(function() {
                if (window.enhancedAdmin) {
                    window.enhancedAdmin.showNotification(
                        '页面加载较慢，建议优化查询或启用缓存',
                        'warning'
                    );
                }
            }, 1000);
        }
    });
    
    // 监控内存使用
    if (performance.memory) {
        setInterval(function() {
            var memory = performance.memory;
            var used = Math.round(memory.usedJSHeapSize / 1048576);
            var total = Math.round(memory.totalJSHeapSize / 1048576);
            
            if (used / total > 0.9) {
                console.warn('内存使用率较高: ' + Math.round(used/total*100) + '%');
            }
        }, 30000);
    }
})(); 