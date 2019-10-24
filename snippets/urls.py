from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('start/', views.api_root),
	path('', views.FrontendAppView.as_view()),
    #path('sentry-debug/', trigger_error),
    path('snippets/', views.SnippetList.as_view(), name = 'snippet-list'),
    path('snippets/create/', views.CreateSnippet.as_view()),
    path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name = 'snippet-detail'),
    # path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view(), name='snippet-highlight'),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view(), name = 'user-detail'),
    path('usersupdate/<int:pk>/', views.UpdateUserView.as_view(), name = 'user-update'),
    path('reg/', views.CreateUserView.as_view(), name = 'user-list'),
    path('course/create/', views.CreateCourseView.as_view()),
    path('coursepage/', views.CreatePageView.as_view()),
    path('course/', views.CoursListView.as_view(), name = 'courselist-list'),
    path('course/<int:pk>/', views.CourseDetail.as_view(), name = 'courselist-detail'),
    path('coursepagelist/', views.CoursPageListView.as_view(), name = 'coursepage-list'),
    path('coursepagelist/<int:pk>/', views.CoursPageDetailView.as_view(), name = 'coursepage-detail'),
    path('courseuser/', views.CoursUserView.as_view(), name = 'courseuser-create'),
    path('courseuserlist/', views.CoursUserListView.as_view(), name = 'courseuser-list'),
    path('auth/confirm_email/<str:user>/<str:token>', views.ConfirmEmailView.as_view(), name='confirm_email'),
    path('acc/', views.AccInfoView.as_view(), name='acc_info'),
    path('acc/<int:owner_id>/',  views.AccountView.as_view(), name='account'),
    path('gradelist/', views.gradelist),
    path('gradeupdate/<int:pk>/', views.GradeListUpdateView.as_view(), name = 'gradeupdate'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
