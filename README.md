# TecnoHead Meter Reader

Ferramenta de laboratório para captura passiva RX no ESP32, controles seriais em tempo real pelo Home Assistant e exportação íntegra de sessões para `.bin`, `.jsonl` e `.csv`.

O projeto é independente do TecnoHead Solar. Ele não consulta, autentica, configura ou altera o medidor Nansen. A fase física do Nansen continua pendente de autorização da concessionária e validação elétrica por profissional responsável.

## Estado da entrega

| Área | Estado | Evidência / limite |
|---|---|---|
| Firmware | Compilado com sucesso no ESPHome Device Builder real | ESPHome 2026.9.1 / Device Builder 1.14.9; imagem ESP32 gerada em 17/10/2026 |
| GPIO16 | RX da UART2 | UART configurada sem `tx_pin` |
| GPIO17 | Reservado | Não aparece no YAML e não há ação `uart.write` |
| Controles serial | Implementados | Selects com restauração e aplicação via `load_settings()` |
| Captura íntegra | Implementada | MQTT local → App HAOS; `.bin` preserva `0x00` e bytes não imprimíveis |
| Dashboard nativo | Arquivo fornecido | Importação no HA real depende da criação das entidades após o primeiro boot |
| Console HAOS | App fornecido | Ingress, buffer recente e exportação por sessão |
| Teste de bancada | Simulador fornecido | Nenhuma porta USB apareceu neste host durante a implementação; transmissão física não foi executada |
| ESP32 físico | Pendente | Não havia COM/USB serial visível no host |
| Nansen físico | Bloqueado por segurança | Nenhuma ligação foi feita; TX permanece desativado |

## Arquitetura

```text
UART TTL 3,3 V seguro de bancada
          │ RX
          ▼
GPIO16 / UART2 ── ESP32 ── ESPHome Native API ── Home Assistant
                         └─ MQTT local ── TecnoHead Meter Reader Console
                                              ├─ capture.bin
                                              ├─ capture.jsonl
                                              └─ capture.csv
```

A captura é agrupada pelo debugger do ESPHome por até 256 bytes ou 100 ms de silêncio. O agrupamento não é uma afirmação de framing do protocolo: a ordem original é preservada no `.bin` pela sequência dos registros.

## Instalação no ESPHome Device Builder

1. Abra **ESPHome Builder** no Home Assistant real.
2. Crie ou importe `firmware/tecnohead-meter-reader.yaml` com o nome `tecnohead-meter-reader`.
3. No `secrets.yaml` privado do Builder, mantenha as chaves existentes de Wi-Fi/API/OTA e adicione as chaves MQTT conforme [`firmware/secrets.example.yaml`](firmware/secrets.example.yaml). Não copie valores reais para o GitHub.
4. Confirme a placa física. O arquivo parte de `esp32dev` / ESP32-WROOM-32; se a placa for C3/S3 ou outra variante, ajuste o `board` antes de gravar.
5. Compile no Builder. Só após a compilação sem erros faça a instalação USB/OTA no ESP32 autorizado.
6. Adicione o nó à integração ESPHome pelo hostname ou IP. O `api` usa criptografia; OTA exige senha.

O primeiro boot mantém `Captura RX` desligada. A configuração inicial é `9600 8N1`. Baud, paridade, bits de dados e bits de parada são ajustados pela UI e aplicados em tempo real; o firmware pausa a captura, drena o buffer parcial, chama `load_settings()` e registra a configuração efetiva.

## Home Assistant

- Importe [`dashboard/tecnohead-meter-reader.yaml`](dashboard/tecnohead-meter-reader.yaml) em um dashboard novo pelo editor de configuração bruto.
- Instale o App `TecnoHead Meter Reader — Console` adicionando este repositório à App Store do Supervisor, depois abra o painel Ingress **TecnoHead Meter Reader**.
- O App recebe somente o tópico local `tecnohead/meter-reader/+/capture` via serviço MQTT do Supervisor.
- O armazenamento fica no volume persistente do App em `/data/sessions`. Há limite de 64 MiB por sessão e 256 MiB no total; lacunas de sequência e estouro são marcados como `incomplete`.
- O Recorder não recebe o fluxo bruto. O dashboard mostra apenas prévias curtas; o console é a fonte de exportação íntegra.

## Regra de execução do projeto

O procedimento autorizado para este projeto está em
[`docs/EXECUCAO_AUTORIZADA.md`](docs/EXECUCAO_AUTORIZADA.md): executar a entrega até
instalar, verificar e deixar os componentes funcionando quando o ambiente permitir,
sem confundir bancada segura com leitura física do Nansen.

## Teste seguro de bancada

Use outro microcontrolador ou adaptador UART TTL com nível lógico **3,3 V**, GND comum da bancada e TX do simulador ligado somente ao GPIO16. Não use adaptador RS232, não use os bornes do Nansen e não conecte GPIO17.

O simulador é dry-run por padrão:

```text
python tests/simulador-uart/simulador.py --baud 9600 --parity N --data-bits 8 --stop-bits 1
```

Para transmitir, a confirmação explícita exige a interface TTL:

```text
python tests/simulador-uart/simulador.py --send --interface ttl-3v3 --port COM7 --baud 9600 --parity N --data-bits 8 --stop-bits 1
```

Compare o `expected_hex` do simulador com o `.bin` exportado. Repita em 7N1, 8E1, 8O1, 8N2 e nos demais baud rates, sempre mudando o select no dashboard antes de enviar. Registre o resultado no checklist de [`docs/TESTE_BANCADA.md`](docs/TESTE_BANCADA.md).

## Segurança e escopo físico

Não ligue GPIO16, GPIO17, 3V3 ou GND diretamente ao RS232 do medidor energizado. RS232 usa polaridades e níveis incompatíveis com UART 0–3,3 V. A arquitetura futura, se autorizada, é:

```text
RS232 do Nansen (uso autorizado)
        │
conversor RS232 ↔ UART 3,3 V com isolamento galvânico validado
        │ RX somente
      GPIO16
```

MAX3232 comum converte níveis, mas não fornece isolamento galvânico. A porta óptica lacrada não deve ser tocada. Nenhuma captura publicada neste projeto é leitura real do Nansen.

## Desenvolvimento e validação

```text
python -m pytest
python -m compileall capture-console/app tests
```

O firmware foi compilado pelo ESPHome Device Builder instalado no HAOS, porque o host de desenvolvimento não possui a CLI `esphome`. A ausência de uma placa conectada impede declarar instalação física, OTA, bytes simulados recebidos no ESP e captura de telas do dispositivo como concluídos. A evidência do Builder está registrada em [`docs/VALIDACAO_BUILDER_REAL.md`](docs/VALIDACAO_BUILDER_REAL.md).

## Versões

- Firmware/Builder alvo: ESPHome 2026.9.1 / Device Builder 1.14.9.
- Projeto inicial: `0.1.0`.
- Release do firmware: `v0.1.0`; a imagem do App é publicada pelo workflow quando o GitHub concluir o build da tag.

## Documentação

- [Instalação no HAOS](docs/INSTALACAO_HAOS.md)
- [Configuração UART](docs/CONFIGURACAO_UART.md)
- [Teste de bancada](docs/TESTE_BANCADA.md)
- [Segurança e limites](docs/SEGURANCA_E_LIMITES.md)
- [Diagnóstico passivo de protocolos](docs/PROTOCOLOS.md)
- [Homologação](docs/HOMOLOGACAO.md)
- [Capturas reais](docs/screenshots/README.md)
- [Regra operacional autorizada](docs/EXECUCAO_AUTORIZADA.md)
