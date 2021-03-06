from django.db.models import Prefetch
from rest_framework import viewsets

from reqs.filtersets import AgencyFilter, AgencyGroupFilter, TopicFilter
from reqs.models import Agency, AgencyGroup, Topic
from reqs.serializers import (AgencySerializer, GroupWithAgenciesSerializer,
                              TopicSerializer)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_fields = TopicFilter.get_fields()
    search_fields = ('name',)


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.filter(public=True)
    serializer_class = AgencySerializer
    filter_fields = AgencyFilter.get_fields()
    search_fields = ('name', 'abbr')


class AgencyGroupViewSet(viewsets.ModelViewSet):
    queryset = AgencyGroup.objects.prefetch_related(
        Prefetch('agencies', AgencyViewSet.queryset))
    serializer_class = GroupWithAgenciesSerializer
    filter_fields = AgencyGroupFilter.get_fields()
    filter_fields.update({
        'agencies__' + key: value
        for key, value in AgencyFilter.get_fields().items()})
    search_fields = ('name',)
