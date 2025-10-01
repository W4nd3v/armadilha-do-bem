from django.db import models
from django.utils import timezone

class Acesso(models.Model):
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    data_acesso = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'acessos'
        ordering = ['-data_acesso']
    
    def __str__(self):
        return f"{self.ip} - {self.data_acesso.strftime('%d/%m/%Y %H:%M')}"

class EstatisticasUsuario(models.Model):  # CORRIGIDO: estava EstatisticasUsuario
    ip = models.GenericIPAddressField(unique=True)
    total_acessos = models.IntegerField(default=0)
    primeiro_acesso = models.DateTimeField(default=timezone.now)
    ultimo_acesso = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'estatisticas_usuario'
    
    def __str__(self):
        return f"{self.ip} - {self.total_acessos} acessos"