import json
from pathlib import Path
from typing import Type
from ewatercycle.base.model import LocalModel, ContainerizedModel, eWaterCycleModel
from ewatercycle.base.forcing import GenericLumpedForcing
from pydantic import model_validator
from leakybucket import leakybucket_bmi
from bmipy import Bmi
from ewatercycle.container import ContainerImage


class LeakyBucketMixins(eWaterCycleModel):
    """Common arguments and methods for the eWatercycle LeakyBucket model."""
    forcing: GenericLumpedForcing  # The model requires forcing.

    _config: dict = {
        "forcing_file": "",
        "leakiness": 0.05,
    }

    @model_validator(mode="after")
    def _update_config(self):
        assert self.forcing.directory is not None
        self._config["forcing_file"] = str(self.forcing.directory / self.forcing.pr)
        return self

    def _make_cfg_file(self, **kwargs) -> Path:
        """Write model configuration file."""
        if "leakiness" in kwargs:
            self._config["leakiness"] = kwargs["leakiness"]

        config_file = self._cfg_dir / "leakybucket_config.json"

        with config_file.open(mode="w") as f:
            f.write(json.dumps(self._config, indent=4))

        return config_file


class LocalModelLeakyBucket(LocalModel, LeakyBucketMixins):
    """The LeakyBucket eWaterCycle model, with the local BMI."""
    bmi_class: Type[Bmi] = leakybucket_bmi.LeakyBucketBmi


class LocalContainerLeakyBucket(ContainerizedModel, LeakyBucketMixins):
    """The LeakyBucket eWaterCycle model, with the (local) container BMI & grpc4bmi."""
    bmi_image: ContainerImage = ContainerImage("leakybucket")


class LeakyBucket(ContainerizedModel, LeakyBucketMixins):
    """The LeakyBucket eWaterCycle model, with the Container Registry docker image."""
    bmi_image: ContainerImage = ContainerImage(
        "ghcr.io/ewatercycle/leakybucket:0.0.1"
    )
