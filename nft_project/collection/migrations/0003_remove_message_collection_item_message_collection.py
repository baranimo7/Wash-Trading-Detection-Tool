# Generated by Django 4.0.1 on 2022-09-18 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0002_collectionitem_alter_collection_field_id_message_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='collection_item',
        ),
        migrations.AddField(
            model_name='message',
            name='collection',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='collection.collection'),
            preserve_default=False,
        ),
    ]
