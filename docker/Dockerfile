ARG IMAGE=ubuntu:20.04
FROM ${IMAGE}

LABEL org.opencontainers.image.authors="Dmitrii Cherginets cherginetsda@yandex.ru 2024-03-24"

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get upgrade -y

# Timezone Configuration
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ADD https://NTO-test:glpat-cnZ9sLQmPkgvu2EivBxR@gitlab.com/lab_449/nto/final_2023_2024/VideoStitching.git /opt/VideoStatching
# ADD https://NTO-test:glpat-cnZ9sLQmPkgvu2EivBxR@gitlab.com/lab_449/nto/final_2023_2024/nto_final_participant.git /opt/nto_final

COPY ./requirements.txt /tmp

RUN apt-get install vim wget git screen build-essential cmake g++ libopencv-dev software-properties-common \
    mesa-utils libcanberra-gtk-module libcanberra-gtk3-module -y

RUN add-apt-repository ppa:deadsnakes/ppa && apt update
RUN apt install python3.10 python3.10-distutils python3.10-dev -y
RUN wget https://bootstrap.pypa.io/pip/get-pip.py
RUN python3.10 get-pip.py
RUN python3.10 -m pip install -r /tmp/requirements.txt
 
# Participent package
RUN python3.10 -m pip install nto --index-url https://nto-participant-token:glpat-DJ6-zTiqix24zLJkw4fL@gitlab.com/api/v4/projects/56130233/packages/pypi/simple 

# RUN cd /opt/nto_final && pip3 install -e .
# RUN cd /opt/VideoStatching && pip3 install -e .
