# test
农产品价格数据分析可视化系统友好
# 农产品数据分析可视化

## 项目介绍

1. 基于vue3 + django rest framework + mysql


```shell
# 创建数据库持久化目录
# mkdir /data
#docker compose up
```

## 浏览器打开

<http://localhost>

## 开发环境

```shell
python 3.12
mysql 8.0
django 5.1.4
node v22.12.0
```

## 部署安装

1. 拉取代码


2. 初始化后端

```shell
cd produce/server
pip3 install -r requirements.txt  //各种库
python3 manage.py makemigrations
python3 manage.py migrate
```

3. 启动项目

```shell
//后端
cd produce/server
python3 manage.py runserver
//前端
cd produce/web
npm run dev
```

4. nginx 反向代理

```conf
location / {
  root /beenote/web/dist;
  index  index.html index.htm;
}

location /api {
  proxy_pass  http://localhost:8000;
  proxy_redirect     off;
  proxy_set_header   Host             $host;
  proxy_set_header   X-Real-IP        $remote_addr;
  proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
  proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
  proxy_max_temp_file_size 0;
  proxy_connect_timeout      90;
  proxy_send_timeout         900;
  proxy_read_timeout         900;
  proxy_buffer_size          34k;
  proxy_buffers              4 32k;
  proxy_busy_buffers_size    64k;
  proxy_temp_file_write_size 64k;
}
```

## 后台地址

```url
<http://ip:8000/admin>
```

## 默认用户名密码

```conf
用户名：yucn
密码： nong123456
```

## License

[996ICU License](LICENSE)  
