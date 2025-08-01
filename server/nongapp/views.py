from django.db.models.functions import TruncDate
import logging
# 设置日志记录
logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import ProductPrice  # 确保您有这个模型
User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Max, Min, Count, Sum
from django.http import JsonResponse
from django.db.models.functions import ExtractYear, ExtractMonth
from collections import defaultdict
import json
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from .serializers import ProductPriceSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Max, Avg, Count, Case, When, IntegerField
from django.db.models.functions import TruncMonth
import json
import jieba
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from django.http import JsonResponse
import os
import numpy as np
import pymysql
import pandas as pd
from django.http import JsonResponse
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from django.utils.timezone import now
from datetime import timedelta


def get_price_statistics(request):
    """获取价格统计数据"""
    stats = ProductPrice.objects.aggregate(
        avg_price=Avg('price'),
        max_price=Max('price'),
        min_price=Min('price'),
        total_records=Count('id')
    )

    # 获取品种统计
    variety_stats = ProductPrice.objects.values('variety') \
                        .annotate(
        avg_price=Avg('price'),
        max_price=Max('price'),
        min_price=Min('price'),
        count=Count('id')
    ).order_by('-count')[:10]

    # 获取地区统计
    area_stats = ProductPrice.objects.values('area') \
                     .annotate(
        avg_price=Avg('price'),
        count=Count('id')
    ).order_by('-count')[:10]

    return JsonResponse({
        'code': 200,
        'data': {
            'overall_stats': stats,
            'variety_stats': list(variety_stats),
            'area_stats': list(area_stats)
        },
        'msg': '获取统计数据成功'
    })


def get_price_trend(request):
    """获取价格趋势数据"""
    trends = ProductPrice.objects.annotate(
        date=TruncDate('data')
    ).values('date').annotate(
        avg_price=Avg('price'),
        count=Count('id')
    ).order_by('date')

    return JsonResponse({
        'code': 200,
        'data': list(trends),
        'msg': '获取价格趋势成功'
    })



def get_product_prices(request):
    """获取农产品价格数据（带分页）"""
    try:
        # 打印请求信息，帮助调试
        print(f"请求方法: {request.method}")
        print(f"请求参数: {request.GET}")

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 10))

        # 计算分页
        start = (page - 1) * page_size
        end = start + page_size

        # 获取总记录数
        total = ProductPrice.objects.count()

        # 获取分页数据
        products = ProductPrice.objects.all().order_by('-data')[start:end]

        data = []
        for product in products:
            data.append({
                'id': product.id,
                'date': product.data.strftime('%Y-%m-%d'),
                'category': product.category,
                'variety': product.variety,
                'price': float(product.price),
                'unit': product.unit,
                'area': product.area
            })

        response_data = {
            'code': 200,
            'data': {
                'list': data,
                'total': total
            },
            'msg': '获取价格数据成功'
        }

        print("响应数据:", response_data)
        return JsonResponse(response_data)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': {
                'list': [],
                'total': 0
            }
        })

def get_product_prices_by_variety(request):
    """按品种获取农产品价格数据"""
    varieties = ProductPrice.objects.values_list('variety', flat=True).distinct()
    result = {}
    for variety in varieties:
        products = ProductPrice.objects.filter(variety=variety).order_by('-data')
        result[variety] = [{
            'date': product.data.strftime('%Y-%m-%d'),
            'category': product.category,#大类
            'price': float(product.price),
            'unit': product.unit,
            'area': product.area
        } for product in products]

    return JsonResponse({
        'status': 'success',
        'data': result
    })

#可视化大屏
def data_dashboard(request):
    """
    返回前端大屏所需的各种数据（例如：最高价品种、最低价品种、平均价格、年度趋势统计等）。
    """
    # 1. 统计所有数据条目数
    total_varieties = ProductPrice.objects.count()

    # 2. 计算最大、最小、平均价格
    agg_data = ProductPrice.objects.aggregate(
        max_price=Max('price'),
        min_price=Min('price'),
        avg_price=Avg('price')
    )

    # 3. 最高价 & 最低价品种
    highest_item = ProductPrice.objects.order_by('-price').first()
    lowest_item = ProductPrice.objects.exclude(price=0).order_by('price').first()

    # 4. 获取最新数据的日期
    latest_record = ProductPrice.objects.order_by('-data').first()
    latest_date = latest_record.data.strftime('%Y-%m-%d') if latest_record else None

    # 5. 计算热门品种排行（按分类选最高价）
    categories = {
        "水果": 2,  # 取2个最高价
        "水产品": 1,
        "蔬菜": 1,
        "畜禽产品": 1
    }

    top_items = []
    for category, limit in categories.items():
        items = list(ProductPrice.objects.filter(category=category).order_by('-price')[:limit])
        top_items.extend(items)

    # 按价格排序（降序）
    top_items.sort(key=lambda x: x.price or 0, reverse=True)

    # 6. 年度农产品趋势统计
    yearly_trends = defaultdict(lambda: [0] * 12)  # 初始化12个月的默认数据

    trends_data = (
        ProductPrice.objects
        .annotate(year=ExtractYear('data'), month=ExtractMonth('data'))
        .values('year', 'month')
        .annotate(avg_price=Avg('price'))
        .order_by('year', 'month')
    )

    for entry in trends_data:
        year = str(entry["year"])
        month = entry["month"] - 1  # 1月对应索引0
        yearly_trends[year][month] = round(entry["avg_price"], 2)  # 保留2位小数

    # 7. 品类占比统计
    category_stats = ProductPrice.objects.values('category') \
        .annotate(category_count=Count('category'), total_price=Sum('price')) \
        .order_by('-category_count')

    total_count = ProductPrice.objects.count()  # 总记录数，用于计算占比
    total_price = ProductPrice.objects.aggregate(total_price=Sum('price'))["total_price"] or 0  # 总价格，用于计算占比

    # 计算品类占比（按数量和销售金额占比）
    category_percentage = []
    for stat in category_stats:
        category_name = stat['category']
        category_count = stat['category_count']
        total_price_for_category = stat['total_price'] or 0

        category_percentage.append({
            'category': category_name,
            'count_percentage': round(category_count / total_count * 100, 2),  # 按数量占比
            'price_percentage': round(total_price_for_category / total_price * 100, 2)  # 按销售额占比
        })

    # 8. 计算全国和地方部分的比例
    total_count_national = ProductPrice.objects.filter(area='全国平均').count()  # 假设 area 字段为 "全国"
    total_count_local = ProductPrice.objects.exclude(area='全国平均').count()  # 假设 area 字段为 "地方"

    national_percentage = round(total_count_national / total_count * 100, 2) if total_count else 0
    local_percentage = round(total_count_local / total_count * 100, 2) if total_count else 0

    # 9. 区域热力图数据（填充缺失省份）
    # 假设数据库中的 province='全国平均' 这条记录代表全国均价
    national_obj = ProductPrice.objects.filter(province='全国平均').aggregate(nat_avg=Avg('price'))
    national_avg = national_obj['nat_avg'] or 0  # 若没查到则为0

    # 查询已有省份的平均价
    region_data = (
        ProductPrice.objects
        .values('province')
        .annotate(avg_price=Avg('price'))
        .order_by('province')
    )

    # 先做成一个 {省份名称: 平均价} 的字典
    province_avg_dict = {}
    for row in region_data:
        prov = row["province"]
        if prov:
            province_avg_dict[prov] = round(row["avg_price"], 2)

    # 需要手动补上的省份
    missing_provinces = ["西藏自治区", "贵州省", "江西省", "重庆市", "吉林省", "台湾省"]
    for mp in missing_provinces:
        if mp not in province_avg_dict:
            province_avg_dict[mp] = round(national_avg, 2)  # 用全国平均填充

    # 重新构造 region_distribution
    region_distribution = []
    for prov_name, avg_val in province_avg_dict.items():
        # 过滤掉不在中国地图的外国记录（如 "美国"、"加拿大" 等）
        # 如果你只想保留中国省份，就在这里做一层判断：
        # if prov_name not in ALL_CHINA_PROVINCES: continue
        region_distribution.append({
            "name": prov_name,
            "value": avg_val
        })

    # 构造返回给前端的数据
    response_data = {
        "total_varieties": total_varieties,
        "max_price": agg_data["max_price"] or 0,
        "min_price": agg_data["min_price"] or 0,
        "avg_price": round(agg_data["avg_price"] or 0, 2),
        "latest_date": latest_date,
        "highest_item": {
            "variety": highest_item.variety if highest_item else "",
            "price": highest_item.price if highest_item else 0
        },
        "lowest_item": {
            "variety": lowest_item.variety if lowest_item else "",
            "price": lowest_item.price if lowest_item else 0
        },
        "top_items": [
            {
                "variety": item.variety,
                "price": item.price,
                "category": item.category  # 增加品种分类信息
            } for item in top_items
        ],
        "yearly_trends": yearly_trends,  # 新增年度趋势数据
        "category_percentage": category_percentage, # 品类占比数据
        "national_percentage": national_percentage,  # 全国部分占比
        "local_percentage": local_percentage, # 地方部分占比
        # 将区域热力图数据放到返回的 JSON 中
        "region_distribution": region_distribution
    }

    return JsonResponse(response_data, safe=False)


