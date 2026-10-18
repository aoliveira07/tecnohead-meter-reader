# Instalação no HAOS

## Pré-requisitos

- Home Assistant OS com ESPHome Device Builder instalado.
- Broker MQTT local disponível no Supervisor.
- ESP32 DevKit com ESP32-WROOM-32 confirmado.
- Interface de bancada UART TTL 3,3 V, sem RS232 direto.

## Builder

Importe o YAML do firmware no Device Builder. O arquivo usa as mesmas chaves de segredo normalmente existentes no Builder para Wi-Fi, API e OTA; mantenha os valores fora do repositório. Para o App, o MQTT é obtido pelo Supervisor e não é duplicado na configuração do App.

Antes de gravar, confirme:

1. `rx_pin` é GPIO16.
2. Não existe `tx_pin`.
3. `GPIO17` não aparece na configuração.
4. `Captura RX` inicia desligada.
5. O log de configuração mostra 9600, 8 bits, paridade NONE e 1 stop bit.

## App de console

1. Em **Configurações → Apps → App Store → Repositórios**, adicione o repositório GitHub deste projeto.
2. Instale **TecnoHead Meter Reader — Console**.
3. Inicie o App e abra o painel Ingress.
4. Confirme no console que MQTT está conectado antes de iniciar uma sessão.
5. Use a função de backup do HA para incluir o volume do App; os arquivos ficam em `/data/sessions`.

## Reimplantação

O firmware pode ser atualizado por OTA autenticada depois do primeiro flash USB. Se OTA não estiver disponível, use o fluxo USB do Builder. O App pode ser atualizado independentemente do firmware.
