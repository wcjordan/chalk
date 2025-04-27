from django.db import migrations

NEW_LABELS = [
    'Danyi todo',
    'Test Sheriff',
    'New Jenkins',
    'backlog',
]


def insert_labels(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    for name in NEW_LABELS:
        label = LabelModel(name=name)
        label.save()


class Migration(migrations.Migration):

    dependencies = [
        ('todos',
         '0009_rankordermetadata_alter_historicaltodomodel_options_and_more'),
    ]

    operations = [
        migrations.RunPython(insert_labels),
    ]
