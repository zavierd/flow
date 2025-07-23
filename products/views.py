from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max, Count, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Q, Min, Max, Count, Prefetch
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import json
import logging

from .models import Category, Brand, Attribute, AttributeValue, SPU, SKU, SPUAttribute
from .serializers import (
    CategorySerializer, BrandSerializer, AttributeSerializer, 
    SPUSerializer, SKUListSerializer, SKUDetailSerializer, FilterSerializer
)

logger = logging.getLogger(__name__)

# 开发环境缓存装饰器 - 禁用缓存
def dev_cache_page(timeout):
    """开发环境禁用缓存的装饰器"""
    def decorator(func):
        if settings.DEBUG:
            # 开发环境直接返回原函数，不缓存
            return func
        else:
            # 生产环境使用正常缓存
            return cache_page(timeout)(func)
    return decorator

# 开发环境缓存helper函数
def get_cache(key, default=None):
    """开发环境禁用缓存的get方法"""
    if settings.DEBUG:
        return default
    return cache.get(key, default)

def set_cache(key, value, timeout):
    """开发环境禁用缓存的set方法"""
    if not settings.DEBUG:
        cache.set(key, value, timeout)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """分类API视图集"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'name', 'created_at', 'level']
    ordering = ['order', 'name']
    
    @method_decorator(dev_cache_page(60 * 15))  # 开发环境禁用缓存
    def list(self, request, *args, **kwargs):
        """获取分类列表 - 支持层级展示"""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        
        # 检查是否有 parent 参数
        parent_id = self.request.query_params.get('parent', None)
        if parent_id is not None:
            if parent_id == 'null' or parent_id == '':
                # 返回顶级分类 (level=0)
                queryset = queryset.filter(level=0)
            else:
                # 返回指定父分类的子分类
                queryset = queryset.filter(parent_id=parent_id)
        else:
            # 默认返回顶级分类 (level=0)
            queryset = queryset.filter(level=0)
        
        return queryset.select_related('parent').prefetch_related('children')
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取完整的分类树"""
        categories = Category.objects.filter(is_active=True, level=0)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_levels(self, request):
        """获取所有层级的分类 - 按层级和排序字段排序"""
        queryset = Category.objects.filter(is_active=True).order_by('level', 'order', 'name')
        
        # 支持层级筛选
        level = request.query_params.get('level', None)
        if level is not None:
            try:
                level = int(level)
                queryset = queryset.filter(level=level)
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取指定分类的直接子分类"""
        try:
            category = self.get_object()
            children = category.get_children().filter(is_active=True).order_by('order', 'name')
            serializer = self.get_serializer(children, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        """获取指定分类的祖先分类"""
        try:
            category = self.get_object()
            ancestors = category.get_ancestors(include_self=False)
            serializer = self.get_serializer(ancestors, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def descendants(self, request, pk=None):
        """获取指定分类的所有后代分类"""
        try:
            category = self.get_object()
            descendants = category.get_descendants().filter(is_active=True).order_by('level', 'order', 'name')
            
            page = self.paginate_queryset(descendants)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(descendants, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """品牌API视图集"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @method_decorator(dev_cache_page(60 * 15))  # 开发环境禁用缓存
    def list(self, request, *args, **kwargs):
        """获取品牌列表"""
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """自定义查询集"""
        return super().get_queryset().select_related()


class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    """属性API视图集"""
    queryset = Attribute.objects.filter(is_active=True)
    serializer_class = AttributeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        
        # 支持筛选可筛选的属性
        filterable_only = self.request.query_params.get('filterable_only', None)
        if filterable_only == 'true':
            queryset = queryset.filter(is_filterable=True)
        
        return queryset.prefetch_related('values')


