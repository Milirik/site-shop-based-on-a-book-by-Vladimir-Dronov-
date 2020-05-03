from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, Http404

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView, View

from django.urls import reverse, reverse_lazy

from .forms import ChangeUserInfoForm, RegisterUserForm
from .models import AdvUser
from .utilities import signer


#Переходы по страницам
def index(request):
	return render(request, 'main/index.html', context={})

def other_page(request, page):
	try:
		template = get_template('main/' + page + '.html')
	except TemplateDoesNotExist:
		raise Http404
	return HttpResponse(template.render(request=request))


#Авторизация
class BBLoginView(LoginView):
	template_name = 'main/login.html'
	# def get_success_url(self):
	# 	return reverse("main:index")


class BBLogoutView(LoginRequiredMixin, LogoutView):
	template_name = 'main/logout.html'


def user_activate(request, sign):
	try:
		username = signer.unsign(sign)
	except BadSignature:
		return render(request, 'main/bad_signature.html')
	user = get_object_or_404(AdvUser, username=username)
	if user.is_activated:
		template = 'main/user_is_activated.html'
	else:
		template = 'main/activation_done.html'
		user.is_active = True
		user.is_activated = True
		user.save()
	return render(request, template)


#Инфа о пользователе
@login_required
def profile(request):
	return render(request, 'main/profile.html')


#CRUD пользователя

class RegisterUserView(CreateView):
	model = AdvUser
	template_name = 'main/register_user.html'
	form_class = RegisterUserForm
	success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
	template_name = 'main/register_done.html'


class DeleteUserView(LoginRequiredMixin, DeleteView):
	model = AdvUser
	template_name = 'main/delete_user.html'
	success_url = reverse_lazy('main:index')

	def dispatch(self, request, *args, **kwargs):
		self.user_id = request.user.pk
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		logout(request)
		messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
		return super().post(request, *args, **kwargs)

	def get_object(self, queryset=None):
		if not queryset:
			queryset = self.get_queryset()
		return get_object_or_404(queryset, pk=self.user_id)
		

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
	model = AdvUser
	template_name = 'main/change_user_info.html'
	form_class = ChangeUserInfoForm
	success_url = reverse_lazy('main:profile')
	success_message = 'Личные данные пользователя изменены'

	def dispatch(self, request, *args, **kwargs):
		self.user_id = request.user.pk
		return super().dispatch(request, *args, **kwargs)

	def get_object(self, queryset=None):
		if not queryset:
			queryset = self.get_queryset()
		return get_object_or_404(queryset, pk=self.user_id)


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
		template_name = 'main/password_change.html'
		success_url = reverse_lazy('main:profile')
		success_message = 'Пароль пользователя изменен'

