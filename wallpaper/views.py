from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from wallpaper.models import Snippet, Wallpaper
from wallpaper.serializers import SnippetSerializer, UserSerializer
from wallpaper.serializers import WallPagerSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from wallpaper.permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'wallpapers': reverse('wallpaper-list', request=request, format=format)
    })


class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class WallPaperList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = Wallpaper.objects.all()
    serializer_class = WallPagerSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WallPaperDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    lookup_field = 'id'
    queryset = Wallpaper.objects.all()
    serializer_class = WallPagerSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # @api_view(['GET', 'POST'])
    # @permission_classes((permissions.AllowAny,))
    # def wall_pager_list(request):
    #     if request.method == 'GET':
    #         wallpages = WallPager.objects.all()
    #         serializer = WallPagerSerializer(wallpages, many=True)
    #         return Response(serializer.data)
    #     elif request.method == 'POST':
    #         serializer = WallPagerSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # @api_view(['GET', 'PUT', 'DELETE'])
    # @permission_classes((permissions.AllowAny,))
    # def wall_pager_detail(request, id, format=None):
    #     try:
    #         wallpager = WallPager.objects.get(id=id)
    #     except WallPager.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    #     if request.method == 'GET':
    #         serializer = WallPagerSerializer(wallpager)
    #         return Response(serializer.data)
    #
    #     elif request.method == 'PUT':
    #         serializer = WallPagerSerializer(wallpager, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    #     elif request.method == 'DELETE':
    #         wallpager.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
