from django.urls import path
import wallpaper.views as bv

urlpatterns = [
    path('list/', bv.SnippetList.as_view()),
    path('snippets/<int:pk>/', bv.SnippetDetail.as_view()),
    path('wallpaper/', bv.WallPaperList.as_view(), name='wallpaper-list'),
    path('wallpaper/detail/<int:id>/', bv.WallPaperDetail.as_view(), name='wallpaperDetail'),
    path('users/', bv.UserList.as_view(), name='user-list'),
    path('users/int<id>/', bv.UserDetail.as_view(), name='userDetail'),
]