# 定义一个标准分页器
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100  # 每页返回100条数据，根据实际情况调整
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.all()
    serializer_class = ProductPriceSerializer
    pagination_class = StandardResultsSetPagination  # 假设你已开启分页

    def get_queryset(self):
        """
        支持 ?category=xxx 过滤、?variety=xxx 过滤，并默认按日期降序。
        """
        queryset = super().get_queryset()

        category = self.request.query_params.get('category')
        variety = self.request.query_params.get('variety')

        if category:
            queryset = queryset.filter(category=category)

        if variety:
            queryset = queryset.filter(variety__icontains=variety)

        # 按日期字段倒序
        queryset = queryset.order_by('-data')
        return queryset


def city_category_analysis(request):
    # 获取前端传入的年份参数，默认返回全部
    year = request.GET.get('year')  # 示例：2023、2024、2025

    queryset = ProductPrice.objects.all()

    if year:
        queryset = queryset.filter(data__year=year)  # ✅ 正确：data 是你的日期字段  # 假设你的日期字段为 date

    # 获取所有的省份和分类组合计数
    raw_data = (
        queryset.values('province', 'category')
        .annotate(count=Count('id'))
        .order_by('province', 'category')
    )

    # 构建结构：{province: {分类: count}}
    province_set = set()
    category_set = set()
    data_map = {}

    for item in raw_data:
        province = item['province'] or '未知省份'
        category = item['category'] or '未知分类'
        count = item['count']

        province_set.add(province)
        category_set.add(category)

        if province not in data_map:
            data_map[province] = {}
        data_map[province][category] = count

    province_list = sorted(province_set)
    category_list = sorted(category_set)

    # 构造前端需要的数据格式（每个分类是一条 series）
    series = []
    for category in category_list:
        series.append({
            "name": category,
            "type": "bar",
            "stack": "total",  # 如果你想要堆叠图就保留，若要并列柱状图就删除这一行
            "data": [data_map.get(province, {}).get(category, 0) for province in province_list]
        })

    # 饼图数据：各分类总量
    category_pie = (
        queryset.values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    pie_data = [
        {"name": item['category'] or '未知分类', "value": item['count']}
        for item in category_pie
    ]

    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": {
            "xAxis": province_list,     # 横轴：城市
            "series": series,           # 柱状图数据
            "pie": pie_data,            # 饼图数据
            "categories": category_list # 分类列表（图例）
        }
    })

def price_sales_analysis(request):
    """
    统计数据：
      1. 各省份的最高价格（城市价格最大值分析）
      2. 各分类的平均价格（类型价格平均值分析）
      3. 按月份统计价格平均值（“月销量价格平均值”）
      4. 按价格区间统计记录比例（价格区间分析占比）
      5. 品种价格平均值分析：按 variety 分组计算平均价格
    """

    # 1. 城市价格最大值分析：按 province 分组取价格最大值
    city_qs = ProductPrice.objects.values('province').annotate(max_price=Max('price'))
    city_max_price = [
        {"name": item["province"] or "未知省份", "value": item["max_price"]}
        for item in city_qs
    ]

    # 2. 类型价格平均值分析：按 category 分组计算平均价格
    category_qs = ProductPrice.objects.values('category').annotate(avg_price=Avg('price'))
    category_avg_price = [
        {"name": item["category"] or "未知分类", "value": round(item["avg_price"], 2)}
        for item in category_qs
    ]

    # 3. 月销量价格平均值（按月份统计平均价格）
    monthly_qs = ProductPrice.objects.annotate(month=TruncMonth('data')).values('month').annotate(avg_price=Avg('price')).order_by('month')
    monthly_avg_price = [
        {"name": item["month"].strftime("%Y-%m"), "value": round(item["avg_price"], 2)}
        for item in monthly_qs
    ]

    # 4. 价格区间分析占比：设定价格区间（示例：0-10, 10-20, 20-30, 30-40, 40以上）
    price_range = ProductPrice.objects.aggregate(
        range_0_10=Count(Case(When(price__lt=10, then=1), output_field=IntegerField())),
        range_10_20=Count(Case(When(price__gte=10, price__lt=20, then=1), output_field=IntegerField())),
        range_20_30=Count(Case(When(price__gte=20, price__lt=30, then=1), output_field=IntegerField())),
        range_30_40=Count(Case(When(price__gte=30, price__lt=40, then=1), output_field=IntegerField())),
        range_40_up=Count(Case(When(price__gte=40, then=1), output_field=IntegerField()))
    )
    price_range_distribution = [
        {"name": "0-10", "value": price_range["range_0_10"]},
        {"name": "10-20", "value": price_range["range_10_20"]},
        {"name": "20-30", "value": price_range["range_20_30"]},
        {"name": "30-40", "value": price_range["range_30_40"]},
        {"name": "40以上", "value": price_range["range_40_up"]},
    ]

    # 5. 品种价格平均值分析：按 variety 分组计算平均价格
    variety_qs = ProductPrice.objects.values('variety').annotate(avg_price=Avg('price')).order_by('variety')
    variety_avg_price = [
        {"name": item["variety"] or "未知品种", "value": round(item["avg_price"], 2)}
        for item in variety_qs
    ]



    return JsonResponse({
        "code": 0,
        "msg": "success",
        "data": {
            "city_max_price": city_max_price,
            "category_avg_price": category_avg_price,
            "monthly_avg_price": monthly_avg_price,
            "price_range_distribution": price_range_distribution,
            "variety_avg_price": variety_avg_price
        }
    })

def variety_wordcloud(request):
    # 品种词云
    data = (
        ProductPrice.objects.values('variety')
        .annotate(count=Count('variety'))
        .order_by('-count')[:100]  # 限制前100个热门词
    )
    return JsonResponse({'data': list(data)})

def area_wordcloud(request):
    # 城市词云，排除 "全国平均"
    data = (
        ProductPrice.objects.exclude(province="全国平均")  # 排除“全国平均”这个城市
        .values('province')  # 按照城市（省份）分组
        .annotate(count=Count('province'))  # 统计每个城市出现的次数
        .order_by('-count')[:100]  # 限制前100个热门城市
    )
    return JsonResponse({'data': list(data)})


# 模型路径 + 预测算法
MODEL_PATH = "predict/models/unified_lstm_model.h5"
SCALER_MIN_PATH = "predict/models/scaler.npy"
SCALER_SCALE_PATH = "predict/models/scaler_scale.npy"

# 数据库读取（获取指定品种最近的数据）
def get_variety_data(variety_name, limit=60):
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="nong",
        charset="utf8mb4"
    )
    cursor = db.cursor()
    sql = f"""
        SELECT data, price FROM nongapp_productprice
        WHERE variety = %s
        ORDER BY data DESC
        LIMIT %s;
    """
    cursor.execute(sql, (variety_name, limit))
    data = cursor.fetchall()
    db.close()

    df = pd.DataFrame(data, columns=["data", "price"])
    df = df.sort_values("data")  # 按时间升序
    return df

