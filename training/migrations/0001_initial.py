 
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160, unique=True, verbose_name='Наименование курса')),
                ('summary', models.TextField(verbose_name='Краткое описание')),
                ('hours', models.PositiveSmallIntegerField(default=72, verbose_name='Количество часов')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LearnerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20, verbose_name='Контактный телефон')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='learner_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль слушателя',
                'verbose_name_plural': 'Профили слушателей',
            },
        ),
        migrations.CreateModel(
            name='EnrollmentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_start', models.DateField(verbose_name='Желаемая дата начала')),
                ('payment', models.CharField(choices=[('card', 'Банковская карта'), ('transfer', 'Банковский перевод'), ('installment', 'Рассрочка')], max_length=20, verbose_name='Способ оплаты')),
                ('state', models.CharField(choices=[('new', 'Новая'), ('studying', 'Идёт обучение'), ('finished', 'Обучение завершено')], default='new', max_length=20, verbose_name='Статус')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollment_requests', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requests', to='training.program')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='ServiceReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(verbose_name='Оценка')),
                ('comment', models.TextField(verbose_name='Отзыв')),
                ('published', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата отзыва')),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='service_review', to='training.enrollmentrequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-published'],
            },
        ),
    ]
