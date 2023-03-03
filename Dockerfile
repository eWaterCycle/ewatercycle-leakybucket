# Python empty model with BMI v2.0
#
# Start from scratch:
# docker run --name test -d -i -t docker.io/condaforge/mambaforge /bin/sh
# docker exec -it test bash
#
# docker build -t  .
# docker run --name test -d -i -t testimage /bin/sh
# docker exec -it test bash
#

# Build with
#
#   docker build -t ewatercycle_defaultmodel-grpc4bmi .
#
#
# Run with

#   from grpc4bmi.bmi_client_docker import BmiClientDocker
#   model = BmiClientDocker('ewatercycle_defaultmodel:v1', work_dir='/tmp', delay=1)

# See https://github.com/mamba-org/micromamba-docker for details on using this base image
FROM mambaorg/micromamba:1.3.1

# Install conda-dependencies
RUN micromamba install -y -n base -c conda-forge python=3.10 esmvalcore && micromamba clean --all --yes
ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)

# Install ewatercycle
RUN pip install https://github.com/eWaterCycle/ewatercycle/archive/entrypoints.zip

# # Install grpc4bmi  # TODO: ensure compatible with above ewatercycle
# RUN pip install https://github.com/eWaterCycle/grpc4bmi/archive/refs/heads/latest-protobuf.zip

# Install defaultmodel plugin
COPY . /opt/ewatercycle_defaultmodel/
RUN pip install -e /opt/ewatercycle_defaultmodel/

# Start GRPC4BMI server
# Don't override micromamba's entrypoint as that activates conda
CMD run-bmi-server --name "ewatercycle_defaultmodel.default_bmi.DefaultBmi" --port 50051
