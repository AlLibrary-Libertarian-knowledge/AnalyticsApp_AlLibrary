from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_peernode_city_peernode_node_alias_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfersession',
            name='is_simulated',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='True para dados gerados por seed_tcc_analytics; False para telemetria medida no desktop.',
                verbose_name='Simulado (seed)',
            ),
        ),
        migrations.AddField(
            model_name='transfersession',
            name='chunk_failures',
            field=models.IntegerField(
                default=0,
                help_text='Tentativas de chunk que falharam (decrypt/rede) antes do sucesso ou abandono.',
                verbose_name='Falhas de chunk',
            ),
        ),
    ]
