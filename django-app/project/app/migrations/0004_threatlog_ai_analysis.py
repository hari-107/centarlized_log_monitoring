from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_server_threatlog_enhancements'),
    ]

    operations = [
        migrations.AddField(
            model_name='threatlog',
            name='ai_analyzed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='threatlog',
            name='ai_confidence',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='threatlog',
            name='ai_indicators',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='threatlog',
            name='ai_model',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='threatlog',
            name='ai_recommendation',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='threatlog',
            name='ai_summary',
            field=models.TextField(blank=True, default=''),
        ),
    ]
