from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_transfersession_is_simulated_chunk_failures'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfersession',
            name='retries',
            field=models.IntegerField(default=0, help_text='Reintentos agregados (announce/chunk) na sessão.', verbose_name='Retries'),
        ),
        migrations.CreateModel(
            name='LookupEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_hash', models.CharField(blank=True, db_index=True, max_length=64)),
                ('hops', models.IntegerField(default=0)),
                ('duration_ms', models.IntegerField()),
                ('success', models.BooleanField(db_index=True, default=False)),
                ('peer_count', models.IntegerField(default=0)),
                ('started_at', models.DateTimeField(db_index=True)),
                ('is_simulated', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Evento de Lookup DHT',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='GossipPropagationEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('msg_id', models.CharField(db_index=True, max_length=64)),
                ('content_hash', models.CharField(db_index=True, max_length=64)),
                ('hop', models.IntegerField(default=0)),
                ('propagation_ms', models.IntegerField()),
                ('recorded_at', models.DateTimeField(db_index=True)),
                ('is_simulated', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Evento de Gossip',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='ChurnEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.CharField(choices=[('node_join', 'Join'), ('node_leave', 'Leave'), ('stale_evict', 'Stale Evict')], db_index=True, max_length=20)),
                ('node_id', models.CharField(db_index=True, max_length=80)),
                ('occurred_at', models.DateTimeField(db_index=True)),
                ('is_simulated', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'Evento de Churn',
                'ordering': ['-occurred_at'],
            },
        ),
    ]
