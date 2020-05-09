from django.db import models
from django.dispatch import Signal
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification

# User
class AdvUser(AbstractUser):
	is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
	send_messages = models.BooleanField(default=True, verbose_name='Слать оповещения о новых комментариях?')
	
	def delete(self, *args, **kwargs):
		for bb in self.bb_set.all():
			bb.delete()
		super().delete(*args, **kwargs)

	class Meta(AbstractUser.Meta):
		pass

# Rubrics
class SuperRubricManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(super_rubric__isnull=True)


class SubRubricManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(super_rubric__isnull=False)


class Rubric(models.Model):
	name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
	order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
	super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Надрубрика')

class SuperRubric(Rubric):
	objects = SuperRubricManager()

	def __str__(self):
		return self.name

	class Meta:
		proxy = True
		ordering = ['order', 'name']
		verbose_name = 'Надрубрика'
		verbose_name_plural = 'Надрубрики'


class SubRubric(Rubric):
	objects = SubRubricManager()

	def __str__(self):
		return '%s - %s' % (self.super_rubric.name, self.name)

	class Meta:
		proxy = True
		ordering = ['super_rubric__order', 'super_rubric__name', 'order', 'name']
		verbose_name='Подрубрика'
		verbose_name_plural = 'Подрубрики'

#Posts
class Bb(models.Model):
	rubric = models.ForeignKey('SubRubric', verbose_name='Рубрика', on_delete=models.PROTECT)
	title = models.CharField(max_length=40, verbose_name='Товар')
	content = models.TextField(verbose_name='Описание')
	price = models.IntegerField(default=0, verbose_name='Цена товара')
	contacts = models.TextField(verbose_name='Контакты')
	image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
	author = models.ForeignKey('AdvUser', on_delete=models.CASCADE , verbose_name='Автор объявления')
	is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

	def delete(self, *args, **kwargs):
		for ai in self.aditionalimage_set.all():
			ai.delete()
		super().delete(*args, **kwargs)
		
	def __str__(self):
		return self.title

	class Meta:
		verbose_name_plural = 'Объявления'
		verbose_name = 'Объявление'
		ordering = ['-created_at']

class AditionalImage(models.Model):
	bb = models.ForeignKey('Bb', on_delete=models.CASCADE, verbose_name='Оюъявление')
	image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

	class Meta:
		verbose_name_plural = 'Дополнительные илюстрации'
		verbose_name = 'Дополнительная илюстрация'

#Comment
class Comment(models.Model):
	bb = models.ForeignKey('Bb', on_delete=models.CASCADE, verbose_name='Объявление')
	author = models.CharField(max_length=30, verbose_name='Автор')
	content = models.TextField(verbose_name='Содержание')
	is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')


	class Meta:
		verbose_name_plural = 'Комментарии'
		verbose_name = 'Комментарий'
		ordering = ['created_at']


#Signals

user_registrated = Signal(providing_args=['instance'])

def user_registrated_dispatcher(sender, **kwargs):
	send_activation_notification(kwargs['instance'])

def post_save_dispatcher(sender, **kwargs):
	author = kwargs['instance'].bb.author
	if kwargs['created'] and author.send_messages:
		send_new_comment_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)
post_save.connect(post_save_dispatcher, sender=Comment)
