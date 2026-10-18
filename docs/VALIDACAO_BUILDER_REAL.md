# Validação no ESPHome Device Builder real

Registro da execução no Home Assistant real (`ESPHome Device Builder 1.14.9`, `ESPHome 2026.9.1`), em 17/10/2026.

## Resultado

- Arquivo importado: `tecnohead-meter-reader.yaml`.
- Placa selecionada: `Espressif ESP32 Dev Module` (`esp32dev`), compatível com o alvo ESP32-WROOM-32 descrito no handoff.
- Validação de segredos: concluída no `secrets.yaml` privado do diretório ESPHome; nenhum valor é versionado.
- Header auxiliar: instalado em `/config/esphome/components/tecnohead_meter_reader_helpers.h`.
- Compilação: concluída com `INFO Successfully compiled program.`
- Imagem gerada pelo Builder: `firmware.factory.bin`, `firmware.ota.bin` e `firmware.elf`.
- Uso de memória informado pelo Builder: aproximadamente 29,2% de RAM e 54,7% de flash.
- Aviso não bloqueante: o Builder recomenda trocar a senha OTA por criptografia OTA; a configuração mantém a senha para compatibilidade inicial e a API continua criptografada.

## Limite da evidência

O diálogo do Builder também informa que o dispositivo ainda não foi instalado porque não havia ESP32/USB disponível no host. Portanto, esta evidência prova a compilação real e a geração da imagem, mas não prova boot, conexão API, entidades no Home Assistant, captura de bytes ou transmissão TTL em bancada.

Não houve conexão ao Nansen, à porta óptica ou a qualquer RS232.

## Captura de tela

A tela real da compilação foi apresentada no relatório da execução e deve ser anexada ao diretório `docs/screenshots/` quando o fluxo de exportação de evidências do ambiente estiver disponível. Não são usadas imagens simuladas para marcar homologação.
