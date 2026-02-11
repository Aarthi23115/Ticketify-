from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='qr_secret',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='qr_status',
            field=models.CharField(default='ACTIVE', max_length=20),
        ),
        migrations.AddField(
            model_name='ticket',
            name='last_qr_generated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='TicketScanLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField(default=False)),
                ('remote_addr', models.CharField(max_length=100, null=True, blank=True)),
                ('device_info', models.CharField(max_length=256, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scan_logs', to='events.ticket')),
            ],
            options={
                'ordering': ['-scanned_at'],
            },
        ),
    ]
