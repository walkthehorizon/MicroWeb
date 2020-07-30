from rest_framework import generics

from wallpaper import state
from wallpaper.models import Category
from wallpaper.serializers import CategorySerializer
import wallpaper.views.helper as util


class GetCategories(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        if util.is_newest_version(self.request):
            return Category.objects.all().filter(type=0)
        else:
            return Category.objects.all().filter(type=1)
