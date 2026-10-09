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

## Sensores adicionais (0.3.9.5)

Selecione `Scan_level: DETAIL` e reinicie o app para ler MPPT, potência nominal,
frequência e diagnóstico. Novas instalações usam DETAIL como padrão; opções de
instalações existentes são preservadas pelo Supervisor. Não é necessário usar ALL.

Os registros são filtrados pelo modelo configurado ou detectado e pelo nível de
leitura. A descoberta MQTT de um novo sensor ocorre somente quando chega seu
primeiro valor válido. Nem todos os modelos fornecem todos os registros.

| Grupo | Novos dados |
| --- | --- |
| Energia | Geração total, mensal e anual PV quando o registro existir; importação e exportação diária e total. |
| MPPT | Tensão, corrente e potência de cada MPPT suportado. |
| Rede | Frequência, fator de potência e potências aparente e reativa. Correntes e tensões de fase já são medidas pelo app. |
| Diagnóstico | Status, códigos de alarme, firmware ARM/DSP, número de série e horas de operação. |
| Comunicação | Last Communication: horário local com fuso da última leitura bem-sucedida. |

Firmware e alarmes são expostos no formato fornecido pelo mapa de registros.
Não se deve interpretar automaticamente todo código diferente de zero como falha.
A segunda temperatura do exemplo de outro inversor não é inferida.

### Cálculos

- MPPT Power (W): tensão (V) multiplicada pela corrente (A) do mesmo MPPT.
- Equivalent Sun Hours (h): geração diária (kWh) dividida pela potência nominal (kW).
- Inverter Utilization (%): potência AC atual dividida pela nominal, com conversão kW/W.
- Conversion Efficiency Estimated (%): potência AC dividida pela DC. É apenas
  indicativa, especialmente em inversores híbridos com bateria; não é uma medição de laboratório.
- Grid Current Estimated (A): corrente ativa equivalente com fator de potência 1.
  Para ligação 2P usa P/V; para 3P4L usa P/(Va+Vb+Vc), supondo fases equilibradas
  e tensões fase-neutro. Outros tipos de ligação não são estimados.
  A corrente real medida por fase continua disponível e deve ser preferida.

Cálculos usam dados da mesma leitura, sem misturar valores retidos com valores
novos. Entradas ausentes, inválidas ou denominadores zero não geram novo cálculo;
a última estimativa válida continua retida. Last Communication indica atualização
 do coletor, não garante que todos os registros tenham sido atualizados naquela leitura.

### Geração mensal e anual sem registro nativo

No Home Assistant, crie dois ajudantes Medidor de consumo (Utility Meter), usando
Total Generation como origem, com ciclos mensal e anual. Isso preserva os acumulados
nos reinícios do Home Assistant. O primeiro mês/ano é parcial: o histórico anterior
não pode ser reconstruído somente a partir da geração total atual.

Há um exemplo YAML em `examples/utility-meter-example.yaml` na raiz do repositório.
Substitua a entidade de origem pela entidade real do seu sensor de geração total.
Os ajudantes são opcionais e precisam ser criados no Home Assistant; o app não os
instala automaticamente.
