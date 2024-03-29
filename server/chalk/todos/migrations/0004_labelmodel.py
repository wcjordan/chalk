# Generated by Django 3.2.5 on 2021-10-10 19:51

from django.db import migrations, models

DEFAULT_LABELS = [
    'low-energy',
    'high-energy',
    'vague',
    'work',
    'home',
    'errand',
    'mobile',
    'desktop',
    'email',
    'urgent',
    '5 minutes',
    '25 minutes',
    '60 minutes',
]


def insert_labels(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    for name in DEFAULT_LABELS:
        label = LabelModel(name=name)
        label.save()


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0003_historicaltodomodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabelModel',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.RunPython(insert_labels),
    ]
