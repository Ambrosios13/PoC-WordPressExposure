# PoC-WordPressExposure

Prova de conceito (PoC) autorizada demonstrando uma vulnerabilidade no endpoint `wp-cron.php` do WordPress. O teste confirma como esse endpoint, quando exposto publicamente, pode ser abusado por atores maliciosos para causar negação de serviço (DoS/DDoS) ou degradação de desempenho do site atráves de sobrecarga no sistema.

## 📌 Sobre

O script contido neste repositório simula um aumento gradual de carga via múltiplas requisições ao `wp-cron.php`, monitorando tempo de resposta, timeouts e estabilidade do serviço. Nenhum serviço é derrubado neste processo — trata-se apenas de uma simulação controlada para fins de auditoria.

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
