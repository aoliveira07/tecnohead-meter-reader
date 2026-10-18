# Regra operacional do projeto

Esta regra faz parte do projeto TecnoHead Meter Reader e registra a autorização do
responsável para que a implementação avance até um resultado verificável.

## Procedimento padrão

Para este projeto, o agente deve:

1. implementar o código e a documentação;
2. instalar e configurar os componentes no Home Assistant/ESPHome quando o ambiente
   estiver disponível;
3. executar os testes seguros possíveis;
4. corrigir os problemas encontrados;
5. publicar a versão e atualizar a instalação;
6. deixar os componentes instalados e em funcionamento quando isso for possível; e
7. chamar o responsável somente quando o resultado estiver pronto ou existir um
   impedimento real que não possa ser resolvido com segurança.

Não é necessário interromper o fluxo para pedir confirmação a cada etapa rotineira
deste escopo. A instalação, a configuração, a atualização e a verificação devem ser
tratadas como uma única entrega contínua.

## Limites que permanecem obrigatórios

Esta autorização não permite ultrapassar os limites elétricos e regulatórios do
projeto:

- GPIO16 é RX de bancada UART TTL 3,3 V; GPIO17 permanece reservado e sem transmissão.
- Nunca ligar GPIO16, GPIO17, 3V3 ou GND diretamente ao RS232 do Nansen.
- Não romper lacres, acessar a porta óptica, enviar comandos, tentar autenticação ou
  executar consultas ativas ao medidor.
- Uma conexão futura ao Nansen exige autorização específica, interface RS232↔UART com
  isolação galvânica validada e avaliação técnica responsável.
- Testes de simulador UART, ausência de tráfego e captura do laboratório não podem ser
  apresentados como leitura real, homologação ou validação da concessionária.
- Segredos ficam somente no Home Assistant e nunca são publicados no GitHub.

## Critério de pronto

Uma entrega só deve ser marcada como pronta quando o estado real estiver documentado:

- firmware compilado e, havendo hardware, instalado;
- dashboard e console acessíveis no Home Assistant;
- captura/exportação verificadas ou a limitação explicitamente registrada;
- testes de bancada separados da etapa física do Nansen; e
- repositório, release, evidências e impedimentos atualizados.
