FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime
FROM python:3.10.1

RUN apt update && apt upgrade -y 
RUN apt-get update && apt-get upgrade -y 
RUN apt-get install iputils-ping -y

ADD build/requirements.txt .
RUN pip uninstall -y -r requirements.txt --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

ADD src/ ./satiscribble-ai/src
ADD tests/ ./satiscribble-ai/tests
WORKDIR /satiscribble-ai/src
