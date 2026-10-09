# Changelog

## 0.3.9.4

- Publica valores MQTT com retain e QoS 1 para recuperar a última leitura.
- Mantém valores anteriores em leituras parciais, ignorando campos nulos ou vazios.
- Evita enfileirar publicações enquanto o broker estiver desconectado.

## 0.3.9.3

- Renomeia o app e o repositório para Sungrow Inverter.
- Substitui ícone e logo pelas imagens personalizadas.

## 0.3.9.2

- Corrige imagem base, dependências e inicialização para o Supervisor atual.
- Salva configuração em /data e protege argumentos com espaços.
- Corrige descoberta MQTT para modelos com sensores indisponíveis e reconexão.
- Remove configuração duplicada e perfil AppArmor de exemplo (usa o padrão).
- Atualiza documentação e arquiteturas para amd64 e aarch64.

## 0.3.3.1
- Update to Sungather July-8 commit

## 0.3.3
- Create only necessary sensors according to Scan_level

## 0.3.2
- Add option model to force detect
- Add internal temperature sensor

## 0.3.1
- Remove conflict config.json file

## 0.3
- Use new source SunGather
- Auto detect Inverter model

## 0.2.2
- Add Sungrow-SG7RT
- ModbusWebClient (port 8082) support WiNet-S dongle
- Fix metric name

## 0.2.1.1
- Fix energy unit of measurement

## 0.2.1 
- Support SH10RT


## 0.2 
- MQTT Auto Discovery

## 0.1

- release first version


