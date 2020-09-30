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

        view_method = getattr(self.view, self.view.action, None)

        if view_method and hasattr(view_method, '_scheme_params'):
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

    def get_response_serializer(self, path, method):
        view_method = getattr(self.view, self.view.action)
        return view_method._scheme_params['response_serializer']

    def get_responses(self, path, method):
        old_func = None
        view_method = getattr(self.view, self.view.action, None)
        if view_method and hasattr(view_method, '_scheme_params') and view_method._scheme_params.get('response_serializer', None):
            old_func = self.view.get_serializer
            # this is too much hack :(
            self.view.get_serializer = lambda: self.get_response_serializer(path, method)

        responses = super(NoModelAutoSchema, self).get_responses(path, method)

        if old_func:
            self.view.get_serializer = old_func

        return responses

    def get_components(self, path, method):
        components = super(NoModelAutoSchema, self).get_components(path, method)

        view_method = getattr(self.view, self.view.action, None)
        if view_method and hasattr(view_method, '_scheme_params') and view_method._scheme_params.get('response_serializer', None):
            serializer = self.get_response_serializer(path, method)

            if not isinstance(serializer, serializers.Serializer):
                return components

            component_name = self.get_component_name(serializer)

            content = self.map_serializer(serializer)
            components.update({component_name: content})
            return components

        return components
