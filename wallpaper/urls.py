from django.urls import path, include
import wallpaper.views.views as bv
import wallpaper.views.users as user
import wallpaper.views.manager as manager
import wallpaper.views.category as category
import wallpaper.views.subject as subject
from rest_framework.routers import DefaultRouter, SimpleRouter

# 创建路由器并注册我们的视图。
router = DefaultRouter()
router.register("subjects", bv.SubjectViewSet)
router.register("wallpapers", bv.WallPapersViewSet)
# router.register("categories", bv.CategoryViewSet)
router.register("banners", bv.BannerViewSet)
urlpatterns = router.urls
urlpatterns += [
    # user
    path('account/info', user.get_account_info, name="login-user"),
    path('account/register/', user.register_user, name="register-user"),
    path('account/logout/', user.logout_user, name="logout-user"),
    path('paper/comments', user.GetPaperComments.as_view()),
    path('paper/comments/add', user.add_paper_comment),

    path('subject/search', subject.Search().as_view()),
    # path('user/list/', bv.UserList.as_view(), name='user-list'),
    path('splash/', bv.GetSplash().as_view(), name='get_splash'),
    path('recommend/', bv.GetRandomRecommend().as_view(), name='get_random_recommend'),
    path('paper/newest', bv.GetNewWallpapers().as_view()),
    path('paper/ranks', bv.GetRankPapers().as_view()),
    path('signature', bv.get_temp_secret_key, name='get_temp_secret_key'),
    # path('subject/list/', bv.SubjectList.as_view(), name='subject-list'),
    # path('subject/detail/<int:pk>/', bv.GetWallpaperBySubjectId.as_view(), name='GetWallpaperBySubject'),

    path('collect/my', bv.GetMyCollect.as_view(), name='my-collect'),
    path('collect/add/<int:pid>', bv.add_collect),
    path('collect/del/collects', bv.del_collect),
    path('buy/paper/<int:pk>', bv.buy_paper),
    path('category/update/', bv.update_category_cover),
    path('user/update/<int:pk>', bv.UserUpdate.as_view()),
    path('update', bv.get_update_info),
    path('sign', bv.get_is_sign),
    path('wallpaper/detail/<int:pk>', bv.get_paper_for_web),
    path('paper/set/banner', bv.set_wallpaper_banner),

    path('paper/share/num', bv.update_share_num),
    # path('category/list/<int:id>/', bv.GetPictureByCategoryId.as_view(), name='get-category-by-id'),
    # path('subject/put/support/', bv.put_subject_support, name='put-subject-support'),
    # path('subject/support/<int:subjectId>/', bv.GetSubjectSupportCount.as_view(), name='GetSubjectSupportCount'),
    #
    # path('wallpaper/list', bv.WallPaperList.as_view(), name='wallpaper-list'),
    # path('wallpaper/detail/<int:pk>/', bv.WallPaperDetail.as_view(), name='wallpaper-detail'),
    # path('category/list', bv.CategoryList.as_view(), name='category-list'),

    # category
    path('categories', category.GetCategories.as_view()),

    # manager
    path('subject/delete', manager.delete_subject),
    path('subjects', manager.GetSubjects.as_view()),
    path('upload', manager.upload_paper),
]
