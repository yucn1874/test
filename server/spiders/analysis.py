import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import mysql.connector
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("开始农产品价格数据分析...")

# 连接数据库
try:
    print("连接MySQL数据库...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="nongdata"
    )

    # 读取数据
    query = "SELECT * FROM nongapp_productprice"
    print(f"执行SQL查询: {query}")
    df = pd.read_sql(query, conn)
    conn.close()

    print(f"数据加载成功，共{len(df)}行")

    # 数据预处理
    print("\n数据预处理...")
    # 转换日期列
    df['date'] = pd.to_datetime(df['data'])
    # 检查并处理缺失值
    missing_values = df.isnull().sum()
    print(f"缺失值统计:\n{missing_values}")

    # 检查并处理异常值 (例如: 价格为负或异常高的值)
    price_mean = df['price'].mean()
    price_std = df['price'].std()
    price_min = max(0, price_mean - 3 * price_std)  # 下限不低于0
    price_max = price_mean + 3 * price_std

    print(f"价格范围: {price_min:.2f} - {price_max:.2f} 元/公斤")
    df_cleaned = df[(df['price'] >= price_min) & (df['price'] <= price_max)]
    print(f"清洗后数据: {len(df_cleaned)}行 (移除了{len(df) - len(df_cleaned)}行异常值)")

    # 基本统计分析
    print("\n基本统计量:")
    price_stats = df_cleaned['price'].describe()
    print(price_stats)

    # 创建输出目录
    output_dir = "data_analysis_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 按品种分组统计
    print("\n按品种分组统计...")
    variety_stats = df_cleaned.groupby('variety').agg({
        'price': ['count', 'mean', 'min', 'max', 'std']
    }).reset_index()
    variety_stats.columns = ['variety', 'count', 'avg_price', 'min_price', 'max_price', 'stddev_price']
    variety_stats = variety_stats.sort_values('count', ascending=False)

    print(f"共有{len(variety_stats)}个不同品种")
    print("\n数量最多的10个品种:")
    print(variety_stats.head(10))

    # 保存到CSV
    variety_stats.to_csv(f"{output_dir}/variety_statistics.csv", index=False, encoding='utf-8-sig')

    # 2. 按产地分组统计
    print("\n按产地分组统计...")
    area_stats = df_cleaned.groupby('area').agg({
        'price': ['count', 'mean', 'min', 'max']
    }).reset_index()
    area_stats.columns = ['area', 'count', 'avg_price', 'min_price', 'max_price']
    area_stats = area_stats.sort_values('count', ascending=False)

    print(f"共有{len(area_stats)}个不同产地")
    print("\n数量最多的10个产地:")
    print(area_stats.head(10))

    # 保存到CSV
    area_stats.to_csv(f"{output_dir}/area_statistics.csv", index=False, encoding='utf-8-sig')

    # 3. 时间趋势分析
    print("\n时间趋势分析...")
    time_trend = df_cleaned.groupby(df_cleaned['date'].dt.date).agg({
        'price': 'mean',
        'id': 'count'
    }).reset_index()
    time_trend.columns = ['date', 'avg_price', 'count']
    time_trend = time_trend.sort_values('date')

    print("\n时间价格趋势(前10天):")
    print(time_trend.head(10))

    # 保存到CSV
    time_trend.to_csv(f"{output_dir}/time_trend.csv", index=False)

    # 4. 季节性分析
    print("\n季节性分析...")
    df_cleaned['month'] = df_cleaned['date'].dt.month
    df_cleaned['year'] = df_cleaned['date'].dt.year
    df_cleaned['day_of_week'] = df_cleaned['date'].dt.dayofweek

    monthly_trend = df_cleaned.groupby('month').agg({
        'price': 'mean',
        'id': 'count'
    }).reset_index()
    monthly_trend.columns = ['month', 'avg_price', 'count']

    print("\n月度价格趋势:")
    print(monthly_trend)

    # 保存到CSV
    monthly_trend.to_csv(f"{output_dir}/monthly_trend.csv", index=False)

    # 5. 价格波动分析
    print("\n价格波动分析...")
    # 计算变异系数(CV)
    variety_stats['cv'] = variety_stats['stddev_price'] / variety_stats['avg_price']
    # 筛选样本量足够的品种
    volatility = variety_stats[variety_stats['count'] > 10].sort_values('cv', ascending=False)

    print("\n价格波动最大的10个品种:")
    print(volatility.head(10))

    # 保存到CSV
    volatility.to_csv(f"{output_dir}/price_volatility.csv", index=False, encoding='utf-8-sig')

    # 6. 相关性分析
    print("\n相关性分析...")
    # 选择热门品种
    top_varieties = variety_stats.head(10)['variety'].tolist()

    # 创建透视表，行为日期，列为品种，值为价格
    pivot_df = pd.pivot_table(
        df_cleaned[df_cleaned['variety'].isin(top_varieties)],
        values='price',
        index='date',
        columns='variety',
        aggfunc='mean'
    )

    # 计算相关系数
    correlation = pivot_df.corr()
    print("\n热门品种价格相关性矩阵:")
    print(correlation)

    # 保存到CSV
    correlation.to_csv(f"{output_dir}/price_correlation.csv", encoding='utf-8-sig')

    # 7. 简单价格预测 (使用移动平均线)
    print("\n简单价格预测...")
    # 选择一个热门品种
    if len(top_varieties) > 0:
        target_variety = top_varieties[0]
        print(f"为品种 '{target_variety}' 构建简单预测模型")

        # 获取该品种的时间序列数据
        variety_data = df_cleaned[df_cleaned['variety'] == target_variety]
        variety_time_series = variety_data.groupby(variety_data['date'].dt.date).agg({
            'price': 'mean'
        }).reset_index()
        variety_time_series = variety_time_series.sort_values('date')

        # 计算移动平均线 (7天和30天)
        if len(variety_time_series) >= 7:
            variety_time_series['MA7'] = variety_time_series['price'].rolling(window=7).mean()
        if len(variety_time_series) >= 30:
            variety_time_series['MA30'] = variety_time_series['price'].rolling(window=30).mean()

        # 预测未来7天价格 (使用最近7天平均值)
        last_date = variety_time_series['date'].max()
        last_price = variety_time_series['price'].iloc[-1]

        if len(variety_time_series) >= 7:
            last_7_avg = variety_time_series['price'].tail(7).mean()
            print(f"最近价格: {last_price:.2f} 元/公斤")
            print(f"最近7天平均价格: {last_7_avg:.2f} 元/公斤")

            # 创建未来7天的预测
            future_dates = [last_date + timedelta(days=i + 1) for i in range(7)]
            future_prices = [last_7_avg] * 7  # 简单预测：使用最近7天平均值

            future_df = pd.DataFrame({
                'date': future_dates,
                'predicted_price': future_prices
            })

            print("\n未来7天价格预测:")
            print(future_df)

            # 保存预测结果
            future_df.to_csv(f"{output_dir}/{target_variety}_price_prediction.csv", index=False)

    # 数据可视化
    print("\n生成数据可视化图表...")

    # 1. 价格时间趋势图
    plt.figure(figsize=(15, 6))
    plt.plot(time_trend['date'], time_trend['avg_price'], marker='o', linestyle='-')
    plt.title('农产品平均价格时间趋势')
    plt.xlabel('日期')
    plt.ylabel('平均价格 (元/公斤)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/price_trend.png")
    plt.close()

    # 2. 热门品种平均价格对比
    plt.figure(figsize=(12, 8))
    top10_varieties = variety_stats.head(10)
    bars = plt.barh(top10_varieties['variety'], top10_varieties['avg_price'], color='skyblue')
    plt.title('热门农产品平均价格对比')
    plt.xlabel('平均价格 (元/公斤)')
    plt.ylabel('品种')
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # 在柱状图上添加数值标签
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height() / 2, f'{width:.2f}',
                 ha='left', va='center')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/variety_price_comparison.png")
    plt.close()

    # 3. 月度价格季节性变化
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_trend['month'], monthly_trend['avg_price'], marker='o', linestyle='-', color='green')
    plt.title('农产品价格季节性变化')
    plt.xlabel('月份')
    plt.ylabel('平均价格 (元/公斤)')
    plt.xticks(range(1, 13))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/seasonal_price_change.png")
    plt.close()

    # 4. 价格相关性热力图
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('热门农产品价格相关性矩阵')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/price_correlation.png")
    plt.close()

    # 5. 如果有预测结果，绘制预测图
    if 'future_df' in locals() and len(variety_time_series) > 0:
        plt.figure(figsize=(15, 6))
        # 绘制历史价格
        plt.plot(variety_time_series['date'], variety_time_series['price'],
                 label='历史价格', color='blue')

        # 绘制移动平均线
        if 'MA7' in variety_time_series.columns:
            plt.plot(variety_time_series['date'], variety_time_series['MA7'],
                     label='7天移动平均', color='orange', linestyle='--')
        if 'MA30' in variety_time_series.columns:
            plt.plot(variety_time_series['date'], variety_time_series['MA30'],
                     label='30天移动平均', color='green', linestyle='-.')

        # 绘制预测价格
        plt.plot(future_df['date'], future_df['predicted_price'],
                 label='预测价格', color='red', linestyle='--', marker='o')

        plt.title(f'{target_variety} 价格趋势与预测')
        plt.xlabel('日期')
        plt.ylabel('价格 (元/公斤)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/{target_variety}_price_prediction.png")
        plt.close()

    print(f"\n分析完成！结果已保存到 {output_dir} 目录")

except Exception as e:
    import traceback

    print(f"发生错误: {str(e)}")
    traceback.print_exc()