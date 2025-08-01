import requests
import logging
from datetime import datetime
import concurrent.futures
import django
import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nongdjango.settings')
django.setup()

from server.nongapp.models import ProductPrice


class MoaSpider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Host': 'zdscxx.moa.gov.cn:8080',
            'Origin': 'http://zdscxx.moa.gov.cn:8080',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.url_conditions = 'http://zdscxx.moa.gov.cn:8080/nyb/updateFrequencyConditions'
        self.url_data = 'http://zdscxx.moa.gov.cn:8080/nyb/getFrequencyData'

    def parse_date(self, date_str):
        """解析日期字符串"""
        try:
            if len(date_str) == 6:  # 格式如 "202444"
                year = date_str[:4]
                week = date_str[4:]
                date_obj = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
                return date_obj.date()
            else:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception as e:
            print(f"日期解析错误 ({date_str}): {str(e)}")
            return datetime.now().date()

    def fetch_page(self, page, category):
        """获取单页数据"""
        try:
            data = {
                'page': page,
                'rows': '20',
                'type': '周度数据',
                'subType': '农产品批发价格',
                'level': '0',
                'time': '["2023-10","2024-10"]',
                'product': category  # 使用传入的类别
            }

            session = requests.Session()
            session.post(self.url_conditions, data=data, headers=self.headers)
            response = session.post(self.url_data, data=data, headers=self.headers)

            if response.status_code == 200:
                content = response.json()
                data_list = content['result']['pageInfo']['table']

                products = []
                for item in data_list:
                    try:
                        price = float(item['value'])
                        date_obj = self.parse_date(item['time'])

                        price_with_unit = f"{price}{item['unit']}"
                        print(f"时间: {date_obj}, 品类: {item['product']}, "
                              f"价格: {price_with_unit}, 地区: {item['area']}")

                        product = ProductPrice(
                            data=date_obj,
                            variety=item['product'],
                            price=price,
                            area=item['area'],
                            category=category  # 添加大类字段
                        )
                        products.append(product)
                    except Exception as e:
                        print(f"处理单条数据时出错: {str(e)}")
                        continue
                return products
            else:
                print(f"请求页面 {page} 失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            print(f"处理页面 {page} 时出错: {str(e)}")
            return []

    def run(self, category='水产品'):
        """运行爬虫"""
        print(f"开始爬取 {category} 数据...")
        all_products = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_page = {executor.submit(self.fetch_page, page, category): page
                              for page in range(1, 20)}

            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    products = future.result()
                    if products:
                        all_products.extend(products)
                        print(f"完成页面 {page} 的爬取，获取到 {len(products)} 条数据")
                except Exception as e:
                    print(f"获取页面 {page} 结果时出错: {str(e)}")
        if all_products:
            try:
                batch_size = 1000
                for i in range(0, len(all_products), batch_size):
                    batch = all_products[i:i + batch_size]
                    ProductPrice.objects.bulk_create(batch)
                    print(f"成功保存第 {i // batch_size + 1} 批数据，共 {len(batch)} 条")
                print(f"总共成功保存 {len(all_products)} 条数据到数据库")
            except Exception as e:
                print(f"保存数据到数据库时出错: {str(e)}")
        else:
            print("没有获取到任何数据")
        print("爬取完成。")


if __name__ == '__main__':
    spider = MoaSpider()
    spider.run(category='水产品')  # 这里可以修改为其他类别，如 '畜禽产品', '水果', '水产品'