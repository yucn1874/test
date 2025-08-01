
from django.urls import path
from django.urls import path, include
from . import views
from .views import data_dashboard
from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter
from .views import ProductPriceViewSet
from .views import city_category_analysis
from .views import price_sales_analysis
from .views import forecast_price
from .views import dashboard_summary


router = DefaultRouter()
router.register(r'product-prices', ProductPriceViewSet, basename='product-price')

urlpatterns = [
    path('', include(router.urls)),

    path('statistics/', views.get_price_statistics, name='price_statistics'),
    path('trend/', views.get_price_trend, name='price_trend'),
    path('list/', views.get_product_prices, name='price_list'),
    path('by_variety/', views.get_product_prices_by_variety, name='price_by_variety'),
    path('data_dashboard/', views.data_dashboard, name='dashboard_data'),
    path('city-category-analysis/', city_category_analysis, name='city_category_analysis'),
    path('price-sales-analysis/', price_sales_analysis, name='price_sales_analysis'),
    path('wordcloud/variety/', views.variety_wordcloud, name='variety_wordcloud'),
    path('wordcloud/area/', views.area_wordcloud, name='area_wordcloud'),
    path('forecast/', forecast_price,name="forecast_price"),
    path('dashboard/summary/', dashboard_summary,name="dashboard_summary"),
]