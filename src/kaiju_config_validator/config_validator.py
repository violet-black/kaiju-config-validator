"""Configuration validator."""

from collections.abc import Collection
from typing import Callable

import jsonschema_gen.schema as j
from kaiju_app import ProjectConfig, Application, Service
from jsonschema_gen import Parser
from fastjsonschema import compile as compile_schema, JsonSchemaException

__all__ = ["ConfigValidator", "InvalidConfiguration"]


class InvalidConfiguration(Exception):
    """Invalid project configuration."""


class ConfigValidator:
    """Config validator.

    It allows to validate a project config including service and app settings before actually trying to create and
    run the app.
    """

    def __init__(self):
        self.annotation_parser = Parser(strict=False)
        self.compile_schema = compile_schema

    def validate_project_config(
        self, app_cls: type[Application], service_classes: dict[str, type[Service]], project_config: ProjectConfig
    ) -> None:
        """Check a project config and raise a validation error if config is invalid."""
        try:
            self._validate_project_config(app_cls, service_classes, project_config)
        except JsonSchemaException as exc:
            raise InvalidConfiguration("Invalid app configuration: see the exception above for details") from exc

    def _validate_project_config(
        self, app_cls: type[Application], service_classes: dict[str, type[Service]], project_config: ProjectConfig
    ) -> None:
        project_schema = self.get_project_config_schema()
        self.compile_schema(project_schema.json_repr())(project_config)
        app_schema = self.get_application_settings_schema(app_cls)
        self.compile_schema(app_schema.json_repr())(project_config["app"].get("settings", {}))
        _service_class_schemas: dict[str, Callable] = {}
        for service_config in project_config["app"].get("services", []):
            service_cls_name = service_config["cls"]
            if service_cls_name not in service_classes:
                raise JsonSchemaException(f'Service class "{service_cls_name}" is not registered in `service_classes`')
            if service_cls_name in _service_class_schemas:
                validate_service = _service_class_schemas[service_cls_name]
            else:
                service_cls = service_classes[service_cls_name]
                service_schema = self.get_service_settings_schema(service_cls)
                _service_class_schemas[service_cls_name] = validate_service = self.compile_schema(
                    service_schema.json_repr()
                )
            validate_service(service_config.get("settings", {}))

    def get_project_config_schema(self) -> j.JSONSchemaType:
        return self.annotation_parser.parse_annotation(ProjectConfig)

    def get_application_settings_schema(self, app_cls: type[Application], /) -> j.JSONSchemaType:
        auto_values = ["name", "logger", "env", "context", "debug", "optional_services"]
        return self._get_class_settings_schema(app_cls, auto_values)

    def get_service_settings_schema(self, service: type[Service], /) -> j.JSONSchemaType:
        auto_values = ["app", "name", "logger"]
        return self._get_class_settings_schema(service, auto_values)

    def _get_class_settings_schema(self, cls_: type, auto_values: Collection[str]) -> j.JSONSchemaType:
        annotation = self.annotation_parser.parse_function(getattr(cls_, "__init__"), cls_)
        kwargs = annotation.kwargs
        kwargs.properties = {key: value for key, value in kwargs.properties.items() if key not in auto_values}
        kwargs.required = [key for key in kwargs.required if key not in auto_values]
        kwargs.additionalProperties = True  # to allow **kwargs there
        return kwargs
