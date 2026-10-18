# Diagnóstico passivo de protocolos

O decodificador tem três camadas:

1. **RAW/HEX**: todos os bytes recebidos, sem conversão e com `0x00` preservado.
2. **Framing**: indícios de CRLF, STX/ETX e `0x7E` são marcados como hipóteses de baixa confiança.
3. **Parsers futuros**: a arquitetura deixa espaço para DLMS/COSEM/ABNT, mas nenhuma consulta, escrita, autenticação ou varredura automática é feita.

Um byte `0x7E` pode ser compatível com HDLC usado em alguns perfis DLMS, mas isso não identifica o protocolo do Nansen. Os códigos de visor 03 e 103 não são tratados como OBIS, endereço ABNT ou registro serial.

A ausência de tráfego também não é evidência contra um protocolo: a interface pode aguardar requisição ou autenticação. A fase 1 é deliberadamente passiva.
