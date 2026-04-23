from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_post_updated_at'),
    ]

    operations = [
        # Add Hashtag model
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        # Add hashtags M2M to Post
        migrations.AddField(
            model_name='post',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='api.hashtag'),
        ),
        # Remove category FK from Post
        migrations.RemoveField(
            model_name='post',
            name='category',
        ),
        # Delete Category model
        migrations.DeleteModel(
            name='Category',
        ),
    ]
