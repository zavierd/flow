"""
Products Admin模块
将原本臃肿的admin.py文件拆分为多个专门的模块
"""

# 导入基础配置
from .base import *
from .filters import *
from .mixins import *

# 导入各个模型的Admin配置
from .category_admin import CategoryAdmin
from .brand_admin import BrandAdmin
from .attribute_admin import AttributeAdmin, AttributeValueAdmin
from .spu_admin import SPUAdmin, SPUAttributeAdmin, SPUDimensionTemplateAdmin
from .sku_admin import SKUAdmin, SKUAttributeValueAdmin
from .product_admin import ProductImageAdmin, ProductsPricingRuleAdmin, ProductsDimensionAdmin
from .import_admin import ImportTaskAdmin, ImportErrorAdmin, ImportTemplateAdmin

# 自定义 Admin 站点配置
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

admin.site.site_header = '整木定制产品库管理系统'
admin.site.site_title = '产品库管理'
admin.site.index_title = '产品数据管理'

# 添加自定义管理工具
class CustomAdminSite(admin.AdminSite):
    """自定义Admin站点，添加数据清理工具"""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-data-tool/', self.admin_view(self.clear_data_tool_view), name='clear_data_tool'),
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def clear_data_tool_view(self, request):
        """数据清理工具视图"""
        context = {
            'title': '产品数据清理工具',
            'site_header': self.site_header,
            'site_title': self.site_title,
            'has_permission': True,
        }
        return render(request, 'admin/clear_data_tool.html', context)

# 使用自定义Admin站点
# admin.site = CustomAdminSite(name='admin')