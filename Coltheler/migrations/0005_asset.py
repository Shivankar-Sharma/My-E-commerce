from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import Coltheler.models


class Migration(migrations.Migration):
    dependencies = [
        ("Coltheler", "0004_alter_potemplate_reference"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to=Coltheler.models.asset_upload_path)),
                ("original_name", models.CharField(max_length=255)),
                ("relative_dir", models.CharField(blank=True, default="", max_length=255)),
                ("size", models.BigIntegerField(default=0)),
                ("content_type", models.CharField(blank=True, default="", max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "asset_file"},
        ),
        migrations.AddIndex(
            model_name="asset",
            index=models.Index(fields=["uploaded_by", "created_at"], name="asset_file_uploade_4fec67_idx"),
        ),
        migrations.AddIndex(
            model_name="asset",
            index=models.Index(fields=["relative_dir"], name="asset_file_relativ_8f3f39_idx"),
        ),
    ]
