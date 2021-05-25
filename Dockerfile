FROM debian:buster
# We need a GitHub access token to clone the NanoFASE repo
ARG GITHUB_ACCESS_TOKEN
ARG GITHUB_UN
ARG GITHUB_PAS


# Install required packages
RUN apt-get update && \
    apt install -y gcc \
        g++ \
        gfortran \
        git \
        make \
        wget \
        libnetcdf-dev \
        libnetcdff-dev


# Install python 3.8
RUN apt-get update && apt-get upgrade -y
RUN apt install -y build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev wget \
    curl \
    libbz2-dev \
    liblzma-dev


RUN curl -O https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
RUN tar -xf Python-3.8.0.tar.xz
RUN cd Python-3.8.0 && \
    ./configure  --enable-optimizations
RUN cd Python-3.8.0 && \
    make && \
    make altinstall


RUN apt update && \
    apt install -y python3-pip


RUN cd /
# Clone NanoFASE repo, create Makefile and a few required directories
RUN git clone -b 0.0.1 --recurse-submodules https://${GITHUB_ACCESS_TOKEN}@github.com/nerc-ceh/nanofase.git && \
    cd nanofase && \
    cp Makefile.example Makefile && \
    mkdir ./bin && \
    mkdir ./log && \
    mkdir ./data && \
    mkdir ./data/output && \
    make release

RUN apt install -y  python-numpy gdal-bin libgdal-dev

RUN mkdir nanofase-api

COPY ./requirements /nanofase-api

RUN python3.8 -m pip install -r nanofase-api/requirements

COPY ./src/ /nanofase-api/src

EXPOSE 5000

#RUN cd /nanofase-api
ENV PYTHONPATH='nanofase-api'

ENV DATA_PATH='/nanofase-api/src/data'
ENV MODEL_DATA='/nanofase-api/src/data/model/data/constants/thames_tio2_2015/'
ENV MODEL_VARS='/nanofase-api/src/data/model/data/model_vars.yaml'
ENV MODEL_CONFIG='/nanofase-api/src/data/config.nml'
ENV MODEL_PATH='/nanofase/bin/main'
ENV GDAL_DATA='/usr/share/gdal'

CMD ["python3.8", "nanofase-api/src/app.py" ]
