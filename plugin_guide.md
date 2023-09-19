
# Plugin Guide

The following steps are outlined in this guide:

1. Creating a Basic Model Interface (BMI) for your model.
2. Wrapping your model's BMI in an eWaterCycle "LocalModel".
3. Accessing your model's BMI through grpc4bmi.
4. Creating a docker container for your grpc4bmi model, and adding it to eWaterCycle.

## 1. Implementing the Basic Model Interface
For eWaterCycle a model requires a [Basic Model Interface](https://bmi.readthedocs.io/en/stable/). Here there are two options:

  - You want to add an existing model with a BMI to eWaterCycle
  - You want to develop a completely new model

### 1A New Model
The file `src/leakybucket/leakybucket_bmi.py` holds the implemented BMI for the "leaky bucket" model.
This model is a lumped hydrological model, with just a single "bucket" for the entire catchment, to simplify this example.

Forcing is generated using the eWaterCycle, in this case the `GenericLumpedForcing` generator. 
For distributed models, a `GenericDistributedForcing` class is available.

To implement your model, modify the BMI to incorporate the processes you want to add or change.

[Notebook 01](01_raw_bmi.ipynb) is available to showcase the BMI, and can be used to test things while developing your plugin.

### 1B Existing Model

If you already have a model with a BMI, you will either need to create an eWaterCycle forcing class, or make your model compatible with the eWaterCycle generic forcing.

Examples are available in the eWaterCycle repository under:

`ewatercycle/src/ewatercycle/plugins/*model_name*/forcing.py`

## 2. Wrapping your BMI in the eWaterCycle interface
To be able to interface your model in eWaterCycle, you need to wrap it in an eWaterCycle model class.

For local debugging, this can be the `LocalModel`. This will be stuctured like the following:

```py
from ewatercycle.base.model import LocalModel, eWaterCycleModel
from mymodel.bmi import MyModelBmi
from bmipy import Bmi

# This "mix-in" class implements the eWaterCycle interface, and can be reused.
class MyPluginMixins(eWaterCycleModel):
    forcing: GenericLumpedForcing  # Models (almost) always require forcing.

    parameter_set: ParameterSet  # If the model has a parameter set (e.g. routing).

    _config: dict = {  # _config holds model configuration settings:
        "forcing_file": "",
        "model_setting_1": 0.05,
    }

    @model_validator(mode="after")
    def _update_config(self):
        ... # Update the config, e.g., by adding the forcing directory.
        return self

    def _make_cfg_file(self, **kwargs) -> Path:
        """Write model configuration file."""
        ... # Write the config to a file to pass it to your model BMI.

class LocalBmiMyPlugin(LocalModel, MyPluginMixins):
    # The local model uses a local BMI class
    bmi_class: Type[Bmi] = MyModelBmi
```

The LeakyBucket implementation can be found in `src/leakybucket/ewatercycle_models.py`.
This is a good starting point to build upon.

[Notebook 02](02_ewatercycle_local_model.ipynb) is available to try the LeakyBucket local model, and can be used to test things while developing your plugin.

## 3. Accessing your model through grpc4bmi
In eWaterCycle we want to run models in containers.
To be able to communicate with the BMI inside the container, we need to use the [grpc4bmi](https://github.com/eWaterCycle/grpc4bmi) package.

If everything was implemented correctly up to now, this should not be a problem.
You can try the following snippet:

```py
from grpc4bmi.bmi_grpc_server import BmiServer
from mymodel.bmi import MyModelBmi

server = BmiServer(MyModelBmi(), debug=True)  # with debug it should 

print(server.getComponentName(0,0))
```
should return*:
```
name: "mymodel"
```
\* (if `MyModelBmi.get_component_name` is available before initialization).

This is demonstrated in [notebook 03](03_local_grpc4bmi.ipynb).

If nothing went wrong, runnign the following command in your terminal (with the eWaterCycle environment active) will start the grpc4bmi server:

```sh
run-bmi-server --name "mymodel.bmi.MyModelBmi" --port 55555 --debug
```

## 4. Putting your model in a container
To be able to share your model, and have it work as an easily installable ewatercycle plugin, you need to create a container for your model.

A `Dockerfile` is available in this repository for the LeakyBucket model, and can be modified to fit your own model. Note that [Docker](https://www.docker.com/) is required for this.

To build the container locally, do:

```sh
docker build . -t "leakybucket"
```
Where `-t "name"` sets the "tag". 

To start the container do:

```sh
docker run leakybucket
```

This should start the container and print the GRPC server's port to the terminal.

The container tag can then be used to create a (local) containerized model:

```py
class LocalContainerLeakyBucket(ContainerizedModel, LeakyBucketMixins):
    bmi_image: ContainerImage = ContainerImage("leakybucket")
```

