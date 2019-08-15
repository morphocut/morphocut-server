# Build frontend
FROM node:10 AS build_frontend
WORKDIR /frontend
COPY morphocut_server/frontend .
RUN cd /frontend  && \
    npm ci && \
    npm run build

FROM debian:latest
FROM continuumio/miniconda3
WORKDIR /code
ENV FLASK_APP morphocut_server
ENV FLASK_RUN_HOST 0.0.0.0

RUN conda config --set notify_outdated_conda false && \
    conda create -yn morphocut python=3.7 numpy && \
    conda clean -y --all

# OpenCV depends on libglib2
RUN apt-get update --fix-missing && \
    apt-get install -y libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install git+https://github.com/morphocut/morphocut.git@0.0.1 && \
    pip install -e .

COPY --from=build_frontend /frontend/dist morphocut_server/frontend/dist

CMD ["flask", "run"]