from django.contrib import admin
from .models import Acesso, EstatisticasUsuario  # CORRIGIDO: estava EstadisticasUsuario

@admin.register(Acesso)
class AcessoAdmin(admin.ModelAdmin):
    list_display = ['ip', 'data_acesso', 'user_agent_short']
    list_filter = ['data_acesso']
    search_fields = ['ip', 'user_agent']
    
    def user_agent_short(self, obj):
        return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'

@admin.register(EstatisticasUsuario)  # CORRIGIDO: estava EstatisticasUsuario
class EstatisticasUsuarioAdmin(admin.ModelAdmin):
    list_display = ['ip', 'total_acessos', 'primeiro_acesso', 'ultimo_acesso']
    list_filter = ['ultimo_acesso']
    search_fields = ['ip']
    readonly_fields = ['total_acessos', 'primeiro_acesso', 'ultimo_acesso']