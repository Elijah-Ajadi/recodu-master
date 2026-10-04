# Generated migration to explicitly alter phone field to null=True on existing databases

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0005_alter_patient_gender_alter_patient_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='phone',
            field=models.CharField(
                blank=True,
                max_length=15,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Enter a valid phone number.',
                        regex='^[\\+]?[\\d\\s\\-]{7,15}$',
                    )
                ],
            ),
        ),
    ]
