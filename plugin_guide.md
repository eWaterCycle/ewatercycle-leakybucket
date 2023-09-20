
# Plugin Guide

The following steps are outlined in this guide:

1. Implementing the Basic Model Interface
2. Wrapping your BMI in the eWaterCycle interface
3. Accessing your model through grpc4bmi
4. Put your model in a container and add it to eWaterCycle 📦

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

[Notebook 01](notebooks/01_raw_bmi.ipynb) is available to showcase the BMI, and can be used to test things while developing your plugin.

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

[Notebook 02](notebooks/02_ewatercycle_local_model.ipynb) is available to try the LeakyBucket local model, and can be used to test things while developing your plugin.

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

This is demonstrated in [notebook 03](notebooks/03_local_grpc4bmi.ipynb).

If nothing went wrong, runnign the following command in your terminal (with the eWaterCycle environment active) will start the grpc4bmi server:

```sh
run-bmi-server --name "mymodel.bmi.MyModelBmi" --port 55555 --debug
```

## 4. Put your model in a container and add it to eWaterCycle 📦

### Containerizing your model
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

The LocalContainerLeakyBucket model is demonstrated in [notebook 04](notebooks/04_containerized_model.ipynb)

### Sharing the container using a registry

To allow others to use the containerized model, the container has to be uploaded to a registry.
One such registry is the Github container registry (ghcr).

To see how to get an access token and upload to the ghcr, see [their guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

The leaky bucket image has been pushed to `ghcr.io/ewatercycle/leakybucket`, with a tag corresponding to the current version of this repository.

Instead of using the local container name, the `ContainerImage` class is given the `ghcr.io` location:

```py
class LeakyBucket(ContainerizedModel, LeakyBucketMixins):
    """The LeakyBucket eWaterCycle model, with the Container Registry docker image."""
    bmi_image: ContainerImage = ContainerImage(
        "ghcr.io/ewatercycle/leakybucket:0.0.1"
    )
```

### Register the model as eWaterCycle model entrypoint (plugin)

Finally, the model can be registered as a plugin so that eWaterCycle can find it.
This is done in the `pyproject.toml` file:

```toml
# This registers the plugin such that it is discoverable by eWaterCycle
[project.entry-points."ewatercycle.models"]
LeakyBucket = "leakybucket.ewatercycle_models:LeakyBucket"
```

Here you would replace the leaky bucket names with the correct model and class name of your own model.

Now you can do:

```py
from ewatercycle.models import LeakyBucket
```

And run the model in eWaterCycle! 🚀

For a working example, see [notebook 05](notebooks/05_finished_ewatercycle_plugin.ipynb)

## Further steps

After finishing the previous steps, you can upload the finished package to pypi.org.
This will allow others to install it into their eWaterCycle installation using (for example):
```sh
pip install ewatercycle-mymodel
```
