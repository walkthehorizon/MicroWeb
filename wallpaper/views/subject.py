from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

import wallpaper.views.helper as util
from wallpaper import models
from wallpaper.models import Subject
from wallpaper.serializers import SubjectSerializer


class Search(generics.ListAPIView):
    serializer_class = SubjectSerializer
    search_fields = ['name', ]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return Subject.objects.filter(type=models.TYPE_COS if util.is_gentle_mode(self.request) else models.TYPE_ANIM)
