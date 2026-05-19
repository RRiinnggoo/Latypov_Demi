from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

 
class LearnerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learner_profile')
    phone = models.CharField('Контактный телефон', max_length=20)

    class Meta:
        verbose_name = 'Профиль слушателя'
        verbose_name_plural = 'Профили слушателей'

    def __str__(self):
        return self.user.username


class Program(models.Model):
    name = models.CharField('Наименование курса', max_length=160, unique=True)
    summary = models.TextField('Краткое описание')
    hours = models.PositiveSmallIntegerField('Количество часов', default=72)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['name']

    def __str__(self):
        return self.name


class EnrollmentRequest(models.Model):
    class State(models.TextChoices):
        NEW = 'new', 'Новая'
        STUDYING = 'studying', 'Идёт обучение'
        FINISHED = 'finished', 'Обучение завершено'

    class PayType(models.TextChoices):
        CARD = 'card', 'Банковская карта'
        TRANSFER = 'transfer', 'Банковский перевод'
        INSTALLMENT = 'installment', 'Рассрочка'

    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollment_requests')
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name='requests')
    preferred_start = models.DateField('Желаемая дата начала')
    payment = models.CharField('Способ оплаты', max_length=20, choices=PayType.choices)
    state = models.CharField('Статус', max_length=20, choices=State.choices, default=State.NEW)
    created = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created']

    def __str__(self):
        return f'{self.learner.username}: {self.program.name}'

    def clean(self):
        if self.pk:
            old_state = type(self).objects.filter(pk=self.pk).values_list('state', flat=True).first()
            if old_state == self.State.FINISHED and self.state != self.State.FINISHED:
                raise ValidationError('Статус завершённой заявки больше нельзя изменить.')

    @property
    def review_allowed(self):
        return self.state == self.State.FINISHED


class ServiceReview(models.Model):
    request = models.OneToOneField(EnrollmentRequest, on_delete=models.CASCADE, related_name='service_review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_reviews')
    score = models.PositiveSmallIntegerField('Оценка')
    comment = models.TextField('Отзыв')
    published = models.DateTimeField('Дата отзыва', default=timezone.now)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-published']

    def __str__(self):
        return f'Отзыв {self.user.username}'
