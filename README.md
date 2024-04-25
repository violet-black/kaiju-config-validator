[![pypi](https://img.shields.io/pypi/v/kaiju-config-validator.svg)](https://pypi.python.org/pypi/kaiju-config-validator/)
[![codecov](https://codecov.io/gh/violet-black/kaiju-config-validator/graph/badge.svg?token=FEUUMQELFX)](https://codecov.io/gh/violet-black/kaiju-config-validator)
[![tests](https://github.com/violet-black/kaiju-config-validator/actions/workflows/tests.yaml/badge.svg)](https://github.com/violet-black/kaiju-config-validator/actions/workflows/tests.yaml)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![python](https://img.shields.io/pypi/pyversions/kaiju-config-validator.svg)](https://pypi.python.org/pypi/kaiju-config-validator/)

**kaiju-config-validator** is designed to work with [kaiju-app](https://kaiju-app.readthedocs.io) library to validate
project configuration dictionary for a set of application service classes. It analyzes `__init__` methods of services
to check the input data before creating an app object.

[fastjsonschema](https://github.com/horejsek/python-fastjsonschema) library is used for validation.

# Installation

With pip and python 3.12+:

```bash
pip3 install kaiju-config-validator
```

# How to use

The configuration process is straightforward.
Use the standard application configuration process as described in the [kaiju-app documentation](https://kaiju-app.readthedocs.io).

```python
from kaiju_config_validator import ConfigValidator
from kaiju_app import Application, ApplicationLoader, Configurator

loader = ApplicationLoader()
loader.service_classes[...] = ...
config = Configurator().create_configuration([...], [...])
```

As soon as a project config dict is produced you can pass it to the validator method along with service classes
map and an application class. The validator will either raise a `InvalidConfiguration` or return `None` if everything
is fine.

```python
ConfigValidator().validate_project_config(Application, loader.service_classes, config)
```
