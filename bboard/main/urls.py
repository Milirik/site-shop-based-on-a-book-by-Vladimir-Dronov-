from django.urls import path, include
from django.contrib.auth.views import PasswordResetView , PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import *

app_name = 'main'
urlpatterns = [
	path('', index, name='index'),
	path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
	path('<int:pk>/', by_rubric, name='by_rubric'),

	path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
	path('accounts/register/done', RegisterDoneView.as_view(), name='register_done'),
	path('accounts/register/', RegisterUserView.as_view(), name='register'),
	path('accounts/login/', BBLoginView.as_view(), name='login'),
	path('accounts/logout/', BBLogoutView.as_view(), name='logout'),

	path('accounts/profile/change/<int:pk>', profile_bb_change, name='profile_bb_change'),
	path('accounts/profile/delete/<int:pk>', profile_bb_delete, name='profile_bb_delete'),
	path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
	path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),
	path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
	path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
	path('accounts/profile/', profile, name='profile'),

	path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
	path('accounts/password_reset/', PasswordResetView.as_view(template_name='main/password_reset.html',
															   subject_template_name='email/reset_subject.txt',
															   email_template_name='email/reset_email.html'),
									 name='password_reset'),
	
	path('<str:page>/', other_page, name='other'),
]