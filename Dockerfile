# Base container for eWaterCycle BMI models written in Python
#
# Activates a default conda base environment with micromamba. While it may not
# always be necessary, many hydrological models may at some point want to
# install conda dependencies, which can be a struggle. This image should provide
# a good starting point.
#
# For details on the base image, see
# https://github.com/mamba-org/micromamba-docker
#
#
# To build the image, run
#
#   docker build --tag defaultmodel-grpc4bmi:v0.0.1 .
#
# If you use podman, you may need to add `--format docker`
#
#   docker build --format docker --tag defaultmodel-grpc4bmi:v0.0.1 .
#
# To talk to the model from outside the container, use grpc4bmi client
#
#   from grpc4bmi.bmi_client_docker import BmiClientDocker
#   model = BmiClientDocker('defaultmodel-grpc4bmi:v0.0.1', work_dir='/tmp', delay=1)
#
# To debug the container, you can override the grpc4bmi command
#
#   docker run --tty --interactive defaultmodel-grpc4bmi:v0.0.1 bash
#
# This will spawn a new bash terminal running inside the docker container

FROM mambaorg/micromamba:1.3.1


# Install Python + additional conda-dependencies,
# Here I added cartopy as an example
RUN micromamba install -y -n base -c conda-forge python=3.10 cartopy && \
    micromamba clean --all --yes


# Make sure the conda environment is activated for the remaining build
# instructions below
ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)


# Install GRPC4BMI
RUN pip install https://github.com/eWaterCycle/grpc4bmi/archive/refs/heads/latest-protobuf.zip


# Install ewatercycle_defaultmodel.default_bmi
# Note that the [plugin] dependencies (ewatercycle/emsvaltool) are not required
COPY . /opt/ewatercycle_defaultmodel
RUN pip install -e /opt/ewatercycle_defaultmodel/


# Default command should be to run GRPC4BMI server
# Don't override micromamba's entrypoint as that activates conda!
CMD run-bmi-server --name "ewatercycle_defaultmodel.default_bmi.DefaultBmi" --port 50051
