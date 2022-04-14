from django.db import migrations

NEW_LABELS = [
    'Chalk',
    'Den Setup',
    'Jenkins',
    'Infra',
]


def insert_labels(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    for name in NEW_LABELS:
        label = LabelModel(name=name)
        label.save()


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0005_labelmodel_todo_set'),
    ]

    operations = [
        migrations.RunPython(insert_labels),
    ]
