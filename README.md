# eWaterCycle plugin example: a leaky bucket model

This repository is a template for adding models to eWatercycle, and will guide you through all required steps.

**Note**: this repository is designed for Python (compatible) models.
Model BMI's written in Julia or Matlab/Octave can interface though Python.

Some information on model BMI's in C/C++ or R is available on [the grpc4bmi repository](https://github.com/eWaterCycle/grpc4bmi).


## Installation
Install this package alongside your eWaterCycle installation

```console
pip install -e .
```

Then LeakyBucket becomes available as one of the eWaterCycle models

```python
from ewatercycle.models import LeakyBucket
```

## Implementing your own model

For more information on implementing your own model see the [plugin guide](plugin_guide.md)

## License

`ewatercycle-plugin` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
