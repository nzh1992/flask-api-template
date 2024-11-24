FROM python:3.8-bullseye

# 替换deb镜像源
RUN apt install apt-transport-https ca-certificates
RUN sed -i 's#http://deb.debian.org#https://mirrors.163.com#g' /etc/apt/sources.list

# 安装系统依赖
RUN apt update
RUN apt install -y python3-dev gcc

WORKDIR /project

COPY . .

# 安装项目依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建uwsgi日志文件
RUN touch /var/log/uwsgi.log

CMD ["uwsgi", "uwsgi.config.ini"]
