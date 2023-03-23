# Generated by Django 4.1.7 on 2023-03-23 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='имя')),
            ],
            options={
                'verbose_name': 'клиент',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'verbose_name': 'продукция',
            },
        ),
        migrations.CreateModel(
            name='StockRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('limit', models.PositiveIntegerField(verbose_name='общий лимит')),
                ('employed_limit', models.IntegerField(default=0, verbose_name='используемый лимит')),
            ],
            options={
                'verbose_name': 'склад',
            },
        ),
        migrations.CreateModel(
            name='StockRoomBasket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit', models.PositiveIntegerField(verbose_name='лимит')),
                ('employed_limit', models.IntegerField(default=0, verbose_name='используемый лимит')),
                ('tariff', models.DecimalField(decimal_places=1, help_text='за единицу продукта', max_digits=10, verbose_name='тариф')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockroom_baskets', to='stockroom.product', verbose_name='продукция')),
                ('stockroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockroom_baskets', to='stockroom.stockroom', verbose_name='склад')),
            ],
            options={
                'verbose_name': 'позиция на складе',
            },
        ),
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.PositiveIntegerField(verbose_name='дистанция')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roads', to='stockroom.client', verbose_name='клиент')),
                ('stockroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roads', to='stockroom.stockroom', verbose_name='склад')),
            ],
        ),
        migrations.CreateModel(
            name='ProductBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='количество')),
                ('object_id_own', models.PositiveIntegerField()),
                ('object_id_holder', models.PositiveIntegerField()),
                ('content_type_holder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
                ('content_type_own', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stockroom.product', verbose_name='продукция')),
            ],
        ),
    ]
