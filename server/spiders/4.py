import pymysql
import re

# 省份映射字典
province_map = {
    "京": "北京市", "津": "天津市", "沪": "上海市", "渝": "重庆市",
    "冀": "河北盛", "晋": "山西省", "辽": "辽宁省", "吉": "吉林省", "黑": "黑龙江省",
    "苏": "江苏省", "浙": "浙江省", "皖": "安徽省", "闽": "福建省", "赣": "江西省",
    "鲁": "山东省", "豫": "河南省", "鄂": "湖北省", "湘": "湖南省", "粤": "广东省",
    "桂": "广西壮族自治区", "琼": "海南省", "川": "四川省", "贵": "贵州省", "云": "云南省",
    "陕": "陕西省", "甘": "甘肃省", "青": "青海省", "宁": "宁夏省", "新": "新疆维吾尔自治区",
    "藏": "西藏自治区", "蒙": "内蒙古自治区", "台": "台湾省", "港": "香港特别行政区", "澳": "澳门特别行政区"
}

# 连接 MySQL
db = pymysql.connect(host="localhost", user="root", password="123456", database="nong")
cursor = db.cursor()

# 查询所有数据
cursor.execute("SELECT id, area FROM nongapp_productprice WHERE province IS NULL;")
data = cursor.fetchall()

# 解析 `area`，转换为标准省份
def parse_area(area):
    # 如果是国家或“全国平均”，直接返回
    if area in ["全国平均", "菲律宾", "新西兰", "澳洲", "美国", "泰国", "越南", "比利时", "南非", "秘鲁", "加拿大", "智利", "埃及", "希腊", "以色列", "摩洛哥", "印尼"]:
        return [area]

    # 处理省份组合
    provinces = []
    matches = re.findall(r'[京津沪渝冀晋辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川贵云陕甘青宁新藏蒙台港澳]', area)
    for abbr in matches:
        if abbr in province_map:
            provinces.append(province_map[abbr])

    return provinces

# 更新数据库
update_sql = "UPDATE nongapp_productprice SET province = %s WHERE id = %s"
for id, area in data:
    province = parse_area(area)
    if province:
        cursor.execute(update_sql, (province, id))

# 提交事务
db.commit()
cursor.close()
db.close()

print("转换后的省份数据已存入原表 `nongapp_productprice`！")
