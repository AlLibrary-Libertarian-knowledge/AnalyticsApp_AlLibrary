from django.db import models
from apps.core.models.base_model import BaseModel

class AcademicDocument(BaseModel):
    """
    Metadados de publicações acadêmicas distribuídas na malha P2P (PDF, EPUB, DOCX).
    Espelha a estrutura de compartilhamento por chunks do DesktopApp_AlLibrary.
    """
    CATEGORY_CHOICES = [
        ('COMPUTACAO', 'Ciência da Computação & IA'),
        ('ENGENHARIA', 'Engenharia de Software & Sistemas'),
        ('SEGURANCA', 'Criptografia, Redes & Tor'),
        ('ECONOMIA', 'Economia & Teoria Monetária'),
        ('DIREITO', 'Direito, Privacidade & Sociedade'),
        ('MATEMATICA', 'Matemática & Teoria da Informação'),
        ('FILOSOFIA', 'Filosofia da Ciência & Epistemologia'),
    ]

    FILE_TYPE_CHOICES = [
        ('PDF', 'Portable Document Format (.pdf)'),
        ('EPUB', 'Electronic Publication (.epub)'),
        ('DOCX', 'Microsoft Word Document (.docx)'),
    ]

    title = models.CharField(max_length=300, db_index=True, verbose_name="Título Acadêmico")
    author = models.CharField(max_length=255, db_index=True, verbose_name="Autor(es)")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, db_index=True, verbose_name="Área de Conhecimento")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='PDF', verbose_name="Formato")
    
    file_size_bytes = models.BigIntegerField(verbose_name="Tamanho (Bytes)")
    content_hash = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="Content Hash (SHA-256)")
    
    chunk_size_bytes = models.IntegerField(default=524288, verbose_name="Tamanho do Chunk (Bytes)")  # 512 KB
    total_chunks = models.IntegerField(verbose_name="Total de Chunks")
    cipher = models.CharField(max_length=50, default="XChaCha20-Poly1305", verbose_name="Algoritmo de Cifra")
    swarm_link = models.CharField(max_length=600, blank=True, verbose_name="Link de Swarm (opocswarm://)")
    
    publication_year = models.IntegerField(default=2024, verbose_name="Ano da Publicação")
    total_downloads = models.IntegerField(default=0, verbose_name="Downloads Totais")
    total_seeds_active = models.IntegerField(default=1, verbose_name="Seeders Ativos")

    class Meta:
        verbose_name = "Documento Acadêmico"
        verbose_name_plural = "Documentos Acadêmicos"
        ordering = ['-total_downloads', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()}) - {self.author}"

    @property
    def file_size_mb(self):
        return round(self.file_size_bytes / (1024 * 1024), 2)
