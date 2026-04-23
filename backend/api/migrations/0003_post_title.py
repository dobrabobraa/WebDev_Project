from django.db import migrations, models


def backfill_titles(apps, schema_editor):
    """Give existing posts a title derived from their text."""
    Post = apps.get_model('api', 'Post')
    for post in Post.objects.all():
        snippet = (post.text or '').strip().split('\n', 1)[0][:60]
        post.title = snippet or 'Untitled'
        post.save(update_fields=['title'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_profile_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_titles, migrations.RunPython.noop),
    ]
