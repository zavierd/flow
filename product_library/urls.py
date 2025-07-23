"""
URL configuration for product_library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from . import views
from .admin import admin_site
from products import views as product_views

urlpatterns = [
    # 健康检查
    path('health/', views.health_check, name='health_check'),
    
    # 产品相关页面路由
    path('products/', include('products.urls')),

    # API 接口 - 使用不同的命名空间避免冲突
    path('api/', include('products.urls', namespace='api')),
    
    # 导入功能 API - 使用独立的命名空间 (暂时禁用)
    # path('api/import/', include('products.urls.import_urls', namespace='import')),
    
    # 导入功能 Web 界面
    path('import/', TemplateView.as_view(template_name='import/import_page_simple.html'), name='import_page'),
    
    # 模板下载API
    path('api/import-templates/download_template/', product_views.download_template, name='download_template'),
    path('api/import-templates/', product_views.list_templates, name='list_templates'),
    
    # ============ AJAX端点统一配置 ============
    # 基础AJAX端点（推荐路径）
    path('ajax/spu/<int:spu_id>/attributes/', product_views.get_spu_attributes_ajax, name='ajax-spu-attributes'),
    path('ajax/attribute/<int:attribute_id>/values/', product_views.get_attribute_values_ajax, name='ajax-attribute-values'),
    
    # ============ URL重写：处理各种可能的路径组合 ============
    # 1. 处理来自admin页面的AJAX请求路径（/products/ajax/...）
    path('products/ajax/spu/<int:spu_id>/attributes/', product_views.get_spu_attributes_ajax, name='ajax-spu-attributes-products'),
    path('products/ajax/attribute/<int:attribute_id>/values/', product_views.get_attribute_values_ajax, name='ajax-attribute-values-products'),
    
    # 2. 处理从admin内部来的AJAX请求路径（/admin/products/ajax/...）
    path('admin/products/ajax/spu/<int:spu_id>/attributes/', product_views.get_spu_attributes_ajax, name='ajax-spu-attributes-admin'),
    path('admin/products/ajax/attribute/<int:attribute_id>/values/', product_views.get_attribute_values_ajax, name='ajax-attribute-values-admin'),
    
    # 3. 处理其他可能的admin路径变体
    # 分类属性推荐（如果这些端点存在的话）
    # path('admin/products/ajax/category-attributes/<int:category_id>/', product_views.get_category_attributes_ajax, name='ajax-category-attributes-admin'),
    # path('products/ajax/category-attributes/<int:category_id>/', product_views.get_category_attributes_ajax, name='ajax-category-attributes-products'),
    # path('ajax/category-attributes/<int:category_id>/', product_views.get_category_attributes_ajax, name='ajax-category-attributes'),
    
    # 属性API端点（如果存在的话）
    # path('admin/products/ajax/attribute-api/', product_views.attribute_api_ajax, name='ajax-attribute-api-admin'),
    # path('products/ajax/attribute-api/', product_views.attribute_api_ajax, name='ajax-attribute-api-products'),
    # path('ajax/attribute-api/', product_views.attribute_api_ajax, name='ajax-attribute-api'),
    
    # 4. 兼容性路径：处理旧版本的属性值端点格式
    path('admin/products/ajax/attribute-values/<int:attribute_id>/', product_views.get_attribute_values_ajax, name='ajax-attribute-values-legacy-admin'),
    path('products/ajax/attribute-values/<int:attribute_id>/', product_views.get_attribute_values_ajax, name='ajax-attribute-values-legacy-products'),
    path('ajax/attribute-values/<int:attribute_id>/', product_views.get_attribute_values_ajax, name='ajax-attribute-values-legacy'),
    
    # ============ 管理后台与应用路由 ============
    # 数据清理工具（在admin路径下）
    path('admin/clear-data-tool/', product_views.clear_data_tool_view, name='clear_data_tool'),

    # 独立的清理工具页面
    path('clear-data/', TemplateView.as_view(template_name='clear_data.html'), name='clear_data_page'),

    # Django 管理后台 - 使用自定义admin站点
    path('admin/', admin_site.urls),
    
    # 首页重定向到管理界面
    path('', lambda request: redirect('/admin/'), name='home'),
    path('pricing-calculator/', views.dynamic_pricing_calculator, name='dynamic_pricing_calculator'),
    path('api/sku-search/', views.dynamic_pricing_calculator, name='sku_search'),
]

# 开发环境下的静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
