from rest_framework import generics

from wallpaper import state, models
from wallpaper.models import Category
from wallpaper.serializers import CategorySerializer
import wallpaper.views.helper as util


class GetCategories(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        if util.is_old_version(self.request):
            return Category.objects.all().filter(type=models.TYPE_COS)
        else:
            return Category.objects.all().filter(type=models.TYPE_ANIM)
