# Sungrow Inverter para Home Assistant

App baseado em SunGather para ler inversores Sungrow pela rede e publicar dados e descoberta de sensores no MQTT do Home Assistant.

## Instalação

1. Envie este diretório para a branch principal do GitHub, incluindo repository.yaml e a pasta inteira modbus_inverter. Não envie .validation.
2. Na loja de Apps (ou Complementos), adicione o repositório https://github.com/rbianchicuzzuol/ha-ModbusTCP2MQTT.
3. Instale e inicie o Mosquitto broker e configure a integração MQTT.
4. Instale Sungrow Inverter, configure Inverter_host e inicie o app.
5. Consulte o log do app e os dispositivos da integração MQTT.

Arquiteturas: amd64 e aarch64. O Supervisor constrói a imagem; não é necessário build.yaml.
Veja [as opções](modbus_inverter/DOCS.md).

## Limitações

O coletor utiliza apenas registros Sungrow. O arquivo SMA original não contém um mapa utilizável. Suporte SMA não está implementado.
A compatibilidade depende do modelo, firmware e acesso de rede do inversor.
O ambiente local não tem Docker: os testes Python não substituem a instalação da imagem Linux no Supervisor e a leitura do equipamento real.

## Origem

Baseado em [MatterVN/ModbusTCP2MQTT](https://github.com/MatterVN/ModbusTCP2MQTT) e [SunGather](https://github.com/bohdan-s/SunGather).
Licença original em modbus_inverter/LICENSE.
