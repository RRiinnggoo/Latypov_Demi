from django.contrib.auth.hashers import make_password
from django.db import migrations

 
PROGRAMS = [
    ('Основы алгоритмизации и программирования', 'Алгоритмы, логика и первые программы.', 72),
    ('Основы веб-дизайна', 'HTML, CSS, композиция и адаптивные интерфейсы.', 64),
    ('Основы проектирования баз данных', 'Таблицы, связи, ключи и ER-структура.', 80),
]


def seed(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Program = apps.get_model('training', 'Program')

    User.objects.update_or_create(
        username='Admin26',
        defaults={
            'password': make_password('Demo20'),
            'is_staff': True,
            'is_superuser': False,
            'is_active': True,
        },
    )
    for name, summary, hours in PROGRAMS:
        Program.objects.update_or_create(name=name, defaults={'summary': summary, 'hours': hours})


def reverse_seed(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='Admin26').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, reverse_seed),
    ]
