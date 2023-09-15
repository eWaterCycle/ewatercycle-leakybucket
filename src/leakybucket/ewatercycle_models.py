import json
from pathlib import Path
from typing import Type
from ewatercycle.base.model import LocalModel, ContainerizedModel
from ewatercycle.base.forcing import GenericLumpedForcing
from pydantic import model_validator
from leakybucket import leakybucket_bmi
from bmipy import Bmi
from ewatercycle.container import ContainerImage


class LocalLeakyBucket(LocalModel):
    bmi_class: Type[Bmi] = leakybucket_bmi.LeakyBucketLumpedBmi

    forcing: GenericLumpedForcing  # not optional for this model

    _config: dict = {
        "forcing_file": "",
        "leakiness": 0.05,
    }

    @model_validator(mode="after")
    def _update_config(self: "LocalLeakyBucket") -> "LocalLeakyBucket":
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


class ContainerLeakyBucket(ContainerizedModel):
    bmi_image: ContainerImage = ContainerImage(
        "sha256:ef55433215e1e5cc4c2546f8254473ab4b15dc4bf3f56242ac3009414335138c"
    )

    forcing: GenericLumpedForcing  # not optional for this model

    _config: dict = {
        "forcing_file": "",
        "leakiness": 0.05,
    }

    @model_validator(mode="after")
    def _update_config(self: "LocalLeakyBucket") -> "LocalLeakyBucket":
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
