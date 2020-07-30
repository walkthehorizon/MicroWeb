from rest_framework import generics, filters

import wallpaper.views.helper as util
from wallpaper.models import CHOICE_TYPE
from wallpaper.models import Subject
from wallpaper.serializers import SubjectSerializer


class Search(generics.ListAPIView):
    serializer_class = SubjectSerializer
    search_fields = ['name', ]
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return Subject.objects.filter(type=CHOICE_TYPE[0][0] if util.is_newest_version(self.request) else CHOICE_TYPE[0][1])
