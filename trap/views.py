from django.shortcuts import render
import pytz
# Create your views here.
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import Acesso, EstatisticasUsuario
from django.http import JsonResponse

def numero_para_texto(numero):
    numeros = {
        1: 'primeira', 2: 'segunda', 3: 'terceira', 4: 'quarta', 5: 'quinta',
        6: 'sexta', 7: 'sétima', 8: 'oitava', 9: 'nona', 10: 'décima',
        11: 'décima primeira', 12: 'décima segunda', 13: 'décima terceira',
        14: 'décima quarta', 15: 'décima quinta', 16: 'décima sexta',
        17: 'décima sétima', 18: 'décima oitava', 19: 'décima nona', 20: 'vigésima'
    }
    return numeros.get(numero, f"{numero}ª")

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    # Obter informações do usuário
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Desconhecido')
    
    # Registrar o acesso
    acesso = Acesso.objects.create(ip=ip, user_agent=user_agent)
    
    # Atualizar estatísticas do usuário
    stats, created = EstatisticasUsuario.objects.get_or_create(ip=ip)
    stats.total_acessos += 1
    stats.ultimo_acesso = timezone.now()
    stats.save()
    
    # Calcular estatísticas por período
    agora = timezone.now()
    
    # Acessos esta semana
    inicio_semana = agora - timedelta(days=agora.weekday())
    acessos_semana = Acesso.objects.filter(
        ip=ip, 
        data_acesso__gte=inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Acessos este mês
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    acessos_mes = Acesso.objects.filter(ip=ip, data_acesso__gte=inicio_mes).count()
    
    # Acessos este ano
    inicio_ano = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    acessos_ano = Acesso.objects.filter(ip=ip, data_acesso__gte=inicio_ano).count()
    
    # Determinar qual período usar na mensagem
    if acessos_semana > 1:
        periodo = "essa semana"
        vezes = acessos_semana
    elif acessos_mes > 1:
        periodo = "esse mês"
        vezes = acessos_mes
    elif acessos_ano > 1:
        periodo = "esse ano"
        vezes = acessos_ano
    else:
        periodo = ""
        vezes = stats.total_acessos
    
    # Converter número para texto
    vezes_texto = numero_para_texto(vezes)
    
    context = {
        'vezes': vezes_texto,
        'periodo': periodo,
        'total_acessos': stats.total_acessos,
        'ip': ip,
        'primeiro_acesso': stats.primeiro_acesso,
    }
    
    return render(request, 'trap/index.html', context)

def estatisticas(request):
    # Usar timezone local (Brasil)
    timezone_brasil = pytz.timezone('America/Sao_Paulo')
    agora = timezone.now().astimezone(timezone_brasil)
    
    # Estatísticas gerais
    total_acessos = Acesso.objects.count()
    usuarios_unicos = EstatisticasUsuario.objects.count()
    
    # Top usuários
    top_usuarios = EstatisticasUsuario.objects.order_by('-total_acessos')[:10]
    
    # Acessos hoje (considerando timezone do Brasil)
    hoje_inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    hoje_fim = hoje_inicio + timedelta(days=1)
    
    acessos_hoje = Acesso.objects.filter(
        data_acesso__gte=hoje_inicio,
        data_acesso__lt=hoje_fim
    ).count()
    
    # Acessos por dia (últimos 7 dias) - considerando timezone
    ultimos_7_dias = []
    max_acessos = 0
    
    for i in range(6, -1, -1):
        data = agora - timedelta(days=i)
        data_inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim = data_inicio + timedelta(days=1)
        
        data_formatada = data.strftime('%d/%m')
        contagem = Acesso.objects.filter(
            data_acesso__gte=data_inicio,
            data_acesso__lt=data_fim
        ).count()
        
        # Atualizar máximo
        if contagem > max_acessos:
            max_acessos = contagem
            
        ultimos_7_dias.append({
            'data': data_formatada, 
            'acessos': contagem
        })
    
    # Garantir que max_acessos seja pelo menos 1 para evitar divisão por zero
    if max_acessos == 0:
        max_acessos = 1
    
    context = {
        'total_acessos': total_acessos,
        'usuarios_unicos': usuarios_unicos,
        'acessos_hoje': acessos_hoje,
        'top_usuarios': top_usuarios,
        'ultimos_7_dias': ultimos_7_dias,
        'max_acessos': max_acessos,
        'agora': agora,  # Para debug
    }
    
    return render(request, 'trap/estatisticas.html', context)

def api_estatisticas(request):
    # API para estatísticas em JSON
    total_acessos = Acesso.objects.count()
    usuarios_unicos = EstatisticasUsuario.objects.count()
    
    hoje = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    acessos_hoje = Acesso.objects.filter(data_acesso__gte=hoje).count()
    
    data = {
        'total_acessos': total_acessos,
        'usuarios_unicos': usuarios_unicos,
        'acessos_hoje': acessos_hoje,
    }
    
    return JsonResponse(data)