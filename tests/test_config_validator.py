from dataclasses import dataclass

import pytest
from kaiju_app import Application, Service
from kaiju_config_validator import ConfigValidator, InvalidConfiguration


_valid_configs = [
    (
        'minimal config', {
            'app': {
                'name': 'app',
                'env': 'pytest'
            }
        }
    ),
    (
        'full config', {
            'debug': True,
            'packages': [
                'some-pkg'
            ],
            'logging': {
                'loggers': {
                    'app': {
                        'handlers': ['stdout'],
                    }
                },
                'handlers': {
                    'stdout': {
                        'formatter': 'json'
                    }
                },
                'formatters': {
                    'json': {
                        'keys': ['message', 'asctime', 'ctx']
                    }
                }
            },
            'app': {
                'name': 'app',
                'env': 'pytest',
                'loglevel': 'INFO',
                'settings': {
                    'service_start_timeout_s': 42.0
                },
                'optional_services': ['_service'],
                'services': [
                    {
                        'cls': '_Service',
                        'name': '_service',
                        'enabled': True,
                        'loglevel': 'INFO',
                        'settings': {
                            'required_value': 1
                        }
                    }
                ]
            }
        }
    ),
]
valid_configs = [_conf[1] for _conf in _valid_configs]
valid_configs_ids = [_conf[0] for _conf in _valid_configs]

_invalid_configs = [
    (
        'empty config', {}
    ),
    (
        'additional section config', {
            'app': {
                'name': 'app',
                'env': 'pytest'
            },
            'something': {}
        }
    ),
    (
        'wrong param type', {
            'app': {
                'name': 'app',
                'env': 123
            }
        }
    ),
    (
        'wrong param type', {
            'app': {
                'name': 'app',
                'env': 123
            }
        }
    ),
    (
        'unknown service class', {
            'app': {
                'name': 'app',
                'env': 'test',
                'services': [
                    {'cls': 'UnknownService'}
                ]
            }
        }
    ),
    (
        'not enough params for service settings', {
            'app': {
                'name': 'app',
                'env': 123,
                'services': [
                    {'cls': '_Service', 'settings': {'not_required_value': 'test2'}}
                ]
            }
        }
    ),
    (
        'too many service settings', {
            'app': {
                'name': 'app',
                'env': 123,
                'services': [
                    {'cls': '_Service', 'settings': {'required_value': 1, 'something': '1'}}
                ]
            }
        }
    ),
]
invalid_configs = [_conf[1] for _conf in _invalid_configs]
invalid_configs_ids = [_conf[0] for _conf in _invalid_configs]

@dataclass
class _Service(Service):
    required_value: int
    not_required_value: str = 'test'


service_classes = {'_Service': _Service}


class TestConfigValidator:

    @pytest.fixture
    def _validator(self):
        return ConfigValidator()

    @pytest.mark.parametrize('config', valid_configs, ids=valid_configs_ids)
    def test_valid_configuration(self, _validator, config):
        _validator.validate_project_config(Application, service_classes, config)

    @pytest.mark.parametrize('config', invalid_configs, ids=invalid_configs_ids)
    def test_invalid_configuration(self, _validator, config):
        with pytest.raises(InvalidConfiguration):
            _validator.validate_project_config(Application, service_classes, config)
