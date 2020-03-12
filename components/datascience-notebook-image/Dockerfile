# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

ARG BASE_IMAGE=jupyter/datascience-notebook:1386e2046833

FROM $BASE_IMAGE

ARG TF_SERVING_VERSION=0.0.0
ARG NB_USER=jovyan

# TODO: User should be refactored instead of hard coded jovyan

USER root

ENV DEBIAN_FRONTEND noninteractive

ENV NB_USER $NB_USER

ENV NB_UID 1000
ENV HOME /home/$NB_USER
ENV NB_PREFIX /


# Use bash instead of sh
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -yq --no-install-recommends \
  apt-transport-https \
  build-essential \
  bzip2 \
  ca-certificates \
  curl \
  g++ \
  git \
  gnupg \
  graphviz \
  locales \
  lsb-release \
  openssh-client \
  sudo \
  unzip \
  vim \
  wget \
  zip \
  emacs \
  python3-pip \
  python3-dev \
  python3-setuptools \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install Nodejs for jupyterlab-manager
RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
RUN apt-get update && apt-get install -yq --no-install-recommends \
  nodejs \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV DOCKER_CREDENTIAL_GCR_VERSION=1.4.3
RUN curl -LO https://github.com/GoogleCloudPlatform/docker-credential-gcr/releases/download/v${DOCKER_CREDENTIAL_GCR_VERSION}/docker-credential-gcr_linux_amd64-${DOCKER_CREDENTIAL_GCR_VERSION}.tar.gz && \
    tar -zxvf docker-credential-gcr_linux_amd64-${DOCKER_CREDENTIAL_GCR_VERSION}.tar.gz && \
    mv docker-credential-gcr /usr/local/bin/docker-credential-gcr && \
    rm docker-credential-gcr_linux_amd64-${DOCKER_CREDENTIAL_GCR_VERSION}.tar.gz && \
    chmod +x /usr/local/bin/docker-credential-gcr

# Install AWS CLI
RUN curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "/tmp/awscli-bundle.zip" && \
    unzip /tmp/awscli-bundle.zip && ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws && \
    rm -rf ./awscli-bundle

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Create NB_USER user with UID=1000 and in the 'users' group
# but allow for non-initial launches of the notebook to have
# $HOME provided by the contents of a PV
RUN chown -R ${NB_USER}:users /usr/local/bin && \
    mkdir -p $HOME

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb https://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk kubectl

# Install Tini - used as entrypoint for container
RUN cd /tmp && \
    wget --quiet https://github.com/krallin/tini/releases/download/v0.18.0/tini && \
    echo "12d20136605531b09a2c2dac02ccee85e1b874eb322ef6baf7561cd93f93c855 *tini" | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ | sh

# Granting $NB_USER sudo access
RUN echo "${NB_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook

# NOTE: Beyond this point be careful of breaking out
# or otherwise adding new layers with RUN, chown, etc.
# The image size can grow significantly.

# Install base python3 packages
RUN pip3 --no-cache-dir install \
    jupyter-console==6.0.0 \
    xgboost \
    git+https://github.com/kubeflow/fairing@a9bb9d5cc1c9f1d75efa31198ddbdccfe176b7bf

COPY --chown=jovyan:users requirements.txt /tmp

# Install extra Python packages
RUN apt-get update && apt-get install -yq --no-install-recommends \
  swig \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*
RUN conda install --yes \
  "boto3=1.10.14" \
  "featuretools=0.12.0" \
  "pip=19.3.1" \
  "git" \
  "nodejs" \
  "minio"
RUN pip --no-cache-dir install \
  git+https://github.com/automl/auto-sklearn.git@47bbd11c02d72a350ea4fd8dc89d46935b7bc04d \
  git+https://github.com/nteract/papermill.git@17d4bbb3960c30c263bca835e48baf34322a3530
RUN conda install --yes \
  pytorch torchvision cpuonly -c pytorch

# Platiagro SDK
RUN pip --no-cache-dir install git+https://github.com/platiagro/sdk.git@master

# Install Jupyter Notebook
RUN pip --no-cache-dir install git+https://github.com/platiagro/notebook.git@platiagro 

# Install Jupyter Lab
RUN cd /opt && \
    wget -q https://github.com/platiagro/jupyterlab/archive/platiagro.zip && \
    unzip -q platiagro.zip && \
    rm platiagro.zip && \
    cd jupyterlab-platiagro && \
    pip --no-cache-dir install -e . && \
    jlpm install && \
    jlpm run build 

RUN chown -R ${NB_USER}:users $HOME/.local

# Configure container startup
EXPOSE 8888

USER jovyan

# Configure Minio credentials
RUN aws --profile default configure set aws_access_key_id "minio" && \
  aws --profile default configure set aws_secret_access_key "minio123" && \
  aws configure set region ""
ENV BOTO3_ENDPOINT_URL=http://minio-service.kubeflow:9000
ENV AWS_DEFAULT_REGION=minio-service
ENV AWS_ACCESS_KEY_ID=minio
ENV AWS_SECRET_ACCESS_KEY=minio123

ENTRYPOINT ["tini", "--"]
CMD ["sh","-c", "jupyter lab --dev-mode --notebook-dir=/home/${NB_USER} --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]
