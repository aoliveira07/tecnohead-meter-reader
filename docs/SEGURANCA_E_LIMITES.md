# Segurança e limites

- UART do ESP32 é 0–3,3 V. RS232 real usa níveis e polaridades diferentes.
- Nunca conectar GPIO16, GPIO17, 3V3 ou GND diretamente aos bornes RS232 do Nansen energizado.
- GPIO17 fica reservado e desativado nesta fase. Não há menu de transmissão, `uart.write` ou consulta automática.
- Não romper lacres, não usar a porta óptica lacrada, não alterar configuração/calibração e não tentar credenciais DLMS.
- MAX3232 comum converte níveis, mas não isola. Para uma etapa autorizada, exigir interface RS232↔UART com isolamento galvânico e avaliação profissional.
- Um estado “API conectada” confirma apenas a sessão ESPHome/HA. Não confirma comunicação com o medidor.
- Um estado “há tráfego RX” confirma bytes TTL observados no GPIO16. Não confirma protocolo, origem ou autorização.
- “Sem tráfego espontâneo observado” é o único resultado permitido quando não há bytes; não declarar porta inoperante.
- O console local limita a retenção para evitar lotar Recorder, flash do ESP ou volume indefinidamente.
