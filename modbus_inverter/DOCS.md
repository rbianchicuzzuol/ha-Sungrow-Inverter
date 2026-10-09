# Configuração

Requer Mosquitto broker iniciado e integração MQTT configurada. O app obtém endereço e credenciais pelo serviço MQTT do Supervisor.

| Opção | Uso |
| --- | --- |
| Inverter_host | IP ou hostname do inversor, obrigatório para iniciar. |
| Inverter_port | Porta TCP, normalmente 502. |
| Inverter_model | Modelo Sungrow; vazio permite detecção automática. |
| Smart_meter | Ative se houver medidor compatível. |
| Connection | Sungrow, Modbus ou HTTP. Todos usam registros Sungrow; HTTP usa porta 8082. |
| Scan_level | BASIC, STANDARD, DETAIL ou ALL. Prefira STANDARD. |
| Scan_interval | Intervalo de 10 a 600 segundos. |
| Scan_timeout | Timeout de 3 a 60 segundos. |
| Log_level | INFO, WARNING, ERROR ou DEBUG. |

Reinicie após mudar as opções. O inversor deve permitir acesso pela rede. Compatibilidade HTTP depende do dongle.
O app publica em inverter/<modelo>/registers e descoberta em homeassistant/. Sensores indisponíveis são ignorados.
ALL consulta registros que o equipamento pode não suportar. Os sensores aparecem na integração MQTT; não há interface web.

A configuração gerada fica em /data/config.sg com credenciais MQTT e permissões restritas. Não publique esse arquivo.
Para erros de instalação consulte o Supervisor; para erros de inicialização e leitura consulte o log do app.
Suporte SMA não está implementado.

## Últimos dados quando o inversor estiver offline

Os dados são publicados com MQTT retain e QoS 1. O broker mantém a última mensagem
e a entrega quando o Home Assistant reinicia ou volta a assinar o tópico.
Não há prazo de expiração nem tópico de disponibilidade para os sensores.
Se o inversor ficar offline, os valores exibidos são a última leitura, não dados atuais.
Uma leitura parcial mantém em memória os registros anteriores até serem atualizados.
Essa mesclagem em memória é reiniciada quando o app reinicia.

Para manter mensagens retidas após reiniciar o broker, a persistência do broker
também deve estar habilitada. O app não altera a configuração do Mosquitto.
Após instalar esta versão, aguarde pelo menos uma leitura bem-sucedida para gravar
a mensagem retida. Dados antigos enviados sem retain não podem ser recuperados.
