# J.A.R.V.I.S. — 2026-04-12 — Day Zero Context

**Tipo:** arquivo de consulta  
**Casa:** `J.A.R.V.I.S.`  
**Data-base:** 2026-04-12  
**Origem:** consolidação operacional do contexto desta virada de trajetória

---

## 1. Objetivo deste arquivo

Este documento existe para servir como **ponto de retomada rápida** do projeto após a reconstrução da KVM2 e a mudança de direção para um **Jarvis local-first, multicanal, hot-swappable, com Ollama local e crescimento por camadas**.

Ele **não é o log bruto** da conversa.  
Ele é a **síntese canônica para consulta**.

---

## 2. Tese consolidada

O Jarvis que queremos não é “um chat com memória”.

Ele é um:

## **control plane agêntico multicanal**

com:

- operação 24/7
- entrada simultânea
- execução atômica por agregado
- memória disciplinada
- watchdog contínuo
- sync com `state`, `omega` e `connectome`
- canais trocáveis
- modelo local como cérebro principal
- voz como módulo, não como dependência inicial

Princípio central:

> **concorrência na ingestão; serialização na mutação de estado**

Ou seja:

- vários canais podem mandar eventos ao mesmo tempo
- o mesmo agregado não pode sofrer mutações conflitantes ao mesmo tempo

---

## 3. Quem é quem

### Jarvis daqui

É o **maestro estratégico**, usado para:

- arquitetura
- auditoria
- refatoração de rota
- investigação profunda
- consolidação canônica
- promoção de estado

### Jarvis da KVM2

É o **operador residente local-first**, usado para:

- operação contínua
- execução de rotina
- resposta operacional
- vigilância básica
- uso de skills/tools locais
- inferência sem custo por token externo no núcleo principal

Contrato atual do Jarvis da KVM2:

- **papel:** operador residente
- **host:** Hostinger KVM2
- **transporte atual:** WhatsApp/UAZAPI
- **cérebro atual:** Ollama local
- **modelo atual:** `qwen3:4b`
- **função:** tocar a casa continuamente, não arbitrar sozinho toda decisão estratégica

---

## 4. Objetivos da fase que acabou de ser concluída

### Objetivo principal

Salvar o que importa, matar o legado da KVM2 sem perder dado e reerguer um core mínimo novo e limpo.

### Desdobramento

1. **Preservação**
   - exportar dados críticos
   - salvar restore-kit
   - registrar manifesto + checksums

2. **Abate seguro da KVM2**
   - parar serviços antigos
   - congelar estado final
   - limpar Docker/volumes/imagens legados

3. **Rebuild mínimo**
   - subir Ollama local
   - subir Jarvis novo
   - operar com provider local

4. **Canonização**
   - registrar em `infrastructure-state`
   - registrar em `state`
   - registrar na casa `J.A.R.V.I.S.`

---

## 5. Critérios de aceite da fase concluída

A fase é considerada aceita quando:

- o bruto crítico está salvo fora da KVM2
- o restore-kit existe
- o manifesto/checksums foram registrados
- o legado foi abatido
- o Docker da KVM2 foi limpo
- o Ollama foi instalado
- o modelo local foi carregado
- o Jarvis voltou no ar
- o provider passou a ser `ollama`
- `/healthz` = `ok`
- `/readyz` = `ready`
- `/statusz` = `ok`
- o estado foi promovido para os repositórios canônicos

**Leitura final:** esse bloco foi fechado.

---

## 6. Estado real validado em 2026-04-12

### KVM2

- **host:** `srv1503897`
- **disco livre após rebuild:** ~`72G`
- **Ollama:** `0.20.5`
- **modelo local:** `qwen3:4b`
- **container:** `jarvis-agent`
- **status:** `healthy`
- **porta publicada:** `3010 -> 3000`

### Provider ativo na KVM2

- `CORE_PROVIDER=ollama`
- `ROUTER_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`
- `OLLAMA_MODEL=qwen3:4b`

### Checks aprovados

- `/healthz` → `ok`
- `/readyz` → `ready`
- `/statusz` → `ok`

### Smoke test do modelo local

Foi executado teste direto no Ollama local com retorno bem-sucedido:

- resposta esperada: `OK_JARVIS_LOCAL`
- resultado: confirmado

---