class SPUViewSet(viewsets.ReadOnlyModelViewSet):
    """SPU API视图集"""
    queryset = SPU.objects.filter(is_active=True)
    serializer_class = SPUSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """自定义查询集"""
        return super().get_queryset().select_related('category').prefetch_related(
            'spuattribute_set__attribute'
        )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """产品API视图集 - 主要的产品查询接口"""
    queryset = SKU.objects.filter(status='active')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'spu__category', 'status', 'is_featured']
    search_fields = ['name', 'code', 'description', 'selling_points', 'tags']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """根据action返回不同的序列化器"""
        if self.action == 'list':
            return SKUListSerializer
        return SKUDetailSerializer
    
    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        
        # 价格范围筛选
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # 库存筛选
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        elif in_stock == 'false':
            queryset = queryset.filter(stock_quantity=0)
        
        # 分类筛选（支持子分类）
        category_id = self.request.query_params.get('category', None)
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                # 获取该分类及其所有子分类
                def get_child_categories(parent_category):
                    """递归获取所有子分类ID"""
                    child_ids = [parent_category.id]
                    for child in parent_category.get_children():
                        child_ids.extend(get_child_categories(child))
                    return child_ids
                
                category_ids = get_child_categories(category)
                queryset = queryset.filter(spu__category_id__in=category_ids)
            except Category.DoesNotExist:
                pass
        
        # 属性筛选
        for key, value in self.request.query_params.items():
            if key.startswith('attr_') and value:
                attr_code = key[5:]  # 去掉 'attr_' 前缀
                queryset = queryset.filter(
                    sku_attribute_values__attribute__code=attr_code,
                    sku_attribute_values__custom_value=value
                ).distinct()
        
        return queryset.select_related('brand', 'spu__category').prefetch_related('images')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """获取推荐产品"""
        queryset = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最新产品"""
        queryset = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """高级搜索"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 构建搜索查询
        search_query = Q(name__icontains=query) | \
                      Q(code__icontains=query) | \
                      Q(description__icontains=query) | \
                      Q(selling_points__icontains=query) | \
                      Q(tags__icontains=query) | \
                      Q(spu__name__icontains=query) | \
                      Q(brand__name__icontains=query)
        
        queryset = self.get_queryset().filter(search_query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FilterViewSet(viewsets.ViewSet):
    """筛选器API视图集"""
    permission_classes = [AllowAny]
    
    @method_decorator(dev_cache_page(60 * 30))  # 开发环境禁用缓存
    def list(self, request):
        """获取筛选器数据"""
        data = {
            'categories': Category.objects.filter(is_active=True, level=0),
            'brands': Brand.objects.filter(is_active=True),
            'attributes': Attribute.objects.filter(is_active=True, is_filterable=True),
            'price_range': {
                'min': SKU.objects.filter(status='active').aggregate(Min('price'))['price__min'] or 0,
                'max': SKU.objects.filter(status='active').aggregate(Max('price'))['price__max'] or 0,
            },
            'status_choices': [
                {'value': 'active', 'label': '在售'},
                {'value': 'inactive', 'label': '停售'},
                {'value': 'draft', 'label': '草稿'},
            ]
        }
        
        serializer = FilterSerializer(data)
        return Response(serializer.data)


class AttributeAPIView(View):
    """属性相关 API 视图"""
    
    @method_decorator(staff_member_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """获取属性列表"""
        try:
            # 获取查询参数
            category_id = request.GET.get('category_id')
            attribute_type = request.GET.get('type')
            search = request.GET.get('search', '').strip()
            exclude_spu = request.GET.get('exclude_spu')  # 排除已关联的SPU
            only_filterable = request.GET.get('only_filterable') == 'true'
            
            # 安全处理 limit 参数
            try:
                limit = int(request.GET.get('limit', 50))
                limit = max(1, min(limit, 100))  # 确保在 1-100 范围内
            except (ValueError, TypeError):
                limit = 50
            
            # 构建缓存键
            cache_key = f"attributes_api_{category_id}_{attribute_type}_{search}_{exclude_spu}_{only_filterable}_{limit}"
            
            # 尝试从缓存获取
            cached_result = get_cache(cache_key)
            if cached_result:
                return JsonResponse(cached_result)
            
            # 构建查询
            queryset = Attribute.objects.filter(is_active=True)
            
            # 按分类筛选 - 根据该分类下SPU常用的属性
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    # 获取该分类及其子分类下所有SPU使用的属性
                    related_categories = category.get_descendants(include_self=True)
                    spu_attributes = SPUAttribute.objects.filter(
                        spu__category__in=related_categories
                    ).values_list('attribute_id', flat=True).distinct()
                    
                    if spu_attributes:
                        # 优先显示该分类常用的属性，然后是其他属性
                        queryset = queryset.extra(
                            select={
                                'is_category_common': f'CASE WHEN products_attribute.id IN ({",".join(map(str, spu_attributes))}) THEN 1 ELSE 0 END'
                            },
                            order_by=['-is_category_common', 'order', 'name']
                        )
                except Category.DoesNotExist:
                    pass
            
            # 按属性类型筛选
            if attribute_type:
                queryset = queryset.filter(type=attribute_type)
            
            # 搜索筛选
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # 只显示可筛选的属性
            if only_filterable:
                queryset = queryset.filter(is_filterable=True)
            
            # 排除已关联的SPU的属性
            if exclude_spu:
                try:
                    existing_attrs = SPUAttribute.objects.filter(
                        spu_id=exclude_spu
                    ).values_list('attribute_id', flat=True)
                    queryset = queryset.exclude(id__in=existing_attrs)
                except (ValueError, TypeError):
                    pass
            
            # 预加载属性值（只加载前几个用于预览）
            queryset = queryset.prefetch_related(
                Prefetch(
                    'values',
                    queryset=AttributeValue.objects.filter(is_active=True).order_by('order', 'value')[:5],
                    to_attr='preview_values'
                )
            ).annotate(
                values_count=Count('values', filter=Q(values__is_active=True))
            )
            
            # 应用排序和限制
            if not category_id:  # 如果没有按分类排序，使用默认排序
                queryset = queryset.order_by('order', 'name')
            
            queryset = queryset[:limit]
            
            # 构建返回数据
            attributes_data = []
            for attr in queryset:
                # 属性基本信息
                attr_data = {
                    'id': attr.id,
                    'name': attr.name,
                    'code': attr.code,
                    'type': attr.type,
                    'type_display': attr.get_type_display(),
                    'unit': attr.unit or '',
                    'description': attr.description or '',
                    'is_required': attr.is_required,
                    'is_filterable': attr.is_filterable,
                    'order': attr.order,
                    'values_count': attr.values_count,
                    'display_label': self._format_attribute_label(attr),
                }
                
                # 属性值预览
                if hasattr(attr, 'preview_values'):
                    preview_values = []
                    for value in attr.preview_values:
                        value_data = {
                            'id': value.id,
                            'value': value.value,
                            'display_name': value.display_name or value.value,
                        }
                        
                        # 根据属性类型添加特殊字段
                        if attr.type == 'color' and value.color_code:
                            value_data['color_code'] = value.color_code
                        elif attr.type == 'image' and value.image:
                            value_data['image_url'] = value.image.url
                        
                        preview_values.append(value_data)
                    
                    attr_data['preview_values'] = preview_values
                    attr_data['has_more_values'] = attr.values_count > 5
                
                # 如果有分类关联度信息，添加到返回数据中
                if hasattr(attr, 'is_category_common'):
                    attr_data['is_category_common'] = bool(attr.is_category_common)
                
                attributes_data.append(attr_data)
            
            # 构建响应数据
            response_data = {
                'success': True,
                'data': attributes_data,
                'count': len(attributes_data),
                'has_more': len(attributes_data) == limit,  # 是否还有更多数据
                'filters': {
                    'category_id': category_id,
                    'type': attribute_type,
                    'search': search,
                    'exclude_spu': exclude_spu,
                    'only_filterable': only_filterable,
                }
            }
            
            # 缓存结果（缓存5分钟）
            set_cache(cache_key, response_data, 300)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"获取属性列表时发生错误: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '获取属性列表失败',
                'message': str(e) if request.user.is_superuser else '服务器内部错误'
            }, status=500)
    
    def _format_attribute_label(self, attr):
        """格式化属性标签用于显示"""
        label_parts = [attr.name]
        
        # 添加类型标识
        type_display = attr.get_type_display()
        label_parts.append(f"[{type_display}]")
        
        # 添加单位
        if attr.unit:
            label_parts.append(f"({attr.unit})")
        
        # 添加编码
        label_parts.append(f"- {attr.code}")
        
        return " ".join(label_parts)


class CategoryAttributesAPIView(View):
    """分类属性推荐 API"""
    
    @method_decorator(staff_member_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, category_id):
        """获取特定分类的推荐属性"""
        try:
            # 构建缓存键
            cache_key = f"category_attributes_recommendations_{category_id}"
            cached_result = get_cache(cache_key)
            if cached_result:
                return JsonResponse(cached_result)
            
            try:
                category = Category.objects.get(id=category_id, is_active=True)
            except Category.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '分类不存在或已停用'
                }, status=404)
            
            # 获取该分类及其子分类
            related_categories = category.get_descendants(include_self=True)
            
            # 统计该分类下SPU使用的属性频率
            attribute_usage = SPUAttribute.objects.filter(
                spu__category__in=related_categories,
                spu__is_active=True,
                attribute__is_active=True
            ).values(
                'attribute_id',
                'attribute__name',
                'attribute__code',
                'attribute__type',
                'attribute__unit',
                'attribute__description',
                'attribute__order'
            ).annotate(
                usage_count=Count('spu', distinct=True),
                usage_percentage=Count('spu', distinct=True) * 100.0 / Count('spu__category', distinct=True)
            ).order_by('-usage_count', 'attribute__order', 'attribute__name')[:20]  # 取前20个最常用的
            
            # 构建推荐数据
            recommendations = []
            for item in attribute_usage:
                rec_data = {
                    'attribute_id': item['attribute_id'],
                    'name': item['attribute__name'],
                    'code': item['attribute__code'],
                    'type': item['attribute__type'],
                    'type_display': dict(Attribute.ATTRIBUTE_TYPES).get(item['attribute__type'], item['attribute__type']),
                    'unit': item['attribute__unit'] or '',
                    'description': item['attribute__description'] or '',
                    'order': item['attribute__order'],
                    'usage_count': item['usage_count'],
                    'usage_percentage': round(item['usage_percentage'], 1),
                    'recommendation_level': self._get_recommendation_level(item['usage_percentage'])
                }
                recommendations.append(rec_data)
            
            # 获取该分类的总SPU数量
            total_spus = SPU.objects.filter(
                category__in=related_categories,
                is_active=True
            ).count()
            
            response_data = {
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'full_path': category.get_full_path(),
                },
                'total_spus': total_spus,
                'recommendations': recommendations,
                'count': len(recommendations)
            }
            
            # 缓存结果（缓存10分钟）
            set_cache(cache_key, response_data, 600)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"获取分类属性推荐时发生错误: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '获取推荐属性失败',
                'message': str(e) if request.user.is_superuser else '服务器内部错误'
            }, status=500)
    
    def _get_recommendation_level(self, usage_percentage):
        """根据使用率确定推荐级别"""
        if usage_percentage >= 80:
            return 'high'  # 强烈推荐
        elif usage_percentage >= 50:
            return 'medium'  # 推荐
        elif usage_percentage >= 20:
            return 'low'  # 可选
        else:
            return 'optional'  # 备选


@staff_member_required
@require_http_methods(["GET"])
def attribute_values_api(request, attribute_id):
    """获取指定属性的所有属性值"""
    try:
        # 构建缓存键
        cache_key = f"attribute_values_{attribute_id}"
        cached_result = get_cache(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        try:
            attribute = Attribute.objects.get(id=attribute_id, is_active=True)
        except Attribute.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '属性不存在或已停用'
            }, status=404)
        
        # 获取属性值
        values = AttributeValue.objects.filter(
            attribute=attribute,
            is_active=True
        ).order_by('order', 'value')
        
        # 构建属性值数据
        values_data = []
        for value in values:
            value_data = {
                'id': value.id,
                'value': value.value,
                'display_name': value.display_name or value.value,
                'order': value.order,
            }
            
            # 根据属性类型添加特殊字段
            if attribute.type == 'color' and value.color_code:
                value_data['color_code'] = value.color_code
            elif attribute.type == 'image' and value.image:
                value_data['image_url'] = value.image.url
            
            values_data.append(value_data)
        
        response_data = {
            'success': True,
            'attribute': {
                'id': attribute.id,
                'name': attribute.name,
                'code': attribute.code,
                'type': attribute.type,
                'type_display': attribute.get_type_display(),
                'unit': attribute.unit or '',
            },
            'values': values_data,
            'count': len(values_data)
        }
        
        # 缓存结果（缓存10分钟）
        set_cache(cache_key, response_data, 600)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"获取属性值时发生错误: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '获取属性值失败',
            'message': str(e) if request.user.is_superuser else '服务器内部错误'
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_attribute_cache(request):
    """清除属性相关缓存"""
    try:
        # 获取所有属性相关的缓存键
        cache_patterns = [
            'attributes_api_*',
            'category_attributes_recommendations_*',
            'attribute_values_*'
        ]
        
        cleared_count = 0
        for pattern in cache_patterns:
            # Django 缓存不直接支持通配符删除，这里简化处理
            # 在生产环境中可能需要使用 Redis 的 KEYS 命令或其他方式
            pass
        
        # 清除特定缓存（如果有的话）
        if not settings.DEBUG:
            cache.clear()  # 简单粗暴的方法，生产环境中应该更精确
        
        return JsonResponse({
            'success': True,
            'message': '缓存已清除',
            'cleared_count': cleared_count
        })
        
    except Exception as e:
        logger.error(f"清除缓存时发生错误: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '清除缓存失败',
            'message': str(e) if request.user.is_superuser else '服务器内部错误'
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def sku_config_ajax(request, sku_id):
    """
    AJAX视图：处理SKU配置的读取和保存
    GET: 获取SKU当前配置
    POST: 保存SKU配置
    """
    try:
        # 获取SKU对象
        sku = SKU.objects.get(id=sku_id)
        
        if request.method == 'GET':
            # 获取当前配置（从关系表获取）
            config = {}
            for sku_attr_value in sku.sku_attribute_values.select_related('attribute', 'attribute_value').all():
                attr_code = sku_attr_value.attribute.code
                display_value = sku_attr_value.get_display_value()
                if display_value:
                    config[attr_code] = display_value
            
            response_data = {
                'success': True,
                'config': config,
                'sku': {
                    'id': sku.id,
                    'name': sku.name,
                    'code': sku.code,
                    'price': float(sku.price),
                    'spu_id': sku.spu.id if sku.spu else None
                }
            }
            
            return JsonResponse(response_data)
        
        elif request.method == 'POST':
            # 保存配置
            configuration = request.POST.get('configuration', '{}')
            attribute_values = request.POST.get('attribute_values', '{}')
            
            try:
                # 解析JSON数据
                config_data = json.loads(configuration) if configuration else {}
                attr_values_data = json.loads(attribute_values) if attribute_values else {}
                
                # 保存属性值到关系表
                for attr_code, value in attr_values_data.items():
                    if value:  # 只保存有值的属性
                        try:
                            sku.set_relational_attribute_value(attr_code, value)
                        except ValueError:
                            # 忽略不存在的属性
                            continue
                
                # 如果有configuration字段，也保存
                if hasattr(sku, 'configuration'):
                    sku.configuration = config_data
                
                sku.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '配置保存成功',
                    'config': attr_values_data
                })
                
            except json.JSONDecodeError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'JSON格式错误',
                    'message': str(e)
                }, status=400)
                
    except SKU.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'SKU with ID {sku_id} does not exist'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error handling SKU config for SKU {sku_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["GET"])
