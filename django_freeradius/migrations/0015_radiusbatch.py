# Generated by Django 2.0.2 on 2018-03-12 15:18

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_freeradius', '0014_auto_20171226_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='RadiusBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('expiration_date', models.DateTimeField(blank=True, null=True, verbose_name='expiration time')),
                ('radcheck', models.ManyToManyField(to=settings.DJANGO_FREERADIUS_RADIUSCHECK_MODEL)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'radius batch',
                'verbose_name_plural': 'radius batches',
                'db_table': 'radbatch',
                'abstract': False,
                'swappable': 'DJANGO_FREERADIUS_RADIUSBATCH_MODEL',
            },
        ),
    ]
