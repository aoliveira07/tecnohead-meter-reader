# Capturas reais

Este diretório deve conter somente telas reais do Home Assistant/ESPHome Device Builder obtidas durante a implantação, sanitizadas para remover tokens, IPs privados, nomes pessoais, credenciais, números de série e dados do medidor.

Não há capturas de hardware anexadas enquanto o host não possui ESP32 conectado. O dashboard nativo já foi criado no HA real e o console Ingress já foi instalado; as telas reais de compilação, dashboard e console foram verificadas durante a execução, mas não são usadas para declarar captura UART ou homologação física.

Quando a bancada estiver disponível, publique pelo menos:

1. Builder com `tecnohead-meter-reader` e ESPHome 2026.9.1.
2. Dashboard real com API/RX e framing aplicado após o primeiro boot do ESP.
3. Console real com frame simulado em HEX/ASCII.
4. Tela de exportação e arquivos `.bin`/`.jsonl`/`.csv`.
5. Resultado separado: bancada aprovada; Nansen físico pendente.
