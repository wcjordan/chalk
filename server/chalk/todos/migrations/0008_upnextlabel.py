from django.db import migrations


def insert_upnext_label(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    label = LabelModel(name='up next')
    label.save()


def remove_den_setup_label(apps, schema_editor):
    LabelModel = apps.get_model("todos", "LabelModel")
    label = LabelModel.objects.filter(name='Den Setup')
    label.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0007_morelabels'),
    ]

    operations = [
        migrations.RunPython(insert_upnext_label),
        migrations.RunPython(remove_den_setup_label),
    ]
