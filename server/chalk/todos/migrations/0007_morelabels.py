from django.db import migrations

NEW_LABELS = [
    'House',
    'Shopping',
    'chore',
]


def insert_labels(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    for name in NEW_LABELS:
        label = LabelModel(name=name)
        label.save()


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0006_projectlabels'),
    ]

    operations = [
        migrations.RunPython(insert_labels),
    ]
