# Generated manually 2026-04-06
# Adds db_index to guid and link on all 11 RSS content tables for query performance.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_increase_content_name_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aicontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='aicontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='aimedicalimagingcontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='aimedicalimagingcontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='cryptocontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='cryptocontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='cybersecuritycontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='cybersecuritycontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='generalcontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='generalcontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='jobupdatescontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='jobupdatescontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='medicalnewscontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='medicalnewscontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='mobilepccontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='mobilepccontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='pythoncontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='pythoncontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='softwaredevelopmentcontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='softwaredevelopmentcontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='uiuxcontent',
            name='guid',
            field=models.CharField(db_index=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='uiuxcontent',
            name='link',
            field=models.URLField(db_index=True, max_length=2000),
        ),
    ]
