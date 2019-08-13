FROM ubuntu:xenial

SHELL ["/bin/bash", "-c"]
ENTRYPOINT ["/bin/bash", "-c"]

RUN apt-get update --fix-missing && \
    apt-get install -y \
        git \
        bzip2 \
        ca-certificates \
        libglib2.0-0 libxext6 libsm6 libxrender1 \
        git mercurial subversion \
        wget \
        ffmpeg \
        openjdk-8-jre

# Install conda
ENV PATH /opt/conda/bin:$PATH
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    echo 'Downloading latest Miniconda3...' && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    conda update --all --yes && \
    conda config --set auto_update_conda False && \
    conda clean --all --yes

# Copy files and create conda environment
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD backend/environment.yml ./
RUN conda env create

ADD dist /usr/src/app/
ADD backend /usr/src/app/

EXPOSE 8001
CMD ["activate score-tube & exec /opt/conda/envs/score-tube/bin/gunicorn --bind=0.0.0.0:8001 --workers=2 --timeout 180 server:__hug_wsgi__"]
