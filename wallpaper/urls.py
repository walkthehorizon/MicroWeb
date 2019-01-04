from django.urls import path, include
import wallpaper.views as bv
from rest_framework.routers import DefaultRouter, SimpleRouter

# 创建路由器并注册我们的视图。
router = DefaultRouter()
router.register("subjects", bv.SubjectViewSet)
router.register("wallpapers", bv.WallPapersViewSet)
urlpatterns = router.urls
urlpatterns += [
    # path('user/list/', bv.UserList.as_view(), name='user-list'),
    path('splash/', bv.GetSplash().as_view(), name='get-splash'),
    # path('subject/list/', bv.SubjectList.as_view(), name='subject-list'),
    # path('subject/detail/<int:pk>/', bv.GetWallpaperBySubjectId.as_view(), name='GetWallpaperBySubject'),
    # path('account/register/', bv.register_user, name="register-user"),
    # path('account/login/', bv.login_user, name="login-user"),
    # path('account/logout/', bv.logout_user, name="logout-user"),
    # path('category/list/<int:id>/', bv.GetPictureByCategoryId.as_view(), name='get-category-by-id'),
    # path('subject/put/support/', bv.put_subject_support, name='put-subject-support'),
    # path('subject/support/<int:subjectId>/', bv.GetSubjectSupportCount.as_view(), name='GetSubjectSupportCount'),
    #
    # path('wallpaper/list', bv.WallPaperList.as_view(), name='wallpaper-list'),
    # path('wallpaper/detail/<int:pk>/', bv.WallPaperDetail.as_view(), name='wallpaper-detail'),
    # path('category/list', bv.CategoryList.as_view(), name='category-list'),
]
