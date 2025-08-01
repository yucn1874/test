import json
import requests
import threading
import os
import sys
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nongdjango.settings')

import django

django.setup()

#from nongapp.models import ProductPrice  # 导入模型
from server.nongapp.models import ProductPrice

# 商品总列表
count = list()
# 线程锁
lock = threading.RLock()


# 解析网页函数
def url_parse(page):
    # 请求地址
    url = 'http://www.xinfadi.com.cn/getPriceData.html'
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.xinfadi.com.cn",
        "Origin": "http://www.xinfadi.com.cn",
        "Referer": "http://www.xinfadi.com.cn/priceDetail.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {
        "limit": "20",
        "current": page,
        "pubDateStartTime": "",
        "pubDateEndTime": "",
        "prodPcatid": "1190",  # 商品类id,1186是蔬菜，1187是水果，1189是畜禽产品，1190是水产品
        "prodCatid": "",
        "prodName": "",
    }

    # 最大重试次数
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # 添加随机延迟，避免请求过于规律
            time.sleep(random.uniform(1.0, 3.0))

            response = requests.post(url=url, headers=headers, data=data, timeout=15)

            # 检查响应状态码
            if response.status_code != 200:
                print(f"爬取第{page}页失败，状态码: {response.status_code}，正在重试...")
                retry_count += 1
                continue

            # 检查响应内容是否为空
            if not response.text.strip():
                print(f"爬取第{page}页失败，响应内容为空，正在重试...")
                retry_count += 1
                continue

            # 尝试解析JSON
            response_data = json.loads(response.text)

            # 检查是否包含预期的数据结构
            if 'list' not in response_data:
                print(f"爬取第{page}页失败，响应格式不正确，正在重试...")
                retry_count += 1
                continue

            # 获取商品信息
            product_list = response_data['list']

            # 直接处理数据而不是存储到全局列表
            for product in product_list:
                json_parse(product)

            print(f"成功爬取第{page}页，获取{len(product_list)}条数据")
            return True

        except json.JSONDecodeError as e:
            print(f"爬取第{page}页JSON解析错误: {str(e)}，正在重试...")
            retry_count += 1
            # 增加更长的延迟
            time.sleep(random.uniform(3.0, 5.0))

        except requests.exceptions.RequestException as e:
            print(f"爬取第{page}页请求错误: {str(e)}，正在重试...")
            retry_count += 1
            time.sleep(random.uniform(3.0, 5.0))

        except Exception as e:
            print(f"爬取第{page}页时出现未知错误: {str(e)}，正在重试...")
            retry_count += 1
            time.sleep(random.uniform(3.0, 5.0))

    print(f"爬取第{page}页失败，已达到最大重试次数")
    return False


# 解析json函数
def json_parse(product):
    try:
        # 提取价格并正确转换
        avg_price_str = product['avgPrice']
        # 检查价格格式并转换为浮点数
        try:
            # 直接转换为浮点数，不需要去掉小数点
            avg_price = float(avg_price_str)
            # 单位转换：元/斤 -> 元/公斤 (乘以2)
            converted_price = avg_price * 2
            #print(f"原始价格: {avg_price_str} 元/斤 -> 转换后: {converted_price} 元/公斤")
        except ValueError:
            #print(f"价格格式错误: {avg_price_str}")
            return

        # 提取日期并处理时间部分
        pub_date = product['pubDate'].split(' ')[0]  # 只取日期部分
        date_obj = datetime.strptime(pub_date, '%Y-%m-%d')  # 根据实际日期格式调整

        dic = {
            'area': product['place'],  # 产地
            'variety': product['prodName'],  # 品种名称
            'price': converted_price,  # 已转换为元/公斤的价格
            'unit': '元/公斤',  # 单位设置为元/公斤
            'date': date_obj  # 日期
        }

        with lock:
            # 将商品信息添加到商品总列表中
            count.append(dic)
            # 保存到数据库
            save_to_database(dic)

    except Exception as e:
        print(f"处理数据时出错: {str(e)}")

def save_to_database(product_data):
    """将爬取的数据保存到数据库"""
    try:
        product = ProductPrice(
            variety=product_data['variety'],
            area=product_data['area'],
            price=product_data['price'],
            data=product_data['date'],
            category='水产品'  # 根据需要设置类别
        )
        product.save()
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")


def run(start_page=1, end_page=5000, max_workers=3):
    """
    爬取指定页数的数据
    参数:
    - start_page: 起始页码
    - end_page: 结束页码
    - max_workers: 最大线程数
    """
    total_pages = end_page - start_page + 1
    success_count = 0

    print(f"开始爬取从第{start_page}页到第{end_page}页的数据，共{total_pages}页")

    # 使用线程池管理线程
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用tqdm显示进度条
        with tqdm(total=total_pages) as pbar:
            # 分批次提交任务
            batch_size = 10  # 每批次处理的页数，减小批次大小
            for batch_start in range(start_page, end_page + 1, batch_size):
                batch_end = min(batch_start + batch_size - 1, end_page)

                # 提交当前批次的任务
                futures = {executor.submit(url_parse, page): page for page in range(batch_start, batch_end + 1)}

                # 等待当前批次完成
                for future in futures:
                    page = futures[future]
                    result = future.result()
                    if result:
                        success_count += 1
                    pbar.update(1)

                # 批次间暂停，避免请求过于频繁，增加暂停时间
                if batch_end < end_page:
                    pause_time = random.uniform(5.0, 10.0)
                    print(f"完成批次爬取，暂停{pause_time:.2f}秒后继续...")
                    time.sleep(pause_time)

    print(f"爬取完成，成功爬取{success_count}页数据，共{len(count)}条记录")


if __name__ == '__main__':
    # 可以设置起始页、结束页和最大线程数
    # 减少线程数和批次大小，增加请求间隔
    run(start_page=3001, end_page=3384, max_workers=3)