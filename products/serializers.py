from rest_framework import serializers
from .models import Category, Brand, Attribute, AttributeValue, SPU, SKU, ProductImage, SPUAttribute


class CategorySimpleSerializer(serializers.ModelSerializer):
    """简化的分类序列化器 - 避免递归调用"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'level']


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器 - 支持 MPTT 树状结构"""
    full_path = serializers.ReadOnlyField(source='get_full_path')
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'code', 'parent', 'order', 'description', 
            'is_active', 'level', 'lft', 'rght', 'tree_id',
            'full_path', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'level', 'lft', 'rght', 'tree_id']


class BrandSerializer(serializers.ModelSerializer):
    """品牌序列化器"""
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'code', 'description', 'logo', 'logo_url', 
                 'website', 'contact_email', 'contact_phone', 'is_active', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_logo_url(self, obj):
        """获取品牌Logo的完整URL"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class AttributeValueSerializer(serializers.ModelSerializer):
    """属性值序列化器"""
    class Meta:
        model = AttributeValue
        fields = ['id', 'value', 'order', 'is_active']


class AttributeSerializer(serializers.ModelSerializer):
    """属性序列化器"""
    values = AttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'code', 'type', 'description', 'unit', 
                 'is_required', 'is_filterable', 'order', 'is_active', 
                 'values', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    attributes = serializers.SerializerMethodField()
    
    class Meta:
        model = SPU
        fields = ['id', 'name', 'code', 'category', 'category_name', 'description', 
                 'specifications', 'attributes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_attributes(self, obj):
        """获取SPU关联的属性 - 修复版本"""
        spu_attrs = obj.spuattribute_set.select_related('attribute').all()
        return [
            {
                'attribute_name': spa.attribute.name,
                'attribute_code': spa.attribute.code,
                'default_value': spa.default_value,  # 修复：使用正确的字段名
                'unit': spa.attribute.unit,
                'is_required': spa.is_required,
                'order': spa.order
            }
            for spa in spu_attrs
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """产品图片序列化器 - 修复版本"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'order', 'is_active']  # 修复：使用正确的字段名
    
    def get_image_url(self, obj):
        """获取图片的完整URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class SKUListSerializer(serializers.ModelSerializer):
    """SKU列表序列化器 - 用于产品列表展示"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='spu.category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = SKU
        fields = ['id', 'name', 'code', 'brand', 'brand_name', 'spu', 
                 'category_name', 'price', 'cost_price', 'stock_quantity', 
                 'status', 'is_featured', 'primary_image', 'created_at']
        read_only_fields = ['created_at']
    
    def get_primary_image(self, obj):
        """获取主要图片 - 修复版本"""
        # 首先尝试获取main_image
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        
        # 备选方案：获取第一张激活的图片
        first_img = obj.images.filter(is_active=True).order_by('order').first()
        if first_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_img.image.url)
            return first_img.image.url
        return None


class SKUDetailSerializer(serializers.ModelSerializer):
    """SKU详情序列化器 - 用于产品详情展示"""
    brand = BrandSerializer(read_only=True)
    spu = SPUSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SKU
        fields = ['id', 'name', 'code', 'brand', 'spu', 'price', 'cost_price', 
                 'stock_quantity', 'min_stock', 'max_stock', 'weight', 'dimensions', 
                 'color', 'material', 'style', 'description', 'selling_points', 
                 'usage_scenarios', 'maintenance_guide', 'warranty_period', 
                 'tags', 'status', 'is_featured', 'images', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class FilterSerializer(serializers.Serializer):
    """筛选器序列化器"""
    categories = CategorySimpleSerializer(many=True, read_only=True)
    brands = BrandSerializer(many=True, read_only=True)
    attributes = AttributeSerializer(many=True, read_only=True)
    price_range = serializers.DictField(read_only=True)
    status_choices = serializers.ListField(read_only=True) 