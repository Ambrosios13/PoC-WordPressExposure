# 🛡️ PoC - WordPress `wp-cron.php` Exposure

Prova de conceito (PoC) demonstrando uma vulnerabilidade no endpoint `wp-cron.php` do WordPress, identificada durante auditoria real em ambiente autorizado.

Os resultados do teste confirmam como esse endpoint, quando exposto publicamente, pode ser abusado por agentes maliciosos para causar:

- ❌ Negação de serviço (DoS / DDoS)
- 📉 Degradação de desempenho do site

---

## 📌 Sobre

O script contido neste repositório realiza **envio e aumento gradual de carga** via múltiplas requisições ao `wp-cron.php`, monitorando:

- ⏱️ Tempo de resposta  
- 🔁 Timeouts  
- 📊 Estabilidade do serviço  

> Nenhum serviço é derrubado neste processo — trata-se de uma **ação controlada** e segura para fins de PoC.

---

## 🚨 O que é o `wp-cron.php`?

O `wp-cron.php` é um arquivo interno do WordPress responsável por agendar tarefas como publicações, atualizações e verificações automáticas.  
Esse recurso deveria ser acionado **internamente**, apenas quando necessário.

No entanto, muitos sites deixam esse arquivo **acessível pela internet**, permitindo que qualquer um envie requisições diretamente a ele.

---

## ❗ Por que isso é um problema?

Quando o `wp-cron.php` é acessado, o WordPress inicia uma série de processos internos. Se isso ocorrer em grande volume, o servidor pode ficar sobrecarregado — principalmente em ambientes compartilhados ou mal otimizados.

Isso pode causar:

- 🔄 Lentidão geral no site  
- ⚠️ Erros de conexão  
- 💥 Quedas temporárias (DoS – *Denial of Service*)  

---
## ⚙️ Funcionalidade

O código pressiona o sistema com carga crescente por meio de múltiplas threads (unidades paralelas de execução) organizadas em fases sequenciais. A cada nova fase, mais threads são somadas ao teste, intensificando gradualmente o volume de requisições enviadas ao endpoint `wp-cron.php`, com intenção de registrar o impacto no desempenho do serviço.

Durante o processo, o script:

- Envia requisições em alta frequência de forma simultânea
- Registra o tempo de resposta de cada tentativa
- Coleta os códigos de status HTTP (como 200, timeout, erro)
- Gera relatórios com gráficos e estatísticas detalhadas

Essa abordagem permite **observar claramente a degradação do serviço** à medida que a carga aumenta, validando a vulnerabilidade e demonstrando como o endpoint pode ser abusado por agentes maliciosos em um cenário realista de DoS e outros ataques.


## 🛠 Execução


Este script foi desenvolvido em Python 3 e depende das seguintes bibliotecas:

- `requests` – para envio das requisições HTTP
- `matplotlib` – para geração dos gráficos
- `numpy` – para cálculos estatísticos

### ✅ Instalação das dependências

Você pode instalar todos os pacotes necessários com o seguinte comando:

```bash
pip install requests matplotlib numpy  
```


 ## 📦 Outputs do Script

Durante o teste, o script gera automaticamente alguns arquivos que documentam a execução e seus impactos:

### 📝 `baseline.json`
Registra o ponto de partida antes do teste, incluindo:
- Informações do sistema
- URL testada
- Estrutura das fases

### 📊 `dados_brutos_*.json`
Contém todos os dados coletados:
- Latência de cada requisição
- Códigos HTTP retornados
- Timestamps e momentos de troca de fase

### 📈 `estatisticas_*.json`
Resumo por fase com:
- Número de threads 
- Média e mediana de latência
- Sucessos, timeouts e percentuais

### 🖼️ `relatorio_completo_*.png`
Painel visual com gráficos que ilustram:
- Distribuição de latências
- Desempenho por fase
- Capacidade de resposta sob carga

> Esses arquivos permitem analisar com clareza a degradação do serviço e evidenciar o impacto causado por acessos simultâneos ao `wp-cron.php`.