## 7. Preservação e cofre

### Cofre atual

Local de preservação: `oracle-test`

- `raw` ≈ `1.5G`
- `restore-kit` ≈ `12K`

### Principais artefatos preservados

- `kvm2_ruptur_db_data_final`
- `kvm2_baileys_data_final`
- `jarvis_data_final`
- `n8n_n8n_data_consistent`
- `langfuse_langfuse_clickhouse_data_consistent`
- `langfuse_langfuse_postgres_data`
- `langfuse_langfuse_minio_data`
- `kvm2_traefik_letsencrypt`
- `kvm2_warmup_runtime_data`

### Garantia adicional

Na KVM2 também ficou backup local do `.env`:

- `.env.backup-20260412-201746`

---

## 8. Infra e capacidade comparada

### MacBook Pro local

- Intel Core i9-8950HK
- 6 cores / 12 threads
- 16 GB RAM
- melhor ambiente atual para:
  - POC
  - testes
  - voz local experimental
  - desenvolvimento

### Oracle Free Tier atuais

#### VPS 1

- shape `VM.Standard.E2.1.Micro`
- ~1 GB RAM
- útil para utilitário leve, relay, monitor auxiliar

#### VPS 2

- shape `VM.Standard.E2.1.Micro`
- ~1 GB RAM
- útil para relay, cron, webhook leve, cofre auxiliar

### Hostinger KVM2

- 2 vCPU
- 8 GB RAM
- 100 GB NVMe
- boa para:
  - fase inicial
  - texto-first
  - core mínimo
  - watchdog básico
  - WhatsApp/Slack iniciais

### Hostinger KVM8

- 8 vCPU
- 32 GB RAM
- 400 GB NVMe
- alvo recomendado para:
  - produção mais robusta
  - voz ao vivo modular
  - mais workers
  - mais canais
  - crescimento dos próximos 60 dias

---

## 9. Decisões estratégicas consolidadas

### 9.1. Modelo por fase

- **KVM2:** `qwen3:4b`
- **KVM4:** `qwen3:8b`
- **KVM8:** `qwen3:14b`
- **multimodal/visão opcional:** `gemma3:4b`

### 9.2. Estratégia de crescimento

Rampa preferida:

- Fase 0: MacBook/KVM2
- Fase 1: KVM2 dedicada
- Fase 2: pular preferencialmente para KVM8

### 9.3. Voz

Voz entra como **módulo**:

- fase inicial: assíncrona / push-to-talk
- fase posterior: voz ao vivo real

Stack preferida para amadurecimento:

- `LiveKit` como ponte/transporte
- STT/TTS gerenciados ou híbridos
- Jarvis Core soberano

---

## 10. Arquitetura-alvo em camadas

### Núcleo

- `jarvis-gateway`
- `jarvis-ledger`
- `jarvis-core`
- `jarvis-watchdog`
- `jarvis-state-sync`
- `jarvis-voice-bridge`
- `ollama`
- `postgres`
- `redis` opcional

### Regra operacional

Cada evento precisa carregar:

- `event_id`
- `session_id`
- `turn_id`
- `channel`
- `tenant_id`
- `aggregate_key`
- `idempotency_key`
- `correlation_id`
- `causation_id`

E o processamento só pode mutar estado com:

- lock por `aggregate_key`
- replay disponível
- idempotência garantida

---

## 11. Como chamar o Jarvis da KVM2 hoje

### Oficialmente

- via **WhatsApp/UAZAPI**

### Tecnicamente no Warp

#### Status

```bash
ssh hostinger-kvm2 'curl -s http://127.0.0.1:3010/statusz'
```

#### Health

```bash
ssh hostinger-kvm2 'curl -s http://127.0.0.1:3010/healthz'
```

#### Logs

```bash
ssh hostinger-kvm2 'docker logs -f jarvis-agent'
```

#### Smoke do modelo local

```bash
ssh hostinger-kvm2 'curl -s http://127.0.0.1:11434/api/generate -H "Content-Type: application/json" -d "{\"model\":\"qwen3:4b\",\"prompt\":\"Responda apenas OK\",\"stream\":false}"'
```

### Observação importante

Hoje ainda **não existe um chat nativo de terminal** com ele.

No Warp, por enquanto, a interação é:

- operação
- inspeção
- simulação técnica

Melhoria futura recomendada:

- `jarvis chat`
- ou endpoint `/chat`
- ou CLI de conversa direta

---

## 12. O que ele já faz e o que ainda não faz

### Já faz bem

- ficar 24/7
- operar rotina
- receber eventos
- responder checks
- executar tarefas bem definidas
- servir de operador residente

### Ainda não deve fazer sozinho

- arbitragem máxima
- investigação profunda ambígua
- decisão arquitetural arriscada
- refatoração estrutural sem supervisão

Resumo:

- **ele** = operador local permanente
- **Jarvis daqui** = maestro estratégico e executor pesado

---

## 13. Próximas camadas do plano

### Próximos passos imediatos

1. teste funcional real via WhatsApp
2. kit de operação via Warp
3. watchdog
4. ledger transacional
5. state sync reforçado
6. Slack

### Ordem sugerida

1. `watchdog`
2. `ledger`
3. `state sync`
4. expansão de canais

---

## 14. Critérios de aceite da próxima fase

Cada nova camada só entra se cumprir:

1. commit e push
2. configuração rastreável
3. smoke test
4. health check
5. sem regressão do core mínimo
6. registro canônico
7. gate completo se for crítica

---

## 14.1. Correção de rota: validação operacional != prontidão para formatar o Mac

Erro corrigido desta fase:

> **não devemos misturar validação de canal/operação remota com decisão de formatação da workstation local.**

### Eixo A — validação operacional do Jarvis

Pergunta:

> o Jarvis remoto está funcionando bem no contexto da atividade que ele precisa executar?

Exemplos:

- `healthz`, `readyz`, `statusz`
- smoke do Ollama
- envio/recebimento no WhatsApp
- logs e latência
- watchdog
- ledger
- state sync

### Eixo B — prontidão para formatar o Mac

Pergunta:

> se o Mac for apagado agora, a operação continua recuperável?

Critérios corretos:

- repositórios importantes commitados e no remote
- backups concluídos
- segredos e acessos preservados
- chaves SSH testadas
- restore-kit validado
- capacidade real de restaurar a operação em outra máquina
- inexistência de ativos críticos somente locais

### Regra nova para o Jarvis

- falha em um canal remoto **não bloqueia automaticamente** a formatação do Mac;
- ela apenas indica que **a camada operacional daquele canal** ainda não está madura;
- formatação do Mac depende de **backup, acesso, recuperação e continuidade operacional**, não de um canal isolado.

### Tradução simples

- WhatsApp = critério de operação do canal
- formatação do Mac = critério de recuperação da workstation

Esses temas se cruzam, mas **não são o mesmo aceite**.

---

## 15. Registros canônicos desta virada

### J.A.R.V.I.S.

- `24cbee8` — `feat: add ollama local provider support`
- `9147ab7` — `docs: register kvm2 rebootstrap state`

### infrastructure-state

- `6d20ddd` — `ops: freeze kvm2 and refresh final manifests`
- `384c68e` — `docs: register kvm2 rebootstrap with ollama`

### state

- `47d4c25d` — `docs(jarvis): register kvm2 ollama rebootstrap`

---

## 16. Observações que não podem se perder

- o coração do runtime principal já opera sem token pago externo para inferência, porque roda em Ollama local
- isso **não torna o modelo “proprietário”**, mas torna a operação **self-hosted / local-first**
- o legado da KVM2 **não deve voltar por restauração cega**
- toda retomada futura deve ser **seletiva e em camadas**
- as Oracle Free Tier servem melhor como apoio, relay, cofre e auxiliares leves
- a KVM8 continua sendo o alvo natural de maturidade do Jarvis Core

---

## 17. Pergunta-mãe para a próxima etapa

> **Qual é a primeira camada que realmente merece voltar em cima deste core limpo?**

Resposta sugerida neste momento:

1. watchdog
2. ledger
3. state sync
4. expansão de canal

---

## 18. Fechamento

Este arquivo representa o **day zero context da nova trajetória**:

- KVM2 preservada
- legado abatido
- core mínimo reerguido
- Ollama local validado
- Jarvis residente vivo
- canonização concluída

Daqui em diante, o trabalho deixa de ser “salvar e reconstruir” e passa a ser:

## **crescer sem reabrir o caos**