# 预测函数
def predict_next_7_days(variety_name):

    model = load_model(MODEL_PATH, compile=False)
    df = get_variety_data(variety_name)
    # 加载 scaler 参数
    # 新做法：基于当前品种数据动态拟合 scaler
    scaler = MinMaxScaler()
    scaler.fit(df[['price']])

    # 获取数据
    df = get_variety_data(variety_name)
    if len(df) < 7:
        return {"error": "该品种数据不足7天，无法预测"}

    last_sequence = df["price"].values[-7:]
    scaled_seq = scaler.transform(last_sequence.reshape(-1, 1)).reshape(1, 7, 1)

    preds = []
    for _ in range(7):
        pred = model.predict(scaled_seq, verbose=0)[0][0]
        preds.append(pred)
        scaled_seq = np.append(scaled_seq[:, 1:, :], [[[pred]]], axis=1)

    # 还原预测结果
    preds_inverse = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()

    # 构建带日期的结果
    start_date = datetime.now().date()
    forecast = []
    for i in range(7):
        forecast.append({
            "date": (start_date + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
            "predicted_price": round(float(preds_inverse[i]), 2)
        })

    return {"variety": variety_name, "forecast": forecast}

def forecast_price(request):
    try:
        if request.method == "POST":
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            variety = data.get("variety")
        else:  # GET 请求
            variety = request.GET.get("variety")

        if not variety:
            return JsonResponse({"error": "缺少品种名参数 variety"}, status=400)

        result = predict_next_7_days(variety)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def dashboard_summary(request):
    # 最多的品种（按记录数）
    top_variety = (
        ProductPrice.objects
        .values('variety')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    most_common_variety = top_variety['variety'] if top_variety else "暂无数据"

    # 品种总数
    total_varieties = ProductPrice.objects.values('variety').distinct().count()

    # 产地最多的省份（按记录数）
    top_province = (
        ProductPrice.objects
        .values('province')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    most_common_province = top_province['province'] if top_province else "暂无数据"

    # === 价格走势：最近7天 ===
    trend_data_7 = (
        ProductPrice.objects
        .values('data')
        .annotate(avg_price=Avg('price'))
        .order_by('-data')[:7]
    )
    trend_data_7 = sorted(trend_data_7, key=lambda x: x['data'])
    recent_trend = [
        {
            "date": item['data'].strftime('%Y-%m-%d') if item['data'] else "未知日期",
            "avg_price": round(item['avg_price'], 2) if item['avg_price'] else 0
        }
        for item in trend_data_7
    ]

    # === 价格走势：最近30天 ===
    latest_date = ProductPrice.objects.aggregate(latest=Max('data'))['latest'] or now().date()
    start_30_days_ago = latest_date - timedelta(days=30)

    trend_data_30 = (
        ProductPrice.objects
        .filter(data__gte=start_30_days_ago)
        .values('data')
        .annotate(avg_price=Avg('price'))
        .order_by('data')
    )
    trend_30_days = [
        {
            "date": item['data'].strftime('%Y-%m-%d') if item['data'] else "未知日期",
            "avg_price": round(item['avg_price'], 2) if item['avg_price'] else 0
        }
        for item in trend_data_30
    ]

    # === 价格走势：按月统计全年 ===
    trend_data_year = (
        ProductPrice.objects
        .annotate(year=ExtractYear('data'), month=ExtractMonth('data'))
        .values('year', 'month')
        .annotate(avg_price=Avg('price'))
        .order_by('year', 'month')
    )
    trend_year = [
        {
            "date": f"{item['year']}-{item['month']:02d}",
            "avg_price": round(item['avg_price'], 2)
        }
        for item in trend_data_year
    ]



    # 异常检测：找出价格高于均值 3 倍以上的记录
    avg_price = ProductPrice.objects.aggregate(avg=Avg('price'))['avg'] or 0
    threshold = avg_price * 3
    anomalies = list(
        ProductPrice.objects
        .filter(price__gt=threshold)
        .order_by('-price')
        .values('variety', 'price', 'data')[:5]
    )
    for a in anomalies:
        a['data'] = a['data'].strftime('%Y-%m-%d') if a['data'] else '未知日期'
        a['price'] = round(float(a['price']), 2)

    return JsonResponse({
        "most_common_variety": most_common_variety,
        "total_varieties": total_varieties,
        "most_common_province": most_common_province,
        "trend_7_days": recent_trend,
        "trend_30_days": trend_30_days,
        "trend_year": trend_year,
        "price_anomalies": anomalies
    })


