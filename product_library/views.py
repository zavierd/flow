from django.shortcuts import render
from django.http import JsonResponse
from products.models import SKU
from django.db import models

def home(request):
    """首页视图"""
    return render(request, 'base.html')

def health_check(request):
    """健康检查视图"""
    return JsonResponse({
        'status': 'ok',
        'message': '整木定制产品库管理系统运行正常',
        'version': '1.0.0'
    })

def dynamic_pricing_calculator(request):
    """动态价格计算器页面"""
    # 获取有加价规则的SKU - 只显示有SPU且SPU有加价规则的产品
    skus = SKU.objects.filter(
        status='active',
        spu__isnull=False  # 必须有SPU
    ).select_related('spu', 'brand').distinct().order_by('name')
    
    # 进一步过滤有加价规则的SKU
    filtered_skus = []
    for sku in skus:
        if sku.spu and sku.spu.pricing_rules.filter(is_active=True).exists():
            filtered_skus.append(sku)
    
    # 如果是AJAX搜索请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        search_term = request.GET.get('q', '').strip()
        if search_term:
            # 根据搜索关键词过滤SKU
            filtered_skus = [
                sku for sku in filtered_skus
                if (search_term.lower() in sku.name.lower() or
                    search_term.lower() in (sku.code or '').lower() or
                    search_term.lower() in (sku.brand.name if sku.brand else '').lower() or
                    search_term.lower() in (sku.spu.name if sku.spu else '').lower())
            ]
        
        # 返回JSON数据
        sku_data = []
        for sku in filtered_skus[:20]:  # 限制返回数量
            sku_data.append({
                'id': sku.id,
                'name': sku.name,
                'sku_code': sku.code,  # 使用code字段
                'price': float(sku.price) if sku.price else 0,
                'brand': sku.brand.name if sku.brand else '',
                'spu': sku.spu.name if sku.spu else '',
                'display_text': f"{sku.name} - {sku.brand.name if sku.brand else '未知品牌'} - ¥{sku.price}"
            })
        
        return JsonResponse({'skus': sku_data})
    
    context = {
        'skus': filtered_skus,
        'title': '动态价格计算器',
    }
    
    return render(request, 'admin/dynamic_pricing.html', context) 