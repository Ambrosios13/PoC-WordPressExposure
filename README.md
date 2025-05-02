# 🛡️ PoC - WordPress `wp-cron.php` Exposure

> 🚨 **DISCLAIMER:** Este material resulta de testes éticos consentidos realizados **exclusivamente** em ambiente com **permissão legal expressa**.  
> A utilização deste projeto em sites ou sistemas para os quais você **não tem permissão** é **ilegal**.


Prova de conceito (PoC) demonstrando uma vulnerabilidade no endpoint `wp-cron.php` do WordPress, identificada durante auditoria real em ambiente autorizado.

Os resultados do teste confirmam como esse endpoint, quando exposto publicamente, pode ser abusado por agentes maliciosos para causar:

- ❌ Negação de serviço (DoS / DDoS)
- 📉 Degradação controlada de desempenho do site

---

## 📌 Sobre

O script contido neste repositório realiza **envio e aumento gradual de carga** via múltiplas requisições ao `wp-cron.php`, monitorando:

- ⏱️ Tempo de resposta  
- 🔁 Timeouts  
- 📊 Estabilidade do serviço  

> No exemplo em questão nenhum serviço foi derrubado durante os testes — trata-se de uma **ação controlada** e segura para fins de PoC.

---

## 🚨 O que é o `wp-cron.php`?

O `wp-cron.php` é um arquivo do WordPress usado para agendar tarefas como publicações e atualizações automáticas. Ele deveria ser acionado **internamente**, mas muitos sites deixam o arquivo **acessível pela internet**, o que pode permitir que qualquer pessoa envie requisições e potencialmente explore falhas de segurança.

Para aumentar a segurança, é recomendável bloquear o acesso externo ao arquivo ou desativá-lo, configurando o cron manualmente.


---

## ❗ Por que isso é um problema?

Quando o `wp-cron.php` é acessado, o WordPress inicia uma série de processos internos. Se isso ocorrer em grande volume, o servidor pode ficar sobrecarregado — principalmente em ambientes compartilhados ou mal otimizados.

Isso pode causar:

- 🔄 Lentidão geral no site  
- ⚠️ Erros de conexão  
- 💥 Quedas temporárias (DoS – *Denial of Service*)  

---

## 🎥 PoC.mp4 – Demonstração do Ataque

O vídeo `PoC.mp4` apresenta uma gravação prática da execução do script de carga contra um site WordPress com o endpoint `wp-cron.php` publicamente acessível.

Durante a demonstração, é possível observar:

- O script sendo executado em fases crescentes de requisições
- A resposta do site sendo progressivamente afetada
- Momentos de lentidão e instabilidade causados pela sobrecarga
- Evidência visual do impacto que acessos automatizados ao `wp-cron.php` podem causar

Essa gravação serve como **validação visual da vulnerabilidade explorada**, destacando a importância de restringir o acesso externo a esse endpoint mesmo em ambientes de baixo tráfego.

> Nenhum sistema real foi prejudicado durante o experimento — o teste foi conduzido em ambiente autorizado e monitorado.

---
## ⚙️ Funcionalidade

O código pressiona o sistema com carga crescente por meio de múltiplas threads (unidades paralelas de execução) organizadas em fases sequenciais. A cada nova fase, mais threads são somadas ao teste, intensificando gradualmente o volume de requisições enviadas ao endpoint `wp-cron.php`, com intenção de registrar o impacto no desempenho do serviço.

Durante o processo, o script:

- Envia requisições em alta frequência de forma simultânea
- Registra o tempo de resposta de cada tentativa
- Coleta os códigos de status HTTP (como 200, timeout, erro)
- Gera relatórios com gráficos e estatísticas simples para evidenciar a degradação.

Essa abordagem permite **observar claramente a degradação do serviço** à medida que a carga aumenta, validando a vulnerabilidade e demonstrando como o endpoint pode ser abusado por agentes maliciosos em um cenário realista de Flooding escalonando para DoS/DDoS.


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
- Informações do sistema auditor
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

---

## 🛡️ Mitigação

Mitigar essa exposição é simples e necessário: **basta impedir que o endpoint `wp-cron.php` seja acessível via browser para qualquer utilizador**.

Isso pode ser feito configurando o servidor ou o próprio WordPress para que o arquivo seja acessível apenas **internamente** e não para qualquer usuario via browser. Essa medida elimina o risco de abusos automatizados, mantendo o agendador do WordPress funcional e seguro.

