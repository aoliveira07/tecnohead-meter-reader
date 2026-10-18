# Validação no Home Assistant real

Registro da implantação no Home Assistant real disponível para o projeto.

## Componentes verificados

- ESPHome Device Builder: 1.14.9.
- ESPHome usado pelo Builder: 2026.9.1.
- App `TecnoHead Meter Reader — Console`: instalado e em funcionamento.
- Versão do App: 0.1.1.
- Ingress: abriu a tela real do console com CSS, JavaScript e API funcionando.
- MQTT do Supervisor: conectado.
- Início automático: habilitado.
- Atalho na barra lateral: habilitado.
- Armazenamento exibido pelo console: `0 B / 256.0 MiB`.
- Mensagens recebidas: `0`; registros descartados: `0`.

## Dashboard

O dashboard nativo `TecnoHead Meter Reader - Laboratorio Serial` foi criado no HA
real em `/tecnohead-meter-reader` e está visível na barra lateral. Ele contém os
cards de segurança, parâmetros seriais, captura, último frame, contadores e
diagnóstico previstos no arquivo [`dashboard/tecnohead-meter-reader.yaml`](../dashboard/tecnohead-meter-reader.yaml).

Como o ESP32 não estava conectado ao host, as entidades do dispositivo ainda não
foram materializadas pelo Native API; os cards aparecem como entidade não encontrada
até o primeiro boot do nó. Isso é uma limitação de hardware, não uma leitura de
tráfego e não deve ser tratado como homologação do firmware.

## Console

O console real exibe a distinção entre:

- HAOS e MQTT conectados;
- canal de captura online, porém sem sessões;
- ausência de frames e armazenamento vazio; e
- limites físicos da bancada, mantendo GPIO17 reservado e TX desativado.

O teste do botão `Marcar teste` foi executado pela tela real. O comando foi aceito
pelo canal MQTT local e não altera UART nem o medidor. Como não havia ESP publicando,
nenhum frame ou sessão foi criado.

## Limite da validação

Não havia ESP32 físico, USB serial ou porta COM disponível neste host. Portanto ainda
não foram comprovados boot do ESP, API Native conectada, aplicação dos selects em
tempo real, bytes TTL enviados pelo simulador e bytes recebidos/exportados. Esses
itens permanecem no checklist de bancada e não são substituídos pela validação do
App ou pela compilação.

Não houve ligação ao Nansen, à porta óptica ou aos terminais RS232. A etapa física
continua pendente de autorização e de conversor RS232↔UART com isolação validada.
