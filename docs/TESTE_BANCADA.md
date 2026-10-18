# Teste de bancada

## Esquema permitido

```text
TX UART TTL 3,3 V do simulador ───── GPIO16 / RX ESP32
GND do simulador ──────────────────── GND da bancada
GPIO17 / TX ESP32 ─────────────────── sem fio / sem uso
```

O simulador não deve ser conectado a uma saída RS232. Confirme com o instrumento ou com a documentação do adaptador que o TX é TTL 3,3 V.

## Procedimento

1. Ligue o ESP32 e confirme API conectada.
2. Deixe **Captura RX** desligada e pressione **Limpar visualização**.
3. Selecione 9600 / Nenhuma / 8 / 1 e ligue a captura.
4. Execute o simulador com o mesmo framing.
5. Pressione **Criar marcação** entre duas sequências.
6. Confirme no dashboard HEX, ASCII, contador, taxa e tempo desde atividade.
7. Exporte `.bin`, `.jsonl` e `.csv` pelo console. Compare o `.bin` com `expected_hex` do simulador.
8. Pause a captura, envie uma nova sequência e confirme que ela não entra como frame válido e que o painel informa descarte/pausa.
9. Altere baud, paridade, bits e stop bits pelo HA sem reflashing. Confirme o texto de configuração aplicada.
10. Desconecte/reconecte Wi-Fi ou reinicie o ESP e verifique que as escolhas persistem e a captura inicia desligada.

## Matriz mínima

| Caso | Configuração | Resultado esperado | Evidência |
|---|---|---|---|
| B01 | 9600 8N1 | bytes `55 AA 00 7E...` na mesma ordem | `.bin` + tela |
| B02 | 1200 7E1 | controles aplicados sem reflash | texto aplicado |
| B03 | 2400 8O1 | controles aplicados sem reflash | texto aplicado |
| B04 | 4800 8N2 | controles aplicados sem reflash | texto aplicado |
| B05 | captura pausada | registros marcados como não confirmados | contador/console |
| B06 | marcação | evento correlacionável | `.jsonl` |
| B07 | lacuna MQTT | sessão `incomplete=true` | manifest |
| B08 | reinício | select restaurado, captura OFF | dashboard |

Até existir uma placa conectada e uma origem TTL na bancada, os casos B01–B08 permanecem planejados, não passados.