def get_spu_attributes_ajax(request, spu_id):
    """
    AJAX视图：根据SPU ID获取可配置属性
    用于SKU Admin页面的动态属性加载
    """
    try:
        # 获取SPU对象
        spu = SPU.objects.get(id=spu_id, is_active=True)
        
        # 获取与此SPU关联的所有属性
        spu_attributes = SPUAttribute.objects.filter(
            spu=spu
        ).select_related('attribute').order_by('order', 'attribute__order')
        
        # 构建响应数据
        attributes_data = []
        for spu_attr in spu_attributes:
            attribute = spu_attr.attribute
            
            # 获取属性值选项
            attribute_values = list(attribute.values.filter(
                is_active=True
            ).values('id', 'value').order_by('order', 'value'))
            
            # 构建属性数据
            attr_data = {
                'id': attribute.id,
                'name': attribute.name,
                'code': attribute.code,
                'type': attribute.type,
                'description': attribute.description,
                'is_required': spu_attr.is_required,
                'default_value': spu_attr.default_value,
                'order': spu_attr.order,
                'values': attribute_values
            }
            
            attributes_data.append(attr_data)
        
        response_data = {
            'success': True,
            'spu': {
                'id': spu.id,
                'name': spu.name,
                'code': spu.code
            },
            'attributes': attributes_data
        }
        
        return JsonResponse(response_data)
        
    except SPU.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'SPU with ID {spu_id} does not exist'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error fetching SPU attributes for SPU {spu_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["GET"])
def get_attribute_values_ajax(request, attribute_id):
    """
    AJAX视图：根据属性ID获取该属性的所有属性值
    用于SKU属性值表格的动态属性值加载
    """
    try:
        # 获取属性对象
        attribute = Attribute.objects.get(id=attribute_id, is_active=True)
        
        # 获取该属性的所有可用属性值
        attribute_values = list(attribute.values.filter(
            is_active=True
        ).values('id', 'value').order_by('order', 'value'))
        
        response_data = {
            'success': True,
            'attribute': {
                'id': attribute.id,
                'name': attribute.name,
                'code': attribute.code,
                'type': attribute.type
            },
            'values': attribute_values
        }
        
        return JsonResponse(response_data)
        
    except Attribute.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Attribute with ID {attribute_id} does not exist'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error fetching attribute values for attribute {attribute_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal
