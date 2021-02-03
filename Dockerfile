# 建立 python3.7 环境
FROM python:3.7

# 镜像作者
MAINTAINER shentu119

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

COPY pip.conf /root/.pip/pip.conf

# 创建 项目 文件夹
RUN mkdir -p /home/shentu/micro_web

# 将 该 文件夹设为工作目录
WORKDIR /home/shentu/micro_web

 # 将当前目录加入到工作目录中（. 表示当前目录）
ADD ./ /home/shentu/micro_web

 # 更新pip版本
RUN /usr/local/bin/python -m pip install --upgrade pip

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt

 # 去除windows系统编辑文件中多余的\r回车空格
RUN sed -i "s/\r//" ./start.sh

 # 给start.sh可执行权限
RUN chmod +x ./start.sh

CMD ./start.sh