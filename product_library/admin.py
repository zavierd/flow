from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.html import format_html


class ProductLibraryAdminSite(AdminSite):
    """自定义管理站点"""
    
    # 基本配置
    site_title = '整木定制产品库'
    site_header = '整木定制产品库管理系统'
    index_title = '管理面板'
    site_url = '/'
    
    # 登录模板
    login_template = 'admin/login.html'
    index_template = 'admin/custom_index.html'
    
    def __init__(self, name='admin'):
        super().__init__(name)
        
    def index(self, request, extra_context=None):
        """自定义首页"""
        if not request.user.is_authenticated:
            return redirect('admin:login')
            
        # 统计数据
        from products.models import Category, Brand, SPU, SKU
        
        stats = {
            'category_count': Category.objects.count(),
            'brand_count': Brand.objects.count(),
            'spu_count': SPU.objects.count(),
            'sku_count': SKU.objects.count(),
            'active_sku_count': SKU.objects.filter(status='active').count(),
            'low_stock_count': SKU.objects.filter(stock_quantity__lte=10).count(),
        }
        
        context = {
            'title': self.index_title,
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': self.site_url,
            'has_permission': True,
            'available_apps': self.get_app_list(request),
            'stats': stats,
        }
        
        if extra_context:
            context.update(extra_context)
            
        return render(request, self.index_template, context)
    
    def get_app_list(self, request, app_label=None):
        """重新组织应用列表"""
        app_list = super().get_app_list(request, app_label)
        
        # 重新组织菜单结构
        organized_apps = []
        
        # 1. 产品管理核心模块
        product_models = []
        auth_models = []
        
        for app in app_list:
            if app['app_label'] == 'products':
                # 分离产品管理和导入功能
                product_models = []
                import_models = []
                
                # 定义产品管理模型顺序
                product_model_order = [
                    'Category', 'Brand', 'Attribute', 'AttributeValue',
                    'SPU', 'SKU', 'SKUAttributeValue', 'SPUAttribute', 'ProductImage',
                    'ProductsPricingRule', 'ProductsDimension'
                ]
                
                # 定义导入功能模型
                import_model_names = ['ImportTask', 'ImportTemplate', 'ImportError']
                
                # 按预定义顺序排列产品管理模型
                for model_name in product_model_order:
                    for model in app['models']:
                        if model['object_name'] == model_name:
                            product_models.append(model)
                            break
                
                # 收集导入功能模型
                for model in app['models']:
                    if model['object_name'] in import_model_names:
                        import_models.append(model)
                
                # 创建产品管理应用
                if product_models:
                    product_app = {
                        'name': '📦 产品管理',
                        'app_label': 'products',
                        'app_url': app['app_url'],
                        'has_module_perms': app['has_module_perms'],
                        'models': product_models
                    }
                    organized_apps.append(product_app)
                
                # 创建导入功能应用
                if import_models:
                    import_app = {
                        'name': '📥 数据导入',
                        'app_label': 'products_import',
                        'app_url': app['app_url'],
                        'has_module_perms': app['has_module_perms'],
                        'models': import_models
                    }
                    organized_apps.append(import_app)
                
            elif app['app_label'] == 'auth':
                # 用户认证模块
                app['name'] = '👥 用户管理'
                organized_apps.append(app)
                
        return organized_apps


# 创建自定义管理站点实例
admin_site = ProductLibraryAdminSite(name='custom_admin')  # 修复：使用唯一的命名空间

# 重新注册所有模型到自定义站点
from products.admin import *
from products.models import (
    Category, Brand, Attribute, AttributeValue, SPU, SPUAttribute, SKU, SKUAttributeValue, 
    ProductImage, ProductsPricingRule, ProductsDimension, 
    ImportTask, ImportError, ImportTemplate
)

# 注册产品相关模型
admin_site.register(Category, CategoryAdmin)
admin_site.register(Brand, BrandAdmin)
admin_site.register(Attribute, AttributeAdmin)
admin_site.register(AttributeValue, AttributeValueAdmin)
admin_site.register(SPU, SPUAdmin)
admin_site.register(SPUAttribute, SPUAttributeAdmin)
admin_site.register(SKU, SKUAdmin)
admin_site.register(SKUAttributeValue, SKUAttributeValueAdmin)
admin_site.register(ProductImage, ProductImageAdmin)
admin_site.register(ProductsPricingRule, ProductsPricingRuleAdmin)
admin_site.register(ProductsDimension, ProductsDimensionAdmin)

# 注册导入功能模型
admin_site.register(ImportTask, ImportTaskAdmin)
admin_site.register(ImportError, ImportErrorAdmin)
admin_site.register(ImportTemplate, ImportTemplateAdmin)

# 注册用户认证模型（如果需要）
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin) 