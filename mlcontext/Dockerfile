FROM ubuntu:latest

ADD cenv_conda.txt cenv_conda.txt
ENV PATH=/miniconda3/bin:$PATH
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get update && \
    DEBIAN_FRONTEND="noninteractive" TZ="Europe/Berlin" apt-get install -y tzdata && \
    apt-get install ffmpeg libsm6 libxext6  -y && \
    apt-get install -y openslide-tools && \
    apt-get install -y python3-openslide && \
    apt install -y build-essential && \
    apt-get install -y apt-utils wget git && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh && \
    chmod +x Miniconda3-py38_4.8.3-Linux-x86_64.sh && \
    ./Miniconda3-py38_4.8.3-Linux-x86_64.sh -b -p /opt/miniconda3 && \
    ln -s /opt/miniconda3/bin/conda /usr/bin/conda && \
    export PATH="/miniconda3/bin:$PATH" && \
    conda create --name hpc_cenv --file=cenv_conda.txt python=3.8 && \
    chmod --recursive a+rw /opt/miniconda3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm /Miniconda3-py38_4.8.3-Linux-x86_64.sh && \
    . /opt/miniconda3/etc/profile.d/conda.sh && \
    conda activate hpc_cenv && \
    pip install --no-input torch torchvision torchaudio && \
    pip install openslide-python numba scikit-learn pytest
VOLUME /data
VOLUME /app
WORKDIR /app

CMD sleep 365d
