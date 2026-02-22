# Generated manually for image upload flow

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0006_rename_prediction_to_predicted_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalattachment',
            name='file_path',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
