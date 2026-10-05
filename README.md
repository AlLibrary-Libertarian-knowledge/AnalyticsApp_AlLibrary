# 📊 AlLibrary Analytics Hub (Backend Django & Jazzmin)

Módulo backend de **Analytics, Telemetria P2P e Coleta de Resultados** para o projeto **AlLibrary**. Desenvolvido com **Python 3.12**, **Django 5**, **Django REST Framework (DRF)**, **drf-yasg (Swagger/ReDoc)** e interface administrativa **Jazzmin Darkly**, estruturado sob rigorosos padrões de engenharia de software e boas práticas de banco de dados.

O hub fornece toda a infraestrutura de telemetria consumida pelo painel web moderno [AnalyticsNextApp_AlLibrary](https://github.com/AlLibrary-Libertarian-knowledge/AnalyticsNextApp_AlLibrary).

---

## 🎯 Finalidade & Objetivos da Rede P2P

O **AlLibrary** é uma biblioteca digital distribuída, descentralizada e imutável voltada à preservação e livre circulação de acervos científicos e acadêmicos. Este serviço centraliza e processa os dados de telemetria empírica da rede para validação experimental de hipóteses científicas:

1. **Gargalo Individual em Redes Onion:** Circuitos Tor Hidden Services (`.onion`) apresentam limitação natural de banda individual (~230 a 410 KB/s por túnel).
2. **Escala por Multi-Semeadura Paralela:** Com a divisão dos arquivos em blocos criptografados de 512 KB (**XChaCha20-Poly1305**), o download paralelo a partir de múltiplos nós (*swarms*) atinge entre **1.8 MB/s e 2.9 MB/s** (ganho de mais de **5.1x** em throughput).
3. **Distribuição Realista de Erros:** Simulação de condições reais de tráfego Tor, contemplando ~92.1% de sucesso, ~5.2% de timeouts de circuitos lentos e ~2.7% de detecções de integridade Poly1305 MAC.
4. **Garantia Criptográfica de Anonimato:** Em estrita aderência ao protocolo, o sistema **não registra a identidade do requisitante do download**. As sessões de transferência (`TransferSession`) mantêm o campo `target_node=None` (downloads 100% anônimos via circuitos efêmeros Tor v3). O cadastro de nós (`PeerNode`) documenta exclusivamente os 14 voluntários reais que cederam suas máquinas como nós de semeadura (*seeders*).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Framework Web:** Django 5.x
* **API REST:** Django REST Framework (DRF)
* **Documentação OpenAPI:** drf-yasg (Swagger & ReDoc)
* **Tema Administrativo:** Jazzmin (*Theme Darkly* com Font Awesome 5)
* **Segurança e CORS:** `django-cors-headers`
* **Banco de Dados:** SQLite (Desenvolvimento/Demonstração) / PostgreSQL-ready

---

## 🏗️ Arquitetura e Modelos de Dados

O projeto segue arquitetura modular desacoplada:

```text
AnalyticsApp_AlLibrary/
├── apps/
│   ├── core/                      # Modelos base abstratos (UUID, timestamps), paginação e mixins
│   │   ├── models/base_model.py
│   │   ├── admin_mixins.py        # Exportação CSV padronizada
│   │   └── pagination.py          # StandardResultsSetPagination (anti full-scan)
│   └── analytics/                 # Domínio de telemetria da rede P2P
│       ├── models/
│       │   ├── node.py            # PeerNode (Topologia dos 14 nós voluntários)
│       │   ├── document.py        # AcademicDocument (Acervo de papers e livros)
│       │   ├── swarm.py           # SwarmSnapshot (Disponibilidade de chunks)
│       │   ├── transfer.py        # TransferSession (Sessões de download anônimas)
│       │   ├── network_metric.py  # DailyNetworkMetric (Série temporal Julho-Outubro)
│       │   └── chunk_metric.py    # ChunkPerformanceLog (Throughput por bloco)
│       ├── serializers/           # DTOs e serializadores DRF otimizados (sem N+1)
│       ├── views/                 # ViewSets REST, filtros e agregadores de KPIs
│       ├── admin/                 # Interfaces administrativas personalizadas
│       └── management/commands/
│           └── seed_tcc_analytics.py # Seeder automatizado da telemetria real
├── config/                        # Configurações do Django (settings, urls, wsgi/asgi)
├── requirements.txt               # Dependências do projeto
├── manage.py
└── .env.example                   # Modelo de configuração de ambiente
```

---

## 🚀 Como Executar o Backend

### 1. Clonar o Repositório e Acessar a Pasta
```bash
git clone git@github.com:AlLibrary-Libertarian-knowledge/AnalyticsApp_AlLibrary.git
cd AnalyticsApp_AlLibrary
```

### 2. Criar e Ativar o Ambiente Virtual (venv)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
*(As configurações padrão já estão pré-ajustadas para execução local imediata).*

### 5. Executar as Migrações do Banco de Dados
```bash
python manage.py migrate
```

### 6. Executar o Seeding de Dados Realistas (Julho a Outubro de 2026)
Popula os 14 nós participantes voluntários reais, o acervo acadêmico (incluindo o teste de estresse do paper do Bitcoin com 10 nós simultâneos), transferências anônimas e métricas diárias:
```bash
python manage.py seed_tcc_analytics
```

### 7. (Opcional) Criar Superusuário para o Admin
Caso queira acessar o painel administrativo:
```bash
python manage.py createsuperuser
```
*(Ou utilize o superusuário de desenvolvimento se gerado previamente: `admin` / `admin123`).*

### 8. Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver 127.0.0.1:8000
```
O backend estará disponível em `http://127.0.0.1:8000`.

---

## 🖥️ Executando em Conjunto com o Frontend Next.js

Para visualizar a experiência completa com a interface visual:

1. Mantenha o backend rodando no terminal 1:
   ```bash
   cd AnalyticsApp_AlLibrary
   source venv/bin/activate
   python manage.py runserver 127.0.0.1:8000
   ```

2. Em um segundo terminal, inicie o frontend Next.js:
   ```bash
   cd ../AnalyticsNextApp_AlLibrary
   npm install
   npm run dev
   ```

3. Abra o navegador em: **[http://localhost:3000](http://localhost:3000)**.

---

## 📡 Endpoints REST & Documentação da API

A documentação interativa com Swagger e ReDoc está disponível nativamente:
* **Swagger UI:** `http://127.0.0.1:8000/swagger/`
* **ReDoc:** `http://127.0.0.1:8000/redoc/`

### Principais Rotas da API (`/api/v1/`):
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/v1/overview/` | KPIs consolidados da rede (Total de nós, transferências, volume transferido, latência e integridade) |
| `GET` | `/api/v1/speed-benchmarks/` | Curva comparativa de Throughput (MB/s) em função do número de seeders paralelos |
| `GET` | `/api/v1/timeline/` | Série temporal (Julho a Outubro) com dias ativos, fins de semana e pausas |
| `GET` | `/api/v1/documents/` | Catálogo de documentos acadêmicos e status de replicação de chunks |
| `GET` | `/api/v1/nodes/` | Topologia e métricas dos 14 nós voluntários da rede P2P |
| `GET` | `/api/v1/transfers/` | Histórico de sessões de download anônimas com tempo, seeds e velocidade |

---

## 👥 Os 14 Nós Voluntários da Rede

A telemetria registra 14 nós sementes voluntários operados pelos integrantes e colaboradores do projeto:
* **Integrantes do Projeto:** Eduardo Prestes (*Sorocaba/SP*), Tales Augusto (*Araçoiaba da Serra/SP*), Arthur Leticio (*Sorocaba/SP*).
* **Colaboradores e Amigos (Sorocaba e Região):** Pedro Andrade, Murilo Duarte, Alexandre Cussiol, Victor Hugo, Vitor Vidoto, Michael Carporas, Henry Almeida, Kaique Vecchia, Lucas Ferreira.
* **Colaboradores e Amigos (Rio Grande do Sul):** Cristiano Yeaguer (*Porto Alegre/RS*), Rodrigo Becker (*Porto Alegre/RS*).

---

## 📜 Licença
Projeto distribuído sob a licença MIT. Consulte o arquivo de licença para mais detalhes.
