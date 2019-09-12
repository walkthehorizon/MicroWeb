from django.urls import path, include
import wallpaper.views as bv
from rest_framework.routers import DefaultRouter, SimpleRouter

# 创建路由器并注册我们的视图。
router = DefaultRouter()
router.register("subjects", bv.SubjectViewSet)
router.register("wallpapers", bv.WallPapersViewSet)
router.register("categories", bv.CategoryViewSet)
router.register("banners", bv.BannerViewSet)
urlpatterns = router.urls
urlpatterns += [
    # path('user/list/', bv.UserList.as_view(), name='user-list'),
    path('splash/', bv.GetSplash().as_view(), name='get_splash'),
    path('recommend/', bv.GetRandomRecommend().as_view(), name='get_random_recommend'),
    path('signature', bv.get_temp_secret_key, name='get_temp_secret_key'),
    # path('subject/list/', bv.SubjectList.as_view(), name='subject-list'),
    # path('subject/detail/<int:pk>/', bv.GetWallpaperBySubjectId.as_view(), name='GetWallpaperBySubject'),
    path('account/register/', bv.register_user, name="register-user"),
    path('account/login/', bv.login_user, name="login-user"),
    path('account/logout/', bv.logout_user, name="logout-user"),
    path('collect/my', bv.GetMyCollect.as_view(), name='my-collect'),
    path('collect/add/<int:pid>', bv.add_collect),
    path('collect/del/collects', bv.del_collect),
    path('buy/paper/<int:pk>', bv.buy_paper),
    path('category/update/', bv.update_category_cover),
    path('user/update/<int:pk>', bv.UserUpdate.as_view()),
    path('update', bv.get_update_info),
    path('wallpaper/detail/<int:pk>', bv.get_paper_for_web)
    # path('category/list/<int:id>/', bv.GetPictureByCategoryId.as_view(), name='get-category-by-id'),
    # path('subject/put/support/', bv.put_subject_support, name='put-subject-support'),
    # path('subject/support/<int:subjectId>/', bv.GetSubjectSupportCount.as_view(), name='GetSubjectSupportCount'),
    #
    # path('wallpaper/list', bv.WallPaperList.as_view(), name='wallpaper-list'),
    # path('wallpaper/detail/<int:pk>/', bv.WallPaperDetail.as_view(), name='wallpaper-detail'),
    # path('category/list', bv.CategoryList.as_view(), name='category-list'),
]
