FROM cone387/seeme
MAINTAINER cone

LABEL project="common-task-system"
USER root

ENV PROJECT_DIR /home/admin/common-task-system

WORKDIR $PROJECT_DIR
copy ./task_server $PROJECT_DIR
copy ./requirements.txt $PROJECT_DIR
# 不能使用copy ./* 这是COPY命令的一个bug， 会导致复制过去的路径混乱


WORKDIR $PROJECT_DIR

RUN pip install -r requirements.txt

ENTRYPOINT python3 manage.py runserver 0.0.0.0:9000