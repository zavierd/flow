from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'attributes', views.AttributeViewSet, basename='attribute')
router.register(r'spus', views.SPUViewSet, basename='spu')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'filters', views.FilterViewSet, basename='filter')

app_name = 'products'

urlpatterns = [
    # API 路由 - REST framework路由
    path('', include(router.urls)),
    
    # Ajax API 路由 - 用于Admin界面
    path('ajax/spu/<int:spu_id>/attributes/', views.get_spu_attributes_ajax, name='spu_attributes_ajax'),
    path('ajax/attribute/<int:attribute_id>/values/', views.get_attribute_values_ajax, name='attribute_values_ajax'),
    path('ajax/sku/<int:sku_id>/config/', views.sku_config_ajax, name='sku_config_ajax'),
    
    # Admin专用API路由
    path('admin/attribute/<int:attribute_id>/values/', views.attribute_values_api, name='admin_attribute_values'),
    path('admin/attributes/', views.AttributeAPIView.as_view(), name='admin_attributes'),
    path('admin/category/<int:category_id>/attributes/', views.CategoryAttributesAPIView.as_view(), name='admin_category_attributes'),
    path('admin/clear-cache/', views.clear_attribute_cache, name='admin_clear_cache'),
    
    # 动态价格计算API路由
    path('api/pricing/calculate/', views.calculate_dynamic_price, name='calculate_dynamic_price'),
    
    # 获取SKU尺寸信息
    path('api/sku/<int:sku_id>/dimensions/', views.get_sku_dimensions, name='get_sku_dimensions'),
    
    # 获取SPU的加价规则
    path('api/spu/<int:spu_id>/pricing-rules/', views.get_pricing_rules, name='get_spu_pricing_rules'),
    
    # 获取SPU下的SKU列表（管理界面用）
    path('api/sku-by-spu/', views.get_sku_by_spu, name='get_sku_by_spu'),
    
    # 获取SPU的尺寸模板（SKU同步用）
    path('api/spu-dimension-templates/', views.get_spu_dimension_templates, name='get_spu_dimension_templates'),

    # Royana模板下载
    path('royana/template/download/', views.download_template, name='download_royana_template'),

    # AI数据格式导入
    path('ai-data/import/', views.import_ai_data, name='import_ai_data'),
    path('ai-data/template/download/', views.download_ai_template, name='download_ai_template'),
    path('debug-paste/', views.debug_paste_view, name='debug_paste'),

    # 数据清理API
    path('admin/clear-data/', views.clear_product_data_api, name='clear_product_data_api'),
    path('admin/data-summary/', views.get_data_summary_api, name='get_data_summary_api'),

    # 数据清理工具页面
    path('admin/clear-data-tool/', views.clear_data_tool_view, name='clear_data_tool'),
]