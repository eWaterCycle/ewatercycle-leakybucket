"""eWaterCycle wrapper around PCRGlobWB BMI."""

import logging
import tempfile
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple

import numpy as np
import xarray as xr
import yaml
from cftime import num2date
from ewatercycle.forcing import DefaultForcing
from ewatercycle.models.abstract import AbstractModel

logger = logging.getLogger(__name__)


class ToyModel(AbstractModel[DefaultForcing]):
    available_versions = ("latest", )

    def setup(self, cfg_dir: Optional[str] = None, **kwargs) -> Tuple[str, str]:  # type: ignore
        work_dir = tempfile.gettempdir()

        config_file = Path(work_dir) / 'config.yaml'
        with open(config_file, 'w') as file:
            yaml.dump({k: v for k, v in self.parameters}, file)

        self.bmi = ... # TODO
        return str(config_file), str(work_dir)

    def get_value_as_xarray(self, name: str) -> xr.DataArray:
        """Return the value as xarray object."""
        # Get time information
        time_units = self.bmi.get_time_units()
        grid = self.bmi.get_var_grid(name)
        shape = self.bmi.get_grid_shape(grid)

        # Extract the data and store it in an xarray DataArray
        da = xr.DataArray(
            data=np.reshape(self.bmi.get_value(name), shape),
            coords={
                "latitude": self.bmi.get_grid_y(grid),
                "longitude": self.bmi.get_grid_x(grid),
                "time": num2date(self.bmi.get_current_time(), time_units),
            },
            dims=["latitude", "longitude"],
            name=name,
            attrs={"units": self.bmi.get_var_units(name)},
        )

        return da

    @property
    def parameters(self) -> Iterable[Tuple[str, Any]]:
        """List the configurable parameters for this model."""
        # An opiniated list of configurable parameters.
        return [
            ("start_time", "20220101T00:00:00Z"),
            ("end_time", "20221231T00:00:00Z"),
        ]
