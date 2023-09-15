from typing import Any, Tuple
import numpy as np
from leakybucket import utils
from leakybucket import empty_bmi


class LeakyBucketLumpedBmi(empty_bmi.EmptyBmi):
    """Demonstration of a minimal hydrological model.

    🌧️
    🪣
    💧
    """

    def initialize(self, config_file: str) -> None:
        # The model config contains the precipitation file, and the model parameter.
        self.config: dict[str, Any] = utils.read_config(config_file)

        # Get the input data:
        #   Note: the precipitation input is in [kg m-2 s-1]
        self.precipitation = utils.load_precip(self.config["forcing_file"])
        self.time_data = self.precipitation["time"]

        # Define the model states:
        self.storage = 0  # [kg m-2 == m-1 (water depth equivalent)]
        self.discharge = 0  # [m d-1]

        # time step size in seconds (to be able to do unit conversions).
        self.timestep_size = (
            self.time_data.values[1] - self.time_data.values[0]
        ) / np.timedelta64(1, "s")

        self.current_timestep = 0
        self.end_timestep = self.time_data.size

        # The one model parameter is the 'leakiness' of the buckets:
        #   the leakiness value is in [d-1].
        self.leakiness = self.config["leakiness"]

    def update(self) -> None:
        if self.current_timestep < self.end_timestep:
            # Add the current timestep's precipitation to the storage
            self.storage += (
                self.precipitation.isel(time=self.current_timestep).to_numpy()
                * self.timestep_size
            )

            # Calculate the discharge [m d-1] based on the leakiness and storage
            self.discharge = self.storage * self.leakiness
            # Subtract this discharge from the storage
            #   The discharge in [m d-1] has to be converted to [m] per timestep.
            self.storage -= self.discharge * (self.timestep_size / 24 / 3600)

            # Advance the model time by one step
            self.current_timestep += 1

    def update_until(self, time: float) -> None:
        while self.get_current_time() < time:
            self.update()

    def finalize(self) -> None:
        """There is nothing to finalize."""
        pass

    def get_component_name(self) -> str:
        return "leakybucket"

    def get_value(self, var_name: str) -> np.ndarray:
        match var_name:
            case "storage":
                return np.array(self.storage)
            case "discharge":
                return np.array(self.discharge / (self.timestep_size / 24 / 3600))
            case _:
                raise ValueError(f"Unknown variable {var_name}")

    def get_var_units(self, var_name: str) -> str:
        match var_name:
            case "storage":
                return "m"
            case "discharge":
                return "m d-1"
            case _:
                raise ValueError(f"Unknown variable {var_name}")

    def set_value(self, var_name: str, src: np.ndarray) -> None:
        match var_name:
            case "storage":
                self.storage = src[0]
            case _:
                raise ValueError(f"Cannot set value of var {var_name}")

    # The BMI has to have some time-related functionality:
    def get_start_time(self) -> float:
        """Return end time in seconds since 1 january 1970."""
        return get_unixtime(self.time_data.isel(time=0).values)

    def get_end_time(self) -> float:
        """Return end time in seconds since 1 january 1970."""
        return get_unixtime(self.time_data.isel(time=-1).values)

    def get_current_time(self) -> float:
        """Return current time in seconds since 1 january 1970."""
        return get_unixtime(self.time_data.isel(time=self.current_timestep).values)

    def get_time_step(self) -> float:
        return self.timestep_size

    # Some BMI required grid-related methods.
    def get_grid_type(self, grid: int) -> str:
        if grid == 0:
            return "scalar"
        else:
            raise ValueError("Unknown grid number.")

    def get_grid_rank(self, grid: int) -> int:
        if grid == 0:
            return 0
        else:
            raise ValueError("Unknown grid number.")

    def get_grid_shape(self, grid: int) -> np.ndarray:
        if grid == 0:
            return np.array(1)
        else:
            raise ValueError("Unknown grid number.")

    def get_grid_x(self, grid: int) -> np.ndarray:
        if grid == 0:
            return self.precipitation["lon"].to_numpy()
        else:
            raise ValueError("Unknown grid number.")

    def get_grid_y(self, grid: int) -> np.ndarray:
        if grid == 0:
            return self.precipitation["lat"].to_numpy()
        else:
            raise ValueError("Unknown grid number.")

    def get_output_var_names(self) -> Tuple[str]:
        return ("discharge",)

    def get_time_units(self) -> str:
        return "s"

    def get_value_at_indices(self, name: str, inds: np.ndarray) -> np.ndarray:
        if inds == np.array(0):
            return self.get_value(name)
        else:
            raise ValueError("Index out of bounds.")

    def set_value_at_indices(
        self, name: str, inds: np.ndarray, src: np.ndarray
    ) -> None:
        if inds == np.array(0):
            self.set_value(name, src)
        else:
            raise ValueError("Index out of bounds.")

    def get_var_grid(self, name: str) -> int:
        return 0

    def get_var_itemsize(self, name: str) -> int:
        return np.array(0.0).nbytes

    def get_var_nbytes(self, name: str) -> int:
        return np.array(0.0).nbytes

    def get_var_type(self, name: str) -> str:
        return "float64"


def get_unixtime(dt64: np.datetime64) -> float:
    """Get unix timestamp (seconds since 1 january 1970) from a np.datetime64."""
    return dt64.astype("datetime64[s]").astype("int")
