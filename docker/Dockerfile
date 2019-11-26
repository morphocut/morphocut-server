# Build frontend
FROM node:10 AS build_frontend
WORKDIR /frontend
COPY morphocut_server/frontend .
RUN cd /frontend  && \
    npm ci && \
    npm run build

FROM continuumio/miniconda3
WORKDIR /code

# OpenCV depends on libglib2
# supervisor is required to run multiple processes in parallel
RUN apt-get update --fix-missing && \
    apt-get install -y libglib2.0-0 supervisor netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY docker/run.sh docker/wait-for environment.yml docker/activate ./

# Install conda env
RUN conda config --set notify_outdated_conda false && \
    conda env create -f environment.yml && \
    conda clean -y --all

COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install the application
COPY versioneer.py setup.py setup.cfg MANIFEST.in README.md ./
COPY tests ./tests
COPY morphocut_server ./morphocut_server
COPY migrations ./migrations
RUN . /opt/conda/etc/profile.d/conda.sh && \
    conda activate morphocut && \
    pip install -e .

COPY --from=build_frontend /frontend/dist morphocut_server/frontend/dist

COPY docker/config_docker.py morphocut_server/
CMD ["/code/run.sh"]