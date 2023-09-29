import json
from pathlib import Path
from ewatercycle.base.model import ContainerizedModel, eWaterCycleModel
from ewatercycle.base.forcing import GenericLumpedForcing
from pydantic import model_validator
from ewatercycle.container import ContainerImage


class LeakyBucketMethods(eWaterCycleModel):
    """Common arguments and methods for the eWatercycle LeakyBucket model."""
    forcing: GenericLumpedForcing  # The model requires forcing.

    _config: dict = {
        "forcing_file": "",
        "precipitation_file": "",
        "leakiness": 0.05,
    }

    @model_validator(mode="after")
    def _update_config(self):
        assert self.forcing.directory is not None
        self._config["precipitation_file"] = str(
            self.forcing.directory / self.forcing.pr
        )
        self._config["temperature_file"] = str(
            self.forcing.directory / self.forcing.tas
        )
        return self

    def _make_cfg_file(self, **kwargs) -> Path:
        """Write model configuration file."""
        for kwarg in kwargs:  # Write any kwargs to the config.
            self._config[kwarg] = kwargs[kwarg]

        config_file = self._cfg_dir / "leakybucket_config.json"

        with config_file.open(mode="w") as f:
            f.write(json.dumps(self._config, indent=4))

        return config_file


class LeakyBucket(ContainerizedModel, LeakyBucketMethods):
    """The LeakyBucket eWaterCycle model, with the Container Registry docker image."""
    bmi_image: ContainerImage = ContainerImage(
        "ghcr.io/ewatercycle/leakybucket-grpc4bmi:v0.0.1"
    )
