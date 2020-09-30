import datetime
from typing import NamedTuple

from django.db.models import QuerySet
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.generators import NoModelAutoSchema, PathParameter
from drf_docs_wo_models.decorators import custom_parameters


class Country(NamedTuple):
    name: str
    created_at: datetime.datetime


countries = [
    Country(name='Uzbekistan', created_at=datetime.datetime.now()),
    Country(name='Russia', created_at=datetime.datetime.now() - datetime.timedelta(days=1)),
    Country(name='USA', created_at=datetime.datetime.now() - datetime.timedelta(days=10)),
]


class CountrySerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    name = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(required=False)


class CountryResponseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    name = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(required=False)
    extra_field = serializers.CharField(default='extra_field_for_response')


class CountryQuerySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    ordering = serializers.CharField(max_length=15, help_text='-name,created_at', required=False)
    search = serializers.CharField(max_length=15, required=False)


class CountryViewSet(viewsets.GenericViewSet):
    queryset = QuerySet()
    serializer_class = CountrySerializer
    pagination_class = PageNumberPagination
    schema = NoModelAutoSchema(
        path_parameters=dict(id=PathParameter(scheme_type='UUID type', description='id of a country')),
    )

    def retrieve(self, request, *args, **kwargs):
        instance = countries[0]
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @custom_parameters(query_serializer=CountryQuerySerializer, response_serializer=CountryResponseSerializer)
    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(countries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(countries, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True)
    def help(self, request, *args, **kwargs):
        instance = countries[0]
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
