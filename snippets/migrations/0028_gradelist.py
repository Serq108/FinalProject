# Generated by Django 2.2.5 on 2019-09-11 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snippets', '0027_delete_gradelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradeList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(default=False)),
                ('course_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coursepage', to='snippets.CoursePage')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cadet', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