from .models import SKU, ProductsPricingRule, ProductsDimension, SPU
from .serializers import SKUDetailSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_dynamic_price(request):
    """
    动态价格计算API - 支持SKU专属规则优先级
    """
    try:
        data = request.data
        sku_id = data.get('sku_id')
        custom_dimensions = data.get('dimensions', {})
        
        if not sku_id:
            return Response(
                {'error': '缺少sku_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取SKU信息
        sku = get_object_or_404(SKU, id=sku_id)
        
        if not sku.spu:
            return Response(
                {'error': '该SKU没有关联的SPU，无法计算价格'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取适用的加价规则（按优先级排序：SKU专属 > SPU通用）
        applicable_rules = ProductsPricingRule.get_applicable_rules(sku)
        
        if not applicable_rules.exists():
            return Response({
                'sku_id': sku_id,
                'sku_name': sku.name,
                'base_price': float(sku.price),
                'total_price': float(sku.price),
                'pricing_details': [],
                'calculation_summary': {
                    'total_increment': 0.0,
                    'applied_rules_count': 0,
                    'calculation_time': timezone.now().isoformat(),
                    'message': '无适用的加价规则'
                }
            })
        
        # 获取SKU的标准尺寸
        sku_dimensions = {}
        for dimension in sku.dimensions.all():
            sku_dimensions[dimension.dimension_type] = {
                'standard_value': float(dimension.standard_value),
                'unit': dimension.unit
            }
        
        # 计算价格
        total_increment = Decimal('0')
        pricing_details = []
        used_rule_types = set()  # 跟踪已使用的规则类型，避免重复应用
        
        for rule in applicable_rules:
            # 如果该规则类型已经被更高优先级的规则处理过，跳过
            if rule.rule_type in used_rule_types:
                continue
            
            # 获取对应维度的自定义值和标准值
            custom_value = custom_dimensions.get(rule.rule_type)
            standard_dimension = sku_dimensions.get(rule.rule_type)
            
            if custom_value is None or standard_dimension is None:
                continue
            
            custom_value = Decimal(str(custom_value))
            threshold_value = rule.threshold_value
            
            # 计算超出值
            if custom_value > threshold_value:
                excess_value = custom_value - threshold_value
                increment = rule.calculate_increment(excess_value)
                
                if increment > 0:
                    total_increment += increment
                    pricing_details.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'rule_type': rule.get_rule_type_display(),
                        'rule_scope': rule.rule_scope,  # 新增：显示规则范围
                        'priority': rule.priority,      # 新增：显示优先级
                        'threshold_value': float(threshold_value),
                        'custom_value': float(custom_value),
                        'excess_value': float(excess_value),
                        'unit': standard_dimension['unit'],
                        'calculation_method': rule.get_calculation_method_display(),
                        'price_increment': float(rule.price_increment),
                        'calculated_increment': float(increment),
                        'unit_increment': float(rule.unit_increment)
                    })
                    
                    # 标记该规则类型已被处理
                    used_rule_types.add(rule.rule_type)
        
        # 计算最终价格
        base_price = sku.price
        total_price = base_price + total_increment
        
        return Response({
            'sku_id': sku_id,
            'sku_name': sku.name,
            'sku_code': sku.code,
            'spu_name': sku.spu.name,
            'base_price': float(base_price),
            'total_price': float(total_price),
            'pricing_details': pricing_details,
            'calculation_summary': {
                'total_increment': float(total_increment),
                'applied_rules_count': len(pricing_details),
                'calculation_time': timezone.now().isoformat(),
                'rule_priority_info': {
                    'sku_specific_rules': len([r for r in applicable_rules if r.sku]),
                    'spu_general_rules': len([r for r in applicable_rules if not r.sku]),
                    'total_available_rules': applicable_rules.count()
                }
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'价格计算失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sku_dimensions(request, sku_id):
    """
    获取SKU的尺寸信息API
    """
    try:
        sku = get_object_or_404(SKU, id=sku_id)
        dimensions = sku.dimensions.all()
        
        result = {
            'sku_id': sku_id,
            'sku_name': sku.name,
            'sku_code': sku.code,
            'price': float(sku.price),
            'brand': sku.brand.name if sku.brand else None,
            'spu_id': sku.spu.id if sku.spu else None,
            'spu_name': sku.spu.name if sku.spu else None,
            'dimensions': []
        }
        
        for dimension in dimensions:
            result['dimensions'].append({
                'dimension_type': dimension.dimension_type,
                'dimension_type_display': dimension.get_dimension_type_display(),
                'standard_value': float(dimension.standard_value),
                'min_value': float(dimension.min_value) if dimension.min_value else None,
                'max_value': float(dimension.max_value) if dimension.max_value else None,
                'unit': dimension.unit,
                'unit_display': dimension.get_display_unit(),
                'tolerance': float(dimension.tolerance),
                'is_key_dimension': dimension.is_key_dimension,
                'description': dimension.description
            })
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'获取尺寸信息时发生错误: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_pricing_rules(request, spu_id):
    """
    获取SPU的加价规则API
    """
    try:
        from .models import SPU
        spu = get_object_or_404(SPU, id=spu_id)
        
        rules = spu.pricing_rules.filter(is_active=True).order_by('rule_type', 'threshold_value')
        
        result = {
            'spu_id': spu_id,
            'spu_name': spu.name,
            'rules': []
        }
        
        for rule in rules:
            if rule.is_effective():
                result['rules'].append({
                    'id': rule.id,
                    'name': rule.name,
                    'rule_type': rule.rule_type,
                    'rule_type_display': rule.get_rule_type_display(),
                    'threshold_value': float(rule.threshold_value),
                    'unit_increment': float(rule.unit_increment),
                    'calculation_method': rule.calculation_method,
                    'calculation_method_display': rule.get_calculation_method_display(),
                    'price_increment': float(rule.price_increment),
                    'multiplier': float(rule.multiplier),
                    'max_increment': float(rule.max_increment) if rule.max_increment else None,
                    'description': rule.description
                })
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'获取加价规则时发生错误: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sku_by_spu(request):
    """
    获取指定SPU下的SKU列表（用于管理界面）
    """
    spu_id = request.GET.get('spu_id')
    
    if not spu_id:
        return JsonResponse({'error': '缺少spu_id参数'}, status=400)
    
    try:
        spu = get_object_or_404(SPU, id=spu_id)
        skus = SKU.objects.filter(spu=spu, status='active').order_by('name')
        
        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'code': sku.code or '',
                'price': float(sku.price) if sku.price else 0.0
            })
        
        return JsonResponse({
            'skus': sku_list,
            'spu_name': spu.name,
            'count': len(sku_list)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_spu_dimension_templates(request):
    """获取指定SPU的尺寸模板"""
    from django.contrib.admin.views.decorators import staff_member_required
    from django.views.decorators.http import require_http_methods
    from .models import SPUDimensionTemplate
    
    # 检查用户权限
    if not request.user.is_staff:
        return JsonResponse({'error': '权限不足'}, status=403)
    
    spu_id = request.GET.get('spu_id')
    
    if not spu_id:
        return JsonResponse({'error': '缺少SPU ID参数'}, status=400)
    
    try:
        templates = SPUDimensionTemplate.objects.filter(spu_id=spu_id).order_by('order')
        
        template_data = []
        for template in templates:
            template_data.append({
                'dimension_type': template.dimension_type,
                'default_value': template.default_value,
                'unit': template.unit,
                'min_value': template.min_value,
                'max_value': template.max_value,
                'is_required': template.is_required,
                'is_key_dimension': template.is_key_dimension,
                'order': template.order,
                'remarks': template.remarks or ''
            })
        
        return JsonResponse({
            'templates': template_data,
            'count': len(template_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 导入模板下载相关
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET
from .utils.template_generator import TextTemplateGenerator
# from .services.ai_data_import_service import AIDataImportService


@require_GET
def download_template(request):
    """
    Royana产品导入模板下载视图

    支持的参数：
    - type: 模板类型 (royana_products)
    - sample: 是否包含示例数据 (true/false)
    - format: 文件格式 (xlsx)，默认xlsx
    """
    # 添加调试日志
    logger.info(f"模板下载请求: type={request.GET.get('type')}, format={request.GET.get('format')}, sample={request.GET.get('sample')}")

    template_type = request.GET.get('template_type', 'royana_import')
    include_sample = request.GET.get('include_sample', 'true').lower() == 'true'
    format_type = request.GET.get('format', 'csv').lower()

    # 验证模板类型
    valid_types = ['royana_import', 'ai_data']
    if template_type not in valid_types:
        return JsonResponse({
            'error': f'不支持的模板类型: {template_type}，当前只支持Royana产品导入',
            'valid_types': valid_types
        }, status=400)

    # 验证格式类型
    valid_formats = ['csv']
    if format_type not in valid_formats:
        return JsonResponse({
            'error': f'不支持的文件格式: {format_type}，当前只支持CSV格式',
            'valid_formats': valid_formats
        }, status=400)
    
    try:
        # 使用文本生成器生成Royana模板
        generator = TextTemplateGenerator()
        response = generator.get_template_response(template_type, include_sample)
        return response

    except Exception as e:
        logger.error(f'Royana模板下载失败: {str(e)}')
        return JsonResponse({
            'error': f'模板生成失败: {str(e)}'
        }, status=500)


@require_GET  
def list_templates(request):
    """
    列出所有可用的模板类型
    """
    templates = [
        {
            'type': 'products',
            'name': '产品数据模板',
            'description': '用于批量导入产品和SKU数据',
            'fields_count': 30,
            'simple_fields_count': 12,
        },
        {
            'type': 'categories', 
            'name': '分类数据模板',
            'description': '用于批量导入产品分类数据',
            'fields_count': 6,
            'simple_fields_count': 4,
        },
        {
            'type': 'brands',
            'name': '品牌数据模板', 
            'description': '用于批量导入品牌数据',
            'fields_count': 8,
            'simple_fields_count': 5,
        },
        {
            'type': 'attributes',
            'name': '属性数据模板',
            'description': '用于批量导入产品属性数据', 
            'fields_count': 9,
            'simple_fields_count': 4,
        },
        {
            'type': 'price_levels',
            'name': '价格级别模板',
            'description': '用于批量导入多级价格产品数据，支持II/III/IV/V级价格',
            'fields_count': 12,
            'simple_fields_count': 12,
        }
    ]
    
    return JsonResponse({
        'templates': templates,
        'download_url_template': '/api/import-templates/download_template/?type={type}&sample={sample}&format={format}&simple={simple}',
        'supported_formats': ['csv', 'txt'],
        'features': {
            'simple_mode': '简化模式，只包含核心必填字段',
            'txt_format': 'TXT格式支持制表符分隔和字段说明',
            'auto_generation': '系统可自动生成SPU编码、库存默认值、状态等字段'
        }
    })


# AI数据格式导入相关视图
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os

@csrf_exempt
@require_POST
def import_ai_data(request):
    """
    AI数据格式导入视图
    处理AI模型输出的15列标准化数据格式
    """
    try:
        # 检查用户权限
        if not request.user.is_authenticated:
            return JsonResponse({'error': '请先登录'}, status=401)

        # 获取上传的文件或CSV数据
        csv_content = None
        file_name = 'ai_data.csv'

        if 'file' in request.FILES:
            # 文件上传
            uploaded_file = request.FILES['file']
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            if file_extension not in allowed_extensions:
                return JsonResponse({'error': f'不支持的文件格式，支持的格式：{", ".join(allowed_extensions)}'}, status=400)

            if file_extension == '.csv':
                csv_content = uploaded_file.read().decode('utf-8')
            else:
                # 处理Excel文件，转换为CSV
                import pandas as pd
                from io import BytesIO

                try:
                    # 读取Excel文件
                    excel_data = BytesIO(uploaded_file.read())
                    df = pd.read_excel(excel_data)

                    # 转换为CSV格式
                    csv_content = df.to_csv(index=False)
                except Exception as e:
                    return JsonResponse({'error': f'Excel文件读取失败: {str(e)}'}, status=400)

            file_name = uploaded_file.name

        elif 'csv_data' in request.POST:
            # 直接传递CSV数据
            csv_content = request.POST['csv_data']
            file_name = f'paste_data_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'

        else:
            return JsonResponse({'error': '请提供CSV文件或CSV数据'}, status=400)

        if not csv_content:
            return JsonResponse({'error': 'CSV数据为空'}, status=400)

        # 获取模板类型，默认为AI数据格式
        template_type = request.POST.get('template_type', 'ai_data')

        # 创建导入任务
        from .models import ImportTask
        task = ImportTask.objects.create(
            name=request.POST.get('name', f'数据导入_{timezone.now().strftime("%Y%m%d_%H%M%S")}'),
            task_type=template_type,
            created_by=request.user,
            status='pending'
        )

        # 使用统一的AI数据导入服务，支持多种模板类型
        from .services.ai_data_import_service_v2 import AIDataImportServiceV2
        import_service = AIDataImportServiceV2(task)

        if template_type == 'ai_data':
            result = import_service.process_ai_data_import(csv_content)
        else:
            # 对于传统Royana格式，先转换为AI数据格式再处理
            try:
                # 这里可以添加格式转换逻辑
                # 暂时直接使用AI数据导入处理
                result = import_service.process_ai_data_import(csv_content)
            except Exception as e:
                logger.error(f"传统格式处理失败: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'数据格式不兼容，请使用AI数据格式或检查数据格式: {str(e)}'
                }, status=400)

        return JsonResponse({
            'success': result['success'],
            'task_id': task.id,
            'total_rows': result['total_rows'],
            'success_rows': result['success_rows'],
            'error_rows': result['error_rows'],
            'message': f'导入完成：成功 {result["success_rows"]} 行，失败 {result["error_rows"]} 行'
        })

    except Exception as e:
        logger.error(f"AI数据导入失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'导入失败: {str(e)}'
        }, status=500)


# 数据清理相关接口
@csrf_exempt
@require_POST
@staff_member_required
def clear_product_data_api(request):
    """清空产品数据API"""
    try:
        from products.services.import_system.utils.data_cleaner import DataCleaner

        # 获取参数
        action = request.POST.get('action', 'summary')  # summary, dry_run, confirm
        data_types = request.POST.getlist('data_types', [])  # 指定数据类型

        cleaner = DataCleaner()

        if action == 'summary':
            # 获取数据摘要
            summary = cleaner.get_data_summary()
            return JsonResponse({
                'success': True,
                'action': 'summary',
                'data': summary
            })

        elif action == 'dry_run':
            # 干运行模式
            stats = cleaner._get_current_stats()
            total_records = sum(stats.values())

            return JsonResponse({
                'success': True,
                'action': 'dry_run',
                'data': {
                    'total_records': total_records,
                    'stats': stats,
                    'will_delete': [
                        {'name': 'SKU属性值关联', 'count': stats['sku_attribute_value_count']},
                        {'name': 'SPU属性关联', 'count': stats['spu_attribute_count']},
                        {'name': 'SKU产品', 'count': stats['sku_count']},
                        {'name': 'SPU产品', 'count': stats['spu_count']},
                        {'name': '属性值', 'count': stats['attribute_value_count']},
                        {'name': '属性', 'count': stats['attribute_count']},
                        {'name': '品牌', 'count': stats['brand_count']},
                        {'name': '产品分类', 'count': stats['category_count']},
                        {'name': '导入错误', 'count': stats['import_error_count']},
                        {'name': '导入任务', 'count': stats['import_task_count']},
                    ]
                }
            })

        elif action == 'confirm':
            # 执行清理
            if data_types:
                # 清理指定类型
                result = cleaner.clear_specific_data(data_types, confirm=True)
            else:
                # 清理所有数据
                result = cleaner.clear_product_data(confirm=True)

            return JsonResponse({
                'success': result['success'],
                'action': 'confirm',
                'data': result
            })

        else:
            return JsonResponse({
                'success': False,
                'error': f'未知的操作类型: {action}'
            }, status=400)

    except Exception as e:
        logger.error(f"数据清理API失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'清理失败: {str(e)}'
        }, status=500)


@require_GET
@staff_member_required
def get_data_summary_api(request):
    """获取数据摘要API"""
    try:
        from products.services.import_system.utils.data_cleaner import DataCleaner

        cleaner = DataCleaner()
        summary = cleaner.get_data_summary()

        return JsonResponse({
            'success': True,
            'data': summary
        })

    except Exception as e:
        logger.error(f"获取数据摘要失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取摘要失败: {str(e)}'
        }, status=500)


@staff_member_required
def clear_data_tool_view(request):
    """数据清理工具页面视图"""
    context = {
        'title': '产品数据清理工具',
        'has_permission': True,
    }
    return render(request, 'admin/clear_data_tool.html', context)


@require_GET
def download_ai_template(request):
    """
    下载AI数据格式模板
    """
    include_sample = request.GET.get('include_sample', 'true').lower() == 'true'

    try:
        generator = TextTemplateGenerator()
        response = generator.get_template_response('ai_data', include_sample)

        # 设置文件名
        filename = f'AI数据格式导入模板{"_含示例数据" if include_sample else ""}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        logger.error(f"AI模板下载失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'模板生成失败: {str(e)}'
        }, status=500)


def debug_paste_view(request):
    """调试粘贴功能的页面"""
    return render(request, 'import/debug_paste.html')
