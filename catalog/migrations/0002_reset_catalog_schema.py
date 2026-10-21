from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(name='ModelOption'),
        migrations.DeleteModel(name='OptionCategory'),
        migrations.DeleteModel(name='TerrainCategory'),
        migrations.DeleteModel(name='ChaletModel'),
        migrations.DeleteModel(name='Terrain'),
        migrations.DeleteModel(name='Option'),
        migrations.CreateModel(
            name='ChaletModel',
            fields=[
                ('slug', models.SlugField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('subtitle', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=100)),
                ('surface_area', models.PositiveIntegerField()),
                ('surface_unit', models.CharField(default='m²', max_length=10)),
                ('bedrooms', models.PositiveSmallIntegerField()),
                ('bathrooms', models.PositiveSmallIntegerField()),
                ('max_guests', models.PositiveSmallIntegerField()),
                ('base_price', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('image', models.URLField(max_length=500)),
                ('gallery', models.JSONField(default=list)),
                ('features', models.JSONField(default=list)),
            ],
            options={'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='Terrain',
            fields=[
                ('slug', models.SlugField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=150)),
                ('country', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('surface_area', models.PositiveIntegerField()),
                ('surface_unit', models.CharField(default='m²', max_length=10)),
                ('base_price', models.PositiveIntegerField()),
                ('image', models.URLField(max_length=500)),
                ('gallery', models.JSONField(default=list)),
                ('features', models.JSONField(default=list)),
            ],
            options={'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('slug', models.SlugField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150)),
                ('short_description', models.TextField()),
                ('description', models.TextField()),
                ('price', models.PositiveIntegerField()),
                ('image', models.URLField(max_length=500)),
                ('popular', models.BooleanField(default=False)),
            ],
            options={'ordering': ('name',)},
        ),
    ]
