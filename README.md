# PoC-WordPressExposure

Prova de conceito (PoC) autorizada demonstrando uma vulnerabilidade no endpoint `wp-cron.php` do WordPress. O teste confirma como esse endpoint, quando exposto publicamente, pode ser abusado por atores maliciosos para causar negação de serviço (DoS/DDoS) ou degradação de desempenho do site atráves de sobrecarga no sistema.

## 📌 Sobre

O script contido neste repositório simula um aumento gradual de carga via múltiplas requisições ao `wp-cron.php`, monitorando tempo de resposta, timeouts e estabilidade do serviço. Nenhum serviço é derrubado neste processo — trata-se apenas de uma simulação controlada para fins de auditoria.

## 🚨 O que é o `wp-cron.php`?

O `wp-cron.php` é um arquivo interno do WordPress que serve para agendar tarefas como publicações, atualizações e verificações. Ele deveria ser chamado pelo próprio sistema em momentos específicos. 

Porém, **muitos sites deixam esse arquivo acessível pela internet**, permitindo que qualquer um envie requisições diretamente a ele.

---

## ❗ Por que isso é um problema?

Quando o `wp-cron.php` é acionado, o WordPress executa uma série de processos internos. Se esse arquivo for acessado muitas vezes seguidas, **o servidor pode ficar sobrecarregado** — especialmente em hospedagens compartilhadas ou mal otimizadas.

Esse tipo de abuso pode causar:

- 🔄 Lentidão geral no site  
- ⚠️ Erros de conexão  
- 💥 Quedas temporárias (DoS – *Denial of Service*)  


## ⚙️ Funcionalidades

- Testes escalonados com múltiplas threads
- Coleta de métricas de latência e códigos HTTP
- Geração de gráficos e relatório completo
- Identificação do ponto de degradação
- Teste seguro e limitado (12s por fase)

## 🛠 Execução

```bash
pip install matplotlib requests numpy
python wp-cron.php_DOS.py
