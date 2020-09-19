from typing import NamedTuple, Mapping, Optional

import uritemplate
from rest_framework import serializers
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.serializers import Serializer


class PathParameter(NamedTuple):
    description: str
    scheme_type: str


class NoModelAutoSchema(AutoSchema):
    def __init__(
            self,
            path_parameters: Optional[Mapping[str, PathParameter]] = None,
            query_parameters: Optional[Mapping[str, Serializer]] = None,
            tags=None,
            operation_id_base=None,
            component_name=None
    ):
        if path_parameters is None:
            path_parameters = {}
        self.path_parameters = path_parameters
        if query_parameters is None:
            query_parameters = {}
        self.query_parameters = query_parameters
        super(NoModelAutoSchema, self).__init__(
            tags=tags, operation_id_base=operation_id_base, component_name=component_name
        )

    def get_path_parameters(self, path, method):
        """
        Return a list of parameters from template path variables.
        """
        parameters = []

        for variable in uritemplate.variables(path):
            description = ''
            scheme_type = 'string'

            path_parameter = self.path_parameters.get(variable, None)
            if path_parameter:
                description = path_parameter.description
                scheme_type = path_parameter.scheme_type

            parameter = {
                "name": variable,
                "in": "path",
                "required": True,
                "description": description,
                'schema': {
                    'type': scheme_type
                },
            }

            parameters.append(parameter)

        return parameters

    def get_operation(self, path, method):
        operation = super(NoModelAutoSchema, self).get_operation(path, method)

        operation['parameters'] = operation['parameters'] + self.get_query_parameters(path, method)
        return operation

    def get_query_parameters(self, path, method):
        parameters = []

        view_method = getattr(self.view, self.view.action)

        if hasattr(view_method, '_scheme_params'):
            query_serializer: Serializer = view_method._scheme_params.get('query_serializer')
            for field in query_serializer.fields.values():

                if isinstance(field, serializers.HiddenField):
                    continue

                parameter = {
                    "name": field.field_name,
                    "in": "query",
                    "required": field.required,
                    "description": field.help_text or '',
                    'schema': self.map_field(field),
                }
                parameters.append(parameter)

        return parameters
