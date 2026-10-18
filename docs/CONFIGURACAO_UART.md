# Configuração UART

## Entidades

| Entidade lógica | Função |
|---|---|
| Velocidade UART | 300 a 115200 baud |
| Paridade | Nenhuma, Par, Ímpar |
| Bits de dados | 7 ou 8 |
| Bits de parada | 1 ou 2 |
| Decodificador | RAW/HEX, ASCII legível, detecção passiva DLMS, detecção passiva ABNT |
| Captura RX | Liga/desliga a sessão; default desligado |
| Limpar visualização | Limpa prévias, não limpa contadores nem arquivos |
| Zerar contadores | Zera contadores de laboratório |
| Criar marcação | Publica um evento de correlação na sessão |

Ao mudar um select serial, o firmware pausa a captura, espera o agrupamento pendente expirar, drena o buffer RX disponível, aplica baud/paridade/data bits/stop bits e chama `load_settings()`. A entidade **Configuração aplicada** é atualizada com o framing efetivo.

O teste de cada parâmetro ainda deve ser feito com um transmissor de bancada configurado com o mesmo framing. O valor 9600 8N1 é apenas o ponto inicial e não constitui evidência sobre o Nansen.

## Estado e perda

- **Sem tráfego**: nenhuma nova sequência RX observada durante a janela atual.
- **MQTT desconectado**: o ESP pode mostrar a prévia local, mas a captura íntegra não é confirmada pelo console.
- **Registros descartados**: bytes observados enquanto a captura estava pausada ou publicação MQTT que não foi confirmada.
- **Sessão incompleta**: lacuna de sequência, limite de armazenamento ou desconexão antes do evento final.
