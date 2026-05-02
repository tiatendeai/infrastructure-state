# Relatório de Débitos Técnicos — 2026-04-20

🧬 🧠 🦾 ⌬ ∞ | J.A.R.V.I.S.

## Resumo executivo

Os débitos técnicos mais relevantes de hoje estão concentrados em seis áreas:

0. consumo exagerado de tokens, re-leitura de contexto e configuração central de execução entre Mac e VPS;
1. runtime do Jarvis/ADK no GCP ainda instável;
2. Paperclip no GCP já está em produção; bootstrap invite ainda pendente;
3. governança de Cloudflare/`hitl.ruptur.cloud` ainda precisa ser formalizada;
4. broker de credenciais para múltiplas contas agora tem o Infisical como chaveiro canônico, mas ainda depende de provisionamento real no cofre e no host;
5. migração GitHub `tiatendeai` → `ruptur-cloud` ainda não foi concluída;
6. alinhamento estrutural entre `state` e `shipyard` ainda está incompleto;
7. catálogo de serviços, objetivos e nomenclaturas ainda misturam legado com presente operacional;
8. AIOX bridge está vivo, mas ainda falha na ponte até o Hermes/Ollama e no fechamento da borda HTTPS.

### Vocabulário canônico atual

- `shipyard` = Estaleiro / infraestrutura-state / execução operacional
- `state` = memória canônica, governança e mapas vivos
- `Ruptur Cloud Lab` / `GCP` = runtime e alvo operacional atual
- `Infisical` = cofre canônico de segredos
- `Terraform` = IaC declarativa principal
- `Ansible` = configuração e sustentação de hosts
- `Obsidian` + `Excalidraw` = mapas e navegação visual
- `Rusty RDK` = camada Rust de integração/SDK para evolução de runtime
- `KVM2`, `Hostinger`, `oracle-*` = legado histórico, não alvo operacional presente

---

## P0 — consumo de tokens, contexto e centralização de config

### 0. Paperclip/Codex está gastando token demais quando o contexto cresce
- Sintoma observado: o agente volta a redescobrir o repositório, lê mais arquivos do que precisa, reprocessa logs e contexto e fica caro em tempo e tokens.
- Sinais típicos:
  - prompts longos sem necessidade;
  - heartbeat frequente demais;
  - revisão de árvore inteira em vez de diffs/assinaturas;
  - arquivos não relevantes entrando no contexto;
  - repetição de leitura entre Mac local e VPS.

### 0.1 O que já existe e deve ser reaproveitado
- `RTK` como ativo do Shipyard para purificar/comprimir contexto.
- `Ansible` como controlador operacional para manter config única em Mac local e VPS.
- `State` como memória canônica do que já foi indexado e do que já foi resolvido.
- `Paperclip` como runtime do agente.
- `Langfuse`/observabilidade como trilha futura de custo, erro e execução.

### 0.2 O que falta para fechar
- budget de contexto por tarefa/agente;
- mapa estático do repositório e whitelist do que realmente entra no prompt;
- `RTK` com config centralizada e sincronizada entre Mac e VPS;
- estratégia única de preflight para compressão de contexto antes de chamar LLM;
- política explícita de verbose/concise para prompts e respostas;
- telemetria de consumo por agente, por tarefa e por host.

### 0.3 Demandas operacionais incluídas neste débito
- a IA precisa saber seu papel, local de atuação, stack, limites e nível de autonomia;
- a configuração precisa ser centralizada para não divergir entre MacBook e VPS;
- o orquestrador não deve assumir contexto fora do que foi declarado;
- a forma de operação deve ficar explícita no `State` e nos playbooks do `Shipyard`.

### 0.4 Blocos de resolução
1. **Preflight e compressão de contexto**: gerar snapshot mínimo antes de invocar o agente.
2. **Configuração centralizada**: Ansible sincroniza `RTK` e regras entre Mac e VPS.
3. **Budget e disciplina de prompt**: reduzir heartbeat, ruído e re-leitura desnecessária.
4. **Observabilidade de custo**: medir consumo, loops e regressões de contexto.
5. **Governança de perfil operacional**: declarar local de residência, atuação, modelo e autonomia.

### 0.5 Critério de aceite
- o agente deixa de varrer o repositório inteiro sem motivo;
- o contexto relevante entra, o ruído sai;
- a mesma política roda igual no Mac e na VPS;
- o consumo de tokens cai de forma perceptível;
- o estado dessa decisão fica registrado no `State`/debt.

---

## P0 — quebrando fluxo agora

### 1. Jarvis/ADK no GCP está instável
- O `jarvis-agent.service` estava em crash loop.
- A causa raiz observada foi `ModuleNotFoundError: No module named 'dotenv'`.
- Isso indica ambiente Python/venv inconsistente no host GCP.

### 2. Paperclip no GCP está em produção, com bootstrap invite ainda pendente
- O playbook e a role foram executados com sucesso.
- O serviço subiu e respondeu em `3100`.
- O que ainda sobra é a etapa final de bootstrap/entrada canônica e a visibilidade operacional no HITL.

### 3. Cloudflare / `hitl.ruptur.cloud` ainda precisa de curadoria operacional
- O DNS já está mapeado, mas falta deixar formal:
  - quem altera;
  - onde ficam os segredos;
  - como validar proxy, SSL e origin.
- O registro em si não basta: a governança operacional ainda está incompleta.
- Os segredos de edge passam a viver no Infisical; Git guarda contrato, não valor sensível.

### 4. Broker de credenciais para múltiplas contas ainda não está fechado
- Existe um banco de contas e o desenho do painel já prevê rotação.
- Mas, sem a credencial efetivamente provisionada no Infisical e sincronizada no host, o orquestrador não tem como inventar uma conta nova.
- Isso vira débito porque, na prática, a continuidade depende de:
  - slot real provisionado;
  - segredo carregado no ambiente correto;
  - runtime recarregado;
  - smoke test aprovado.

### 4.1 Drift de login do Codex no Paperclip / Agent Hub — atualizado em 2026-04-22
- Sintoma observado: o Agent Hub mostrava `Not logged in` e `Conta ativa não identificada`, enquanto o host do Paperclip tinha `auth.json` válido em `/var/lib/paperclip/.codex`.
- Causa raiz: a UI consultava o Codex fora do runtime real do Paperclip e misturava três estados diferentes: autenticação, quota e prontidão de serviço.
- Estado real apurado: Codex autenticado via ChatGPT no usuário `paperclip`; conta `tiatendeai@gmail.com`; plano `plus`; blocker operacional registrado como `quota_exceeded` / `exhausted`.
- Correção aplicada no host HITL: `/api/services` passou a consultar `codex login status` como `paperclip` com `CODEX_HOME=/var/lib/paperclip/.codex`; `/services` passou a exibir `authState`, `quotaState`, `serviceReady`, email, plano, último refresh e blockers.
- Correção adjacente no Paperclip: agentes `codex_local` receberam `--skip-git-repo-check` para evitar falhas quando o cwd não é repositório confiável.
- Débito restante: provisionar contas reservas no cofre/host e criar auditoria durável de login/logout/rotação sem registrar segredos. O patch já foi persistido no repositório fonte local do HITL e validado com build.
- Plano canônico: `docs/agent-hub-auto-rotation-plan.md`.

---

## P1 — governança e arquitetura incompletas

### 4. Migração GitHub `tiatendeai` → `ruptur-cloud` ainda não foi concluída
- O `state` ainda aponta para `tiatendeai/state`.
- Falta transferir os repositórios no GitHub e atualizar os remotes locais.
- Também há referências antigas em docs e configs.

### 5. Contrato `state` vs `shipyard` ainda está incompleto
- A arquitetura correta é:
  - `state` = estratégia, cognição, mapas, inventário e dados;
  - `shipyard` = execução tática e operacional.
- Mas o `state` ainda está muito narrativo.
- Faltam arquivos estruturados como:
  - `inventory.yaml`
  - `gcp_resources.yaml`
  - `services.yaml`
  - topologia consumível por automação.

### 6. Paths e nomes legados ainda existem no Ansible e nos catálogos
- Ainda há referências antigas em `adapters/provisioning/ansible/group_vars/all.yml`, como:
  - `/Users/diego/dev/GitHub/vps-oracle/infra`
  - `/Users/diego/dev/infrastructure-state/...`
- Esses paths precisam ser saneados para o novo desenho canônico:
  - `shipyard` como estaleiro
  - `Ruptur Cloud Lab / GCP` como runtime
  - `Infisical` como cofre
  - `Terraform` e `Ansible` como ferramentas-base
  - `Obsidian` + `Excalidraw` como mapa rápido

### 7. Inventário Ansible e catálogo de serviços precisam ser consolidados
- O `hosts.yml` já foi ajustado para o GCP real, mas ainda mistura:
  - GCP / Ruptur Cloud Lab;
  - Oracle legado;
  - workstation local.
- Falta uma estrutura mais limpa por ambiente e função.
- O catálogo de serviços deve separar claramente:
  - runtime atual;
  - tooling canônico;
  - legado preservado apenas para rastreabilidade.

---

## P1/P2 — legado técnico

### 8. SSH da `oracle-test` ainda está sem chave funcional
- Nenhuma das chaves testadas funcionou.
- Isso impede verificação confiável da máquina e mantém a Oracle-test como débito histórico.

### 9. `oracle-prod` segue como dívida técnica assumida
- Está vivo, mas legado.
- Precisa continuar sendo acompanhado, mesmo sem prioridade hoje.
- O risco de drift continua existindo.

---

## P2 — higiene operacional

### 10. A árvore está com ruído de ambiente
- O `git status` mostra muitas mudanças dentro de `.venv-ansible/`.
- Isso parece venv reconstruído ou alterado por ambiente, não código de produto.
- Débito: limpar, reconstruir e evitar versionar lixo de ambiente.

### 11. Documentação gigante e misturada
- Arquivos como `debitos-tecnicos.md` e `mapa-de-infra-e-projetos-e-debitos.md` acumulam brainstorm, memória e execução.
- Isso ajuda a preservar histórico, mas aumenta o custo de navegação e decisão.
- Débito: separar:
  - canonical;
  - backlog;
  - histórico bruto;
  - mapas vivos em Obsidian + Excalidraw.

---

## Prioridade sugerida

1. reduzir consumo de tokens e padronizar contexto/RTK/Ansible;
2. estabilizar o Jarvis/ADK no GCP;
3. fechar a curadoria do `state`/`shipyard`;
4. planejar a virada da migração GitHub;
5. formalizar Cloudflare e Paperclip sob governança;
6. tratar Oracle como débito monitorado.

---

## Backlog da sprint final

Quando os débitos técnicos, bugs e impedimentos acima estiverem fechados, a sprint final deve entrar com:

- sessão e login do Agent Hub com Redis como session store;
- cookie seguro, expiração e revogação real no logout;
- proteção contra sessão indevida e permanência de login sem autorização;
- observabilidade completa com logs, métricas e traces correlacionados;
- auditoria e telemetria do ciclo de vida da sessão;
- integração explícita com o HITL para refletir estado, origem e proveniência.

Essa frente fica registrada como backlog diferido, não como execução imediata.

**Regra de governança:** este item funciona como **impedimento formal para declarar o projeto como pronto**.  
Ele pode ser revisado, refinado ou reescrito ao longo do caminho, mas **não pode ser esquecido nem removido sem decisão explícita registrada no State**.

---

## Blocos de resolução

### Estado canônico da fila atual
- iniciar pela task de tokens de contexto e sessão P0
- em seguida fechar o debug do AIOX Shipyard Bridge
- depois encerrar os bloqueios de Cloudflare e DNS
- manter o Terraform agora dentro do Estaleiro como casa canônica
- registrar cada avanço no State e na fila local do shipyard
- refletir catálogo e objetivos com a nomenclatura nova

### Bloco 1 — Tokens de contexto e consumo P0
- objetivo: reduzir o consumo exorbitante de tokens e parar de pagar contexto desnecessário
- foco: RTK, Ansible, budget de contexto, mapa estático de repo e disciplina de prompt
- efeito: menos custo, menos loop, mais previsibilidade em Mac e VPS
- task associada: `INFRA-029-token-consumption-context-budget-rtk-ansible`

### Bloco 2 — Sessão e login P0
- objetivo: fechar o contrato de sessão e token opaco com revogação real
- foco: Redis como session store, cookie seguro, logout confiável, rotação e reauth
- efeito: impede que login inválido ou sessão velha continue viva
- task associada: `INFRA-028-tokens-p0-sessao-login-seguranca-observabilidade`

### Bloco 3 — Debug, falhas e erros
- objetivo: transformar falhas recorrentes em triagem com causa raiz
- foco: bugs de runtime, credenciais, drift e erros de integração
- efeito: reduz retrabalho e evita que a mesma falha retorne sem ser fechada
- task associada: `INFRA-029-debug-falhas-erros-triagem`

### Bloco 4 — Dívida técnica impeditiva
- objetivo: manter o backlog canônico de débitos até haver decisão explícita
- foco: governança, rastreabilidade e fechamento ordenado
- efeito: evita esquecimento e impede falso “pronto”

### Bloco 5 — Integrações externas bloqueadoras
- objetivo: separar ausência de credencial/CA de falha real
- foco: Linear auth, Supabase TLS/SSL e sincronização remota
- efeito: reduz erro falso, drift e bloqueio ambíguo no runtime
- tasks associadas: `INFRA-030-linear-credential-gap-and-runtime-sync` e `INFRA-031-supabase-tls-ssl-backend-sync`

### Bloco 6 — AIOX bridge, Hermes e borda HTTPS
- objetivo: estabilizar a casa própria do AIOX e a conexão com o motor Hermes/Ollama
- foco: `host.docker.internal`, `host-gateway`, endpoint OpenAI-compatible, `doctor`, TLS e edge
- efeito: transforma `aiox.ruptur.cloud` em bridge confiável, com causa-raiz ou correção fechada
- task associada: `INFRA-029-aiox-hermes-bridge-debug`

### Bloco 7 — Cloudflare DNS, auth e proxy
- objetivo: finalizar o estado desejado do `aiox.ruptur.cloud` com governança real no edge
- foco: permissão de escrita, `proxied=true`, validação de record e origem, segredo do conector
- efeito: elimina o estado parcial em que o record existe mas a borda ainda não está no contrato final
- task associada: `INFRA-021-jarvis-p0-ansible-terraform-iac-dns`
- desdobramento operacional: `INFRA-030-cloudflare-aiox-dns-proxy-auth-fix`

### Bloco 8 — Higiene do Estaleiro e legado vivo
- objetivo: reduzir ruído operacional, path legada e ambiguidade entre arquivos de execução e memória
- foco: normalizar referências antigas, limpar artefatos de ambiente e manter o State como fonte canônica
- efeito: diminui erro humano, diminui desvio de contexto e melhora a precisão dos próximos turnos
- desdobramento operacional: `INFRA-031-legacy-cleanup-kvm2-hostinger-oracle-refs`

### Ordem de execução sugerida
1. tokens de contexto e consumo P0
2. sessão e login P0
3. debug do AIOX bridge
4. Cloudflare DNS e auth
5. observabilidade e auditoria
6. dívidas técnicas estruturais
7. fechamento do pronto do projeto

### Critério de parada
Se houver qualquer uma destas condições, o projeto **não pode** ser marcado como pronto:
- sessão inválida ainda possível
- logout não revoga de verdade
- tokens sem controle ou sem auditoria
- falha bloqueadora aberta
- débito técnico formal ainda sem decisão registrada

---

## Nota final

Este relatório deve ser atualizado conforme os próximos capítulos do ecossistema Ruptur forem avançando.

---

## 12. Visão / plano / brainstorm ainda não viraram operação

### 12.1 Checklist consolidado por frente

#### SecOps / DevSecOps
- [ ] Wazuh
- [ ] Falco
- [ ] Trivy
- [ ] Keycloak
- [ ] OPA / Gatekeeper
- [ ] TruffleHog
- [ ] Snyk
- [ ] Zero Trust aplicado como padrão
- [ ] rotação de secrets automatizada
- [ ] gates de segurança em PR

#### Observabilidade / IA
- [ ] Langfuse
- [ ] Prometheus
- [ ] Grafana
- [ ] Uptime Kuma
- [ ] tracing de agentes e prompts
- [ ] evals e métricas de qualidade
- [ ] correlação entre erro, custo e execução

#### Segredos / identidade
- [ ] Infisical
- [ ] GCP Secret Manager como produção
- [ ] política de segredo por ambiente
- [ ] integração com playbooks Ansible
- [ ] inventário formal de credenciais e owners

#### Chaos / resiliência
- [ ] Chaos Engineering como prática
- [ ] LitmusChaos
- [ ] Chaos Mesh
- [ ] watchdog de execução
- [ ] caos controlado integrado ao backlog
- [ ] rotina de revisão de resiliência

#### DevOps / IaC / automação
- [ ] Terraform
- [ ] Terragrunt
- [ ] Ansible
- [ ] GitHub Actions
- [ ] GitOps
- [ ] policy-as-code
- [ ] inventário declarativo do runtime

#### A2A / Jarvis / orquestração
- [ ] LangGraph
- [ ] LangChain
- [ ] LangFlow
- [ ] HITL operacional
- [ ] Jarvis Core como orquestrador
- [ ] backlog automático
- [ ] watcher / guardião de execução

#### Cloud / edge / rede
- [ ] Cloudflare como borda governada
- [ ] Tailscale como acesso seguro
- [ ] Pub/Sub para eventos
- [ ] Cloud Run como execução futura
- [ ] Firebase / Firestore para persistência HITL
- [ ] DNS / origin / SSL sob custódia formal

---

### 12.2 Matriz de prioridade de implementação

Critérios do score:
- **Impacto**: quanto destrava operação real
- **Risco**: quanto reduz falha, vazamento ou drift
- **Dependência**: quanto desbloqueia outras frentes
- **Esforço**: quanto custa implementar agora  

Score de recomendação = avaliação prática de 0 a 100.

| Item | Frente | Prioridade | Score | Recomendação curta |
|---|---|---:|---:|---|
| Infisical | Segredos | P0 | 98 | Fechar primeiro; sem cofre formal, todo o resto fica frágil. |
| GCP Secret Manager | Segredos | P0 | 96 | Produção precisa de um padrão canônico de secrets. |
| Langfuse | Observabilidade | P0 | 92 | Sem isso, a camada de IA fica cega. |
| Wazuh | SecOps | P0 | 90 | Dá visibilidade e disciplina de segurança operacional. |
| Trivy | SecOps | P0 | 88 | Bloqueia imagem/contêiner ruim antes de subir. |
| Terraform | IaC | P0 | 88 | Base de provisionamento para o GCP-first. |
| Ansible | IaC/ops | P0 | 86 | Fecha a configuração e a sustentação dos hosts. |
| Cloudflare governado | Edge | P0 | 86 | DNS/SSL/origin precisam custódia formal. |
| Keycloak | SecOps | P1 | 82 | Centraliza identidade e SSO com menos risco. |
| OPA / Gatekeeper | SecOps | P1 | 81 | Policy-as-code para não virar operação manual. |
| TruffleHog | SecOps | P1 | 80 | Reduz vazamento de segredo no ciclo Git. |
| Prometheus | Observabilidade | P1 | 78 | Métrica base da infraestrutura e serviços. |
| Grafana | Observabilidade | P1 | 76 | Consolida visão operacional para decisão rápida. |
| GitHub Actions | DevOps | P1 | 75 | Automatiza validação e reduz drift humano. |
| Falco | SecOps | P1 | 74 | Protege runtime com detecção comportamental. |
| Uptime Kuma | Observabilidade | P1 | 72 | Saúde rápida e simples dos endpoints críticos. |
| GitOps | DevOps | P1 | 72 | Ajuda a estabilizar deploy e auditoria. |
| Chaos Engineering | Resiliência | P2 | 68 | Importante, mas só depois do básico confiável. |
| LitmusChaos | Resiliência | P2 | 66 | Ferramenta boa, mas depende de plataforma madura. |
| Chaos Mesh | Resiliência | P2 | 64 | Mesma lógica: entra depois da base. |
| Keycloak + OPA + Zero Trust | SecOps | P1 | 83 | Combo forte para governança de acesso. |
| LangGraph / LangChain / LangFlow | A2A | P2 | 62 | Valioso, mas só escala depois do core estável. |
| HITL operacional | A2A | P1 | 84 | Precisa existir para controlar o que os agentes fazem. |
| Pub/Sub | Cloud | P2 | 60 | Bom para eventos, mas não é o bloqueador principal. |
| Cloud Run | Cloud | P2 | 58 | Futuro útil, não o gargalo de hoje. |
| Firebase / Firestore | Cloud | P2 | 56 | Útil para HITL, mas vem depois do fechamento básico. |
| Tailscale | Rede | P1 | 79 | Acesso seguro e prático entre ambientes. |

---

### 12.3 Score de recomendação por item

#### SecOps / DevSecOps
- [x] **Wazuh** — score **90/100**
  - recomendação: implantar cedo para ter trilha de segurança e inventário operacional.
- [x] **Falco** — score **74/100**
  - recomendação: entrar depois de Wazuh e do runtime estabilizado.
- [x] **Trivy** — score **88/100**
  - recomendação: priorizar porque reduz risco em containers e artefatos.
- [x] **Keycloak** — score **82/100**
  - recomendação: relevante para centralizar identidade.
- [x] **OPA / Gatekeeper** — score **81/100**
  - recomendação: bom para policy-as-code e gates automáticos.
- [x] **TruffleHog** — score **80/100**
  - recomendação: forte para higiene de repositório e segredos.
- [x] **Snyk** — score **65/100**
  - recomendação: útil, mas não essencial se o stack estiver cobrindo bem com outras ferramentas.

#### Observabilidade / IA
- [x] **Langfuse** — score **92/100**
  - recomendação: prioridade alta para não operar IA no escuro.
- [x] **Prometheus** — score **78/100**
  - recomendação: métrica base da infraestrutura.
- [x] **Grafana** — score **76/100**
  - recomendação: painel central de decisão.
- [x] **Uptime Kuma** — score **72/100**
  - recomendação: rápido para health-check e alerta.

#### Segredos / identidade
- [x] **Infisical** — score **98/100**
  - recomendação: prioridade máxima; hoje é um dos maiores bloqueios.
- [x] **GCP Secret Manager** — score **96/100**
  - recomendação: produção precisa disso como padrão.

#### Chaos / resiliência
- [x] **Chaos Engineering** — score **68/100**
  - recomendação: começa depois que o core ficar confiável.
- [x] **LitmusChaos** — score **66/100**
  - recomendação: bom candidato quando houver base madura.
- [x] **Chaos Mesh** — score **64/100**
  - recomendação: mesma lógica; não é P0.

#### DevOps / IaC / automação
- [x] **Terraform** — score **88/100**
  - recomendação: essencial para o GCP-first.
- [x] **Terragrunt** — score **70/100**
  - recomendação: útil se a complexidade de módulos crescer.
- [x] **Ansible** — score **86/100**
  - recomendação: essencial para configuração e sustentação.
- [x] **GitHub Actions** — score **75/100**
  - recomendação: bom para padronizar validações.
- [x] **GitOps** — score **72/100**
  - recomendação: estabiliza o fluxo de mudanças.

#### A2A / Jarvis / orquestração
- [x] **LangGraph** — score **62/100**
  - recomendação: importante, mas depois de fechar a base.
- [x] **LangChain** — score **60/100**
  - recomendação: serve como camada de composição, não como base.
- [x] **LangFlow** — score **55/100**
  - recomendação: útil para prototipar fluxos, não para sustentar a fundação.
- [x] **HITL operacional** — score **84/100**
  - recomendação: precisa estar ativo para supervisão humana real.

#### Cloud / edge / rede
- [x] **Cloudflare governado** — score **86/100**
  - recomendação: precisa de custódia formal e rotina de validação.
- [x] **Tailscale** — score **79/100**
  - recomendação: acesso seguro entre os ambientes.
- [x] **Pub/Sub** — score **60/100**
  - recomendação: importante em escala, mas não bloqueia o core.
- [x] **Cloud Run** — score **58/100**
  - recomendação: bom para o futuro, não para destravar hoje.
- [x] **Firebase / Firestore** — score **56/100**
  - recomendação: entra se o HITL precisar de persistência já no fluxo.

---

### 12.4 Ordem prática de implementação

Se eu fosse ordenar a virada por impacto real:

1. **Infisical**
2. **GCP Secret Manager**
3. **Langfuse**
4. **Wazuh**
5. **Trivy**
6. **Terraform**
7. **Ansible**
8. **Cloudflare governado**
9. **Keycloak**
10. **OPA / Gatekeeper**
11. **TruffleHog**
12. **HITL operacional**
13. **Prometheus + Grafana**
14. **GitHub Actions**
15. **Tailscale**
16. **Falco**
17. **Chaos Engineering / LitmusChaos / Chaos Mesh**
18. **LangGraph / LangChain / LangFlow**
19. **Pub/Sub**
20. **Cloud Run / Firestore**

---

### 12.5 Leitura final

O que está hoje em modo “visão / plano / brainstorm” não é lixo — é **estoque de ambição**.  
Mas o débito técnico começa quando isso não é convertido em:

- instalação real;
- ownership;
- inventário;
- playbook;
- rotina;
- validação;
- observabilidade;
- segurança;
- e ciclo de operação.

Se você quiser, o próximo passo eu faço já em cima disso:

1. transformar essa seção em **backlog executável**;
2. separar por **P0/P1/P2** com responsável;
3. ou gerar uma **tabela única de “visão → operação”** para cada ferramenta.

---

## 13. Backlog executável

### 13.1 Formato do backlog

Critérios usados:
- **Backlog item** = algo que pode virar task, playbook, issue ou entrega operacional
- **Responsável** = função/área que deve puxar a execução
- **Dependências** = o que precisa existir antes
- **Saída esperada** = evidência concreta de que saiu do brainstorm

### 13.2 Backlog priorizado

| # | Item | Status atual | Próxima ação executável | Responsável | Dependências | Saída esperada |
|---|---|---|---|---|---|---|
| 1 | Infisical | visão/plano | criar instalação canônica e fluxo de secrets | Shipyard + SecOps | inventário de segredos, acesso ao cofre, política por ambiente | cofre funcionando e playbooks lendo dele |
| 2 | GCP Secret Manager | em uso parcial / alinhamento | formalizar como fonte de produção | Shipyard + Infra | projeto GCP correto, service account, policies | secrets de produção sob padrão único |
| 3 | Langfuse | plano / legado a alinhar | subir ou migrar para target canônico | Shipyard + Observabilidade | secrets, storage, domínio, runtime | tracing de agentes e prompts ativo |
| 4 | Wazuh | visão / implantação futura | instalar agente/servidor e conectar logs | SecOps + Shipyard | infra base, storage de logs, regras de alertas | SIEM operacional com alertas |
| 5 | Trivy | visão / implantação futura | colocar scan em PR e artefatos | SecOps + DevOps | CI, repositórios, política de bloqueio | scan automático antes do merge |
| 6 | Terraform | já conhecido, falta fechamento | consolidar módulos e state canônico | Infra | backend de state, inventário GCP, variáveis | provisionamento declarativo repetível |
| 7 | Ansible | já existe, precisa curadoria | limpar paths legados e padronizar inventário | Shipyard + Infra | hosts limpos, secrets, baseline OS | playbooks estáveis por ambiente |
| 8 | Cloudflare governado | operação parcial | documentar owner, segredo e rotina de validação | Shipyard + Edge | acesso ao painel, DNS/origin/SSL | custody model formal e auditável |
| 9 | Keycloak | visão / roadmap | definir se entra agora ou depois do cofre | SecOps + Produto | estratégia de identidade, SSO, front de login | identidade central unificada |
| 10 | OPA / Gatekeeper | visão / roadmap | escrever policies mínimas e gates | SecOps + DevOps | CI, Terraform, regra de aprovação | policy-as-code bloqueando drift |
| 11 | TruffleHog | visão / roadmap | ativar scanning de segredo em repos | SecOps + DevOps | acesso aos repos, CI, baseline | detecção automática de vazamento |
| 12 | Prometheus | visão / roadmap | instalar base métrica | Observabilidade + Infra | host/base runtime, scrape config | métricas operacionais disponíveis |
| 13 | Grafana | visão / roadmap | criar painel único de operação | Observabilidade | Prometheus, datasources | dashboard central de saúde |
| 14 | Uptime Kuma | visão / roadmap | instalar health checks externos | Observabilidade + Infra | DNS, endpoints, alertas | saúde básica dos serviços visível |
| 15 | HITL operacional | parcial | fechar fluxo de aprovações e supervisão | Jarvis + Produto | painel, dados, persistência, regras | humanos aprovando o que importa |
| 16 | Tailscale | parcial | padronizar acesso entre ambientes | Infra + Shipyard | chaves, inventário, ACLs | rede privada pronta e organizada |
| 17 | Falco | visão / roadmap | decidir implementação em runtime alvo | SecOps + Infra | containers, host, política de eventos | runtime security rodando |
| 18 | Chaos Engineering | visão / brainstorm | escolher uma prática mínima e rodar piloto | Infra + Jarvis | stack estável, playbook de teste | experimento de caos controlado |
| 19 | LitmusChaos | visão / brainstorm | validar se é o framework escolhido | Infra + SRE | base Kubernetes / runtime compatível | plano de caos com ferramenta real |
| 20 | Chaos Mesh | visão / brainstorm | avaliar apenas se fizer sentido no target | Infra + SRE | K8s compatível, maturidade operacional | opção comparada e decidida |
| 21 | LangGraph / LangChain / LangFlow | visão / roadmap | decidir qual camada entra primeiro | Jarvis + Produto | objetivo de A2A, fluxo, storage | stack de orquestração escolhida |
| 22 | Pub/Sub | roadmap cloud | desenhar eventos A2A e HITL | Infra + Jarvis | projeto GCP, autenticação, consumers | trilha de eventos formal |
| 23 | Cloud Run | roadmap cloud | avaliar como runtime futuro | Infra + Produto | container pronto, deploy pipeline | opção de execução pronta |
| 24 | Firebase / Firestore | roadmap cloud | decidir persistência do HITL | Produto + Infra | modelagem de dados, auth, custo | persistência operacional definida |
| 25 | Obsidian + Excalidraw + 3D do vault em subdomínios | pendente | provisionar `obsidian.ruptur.cloud` e `excalidraw.ruptur.cloud` com acesso controlado, validar o mapa 3D do Obsidian e publicar os ativos do Shipyard | Shipyard + Edge + Docs + Infra | DNS Cloudflare, origin, autenticação, storage/backup, política de acesso, vault limpo, cache do Obsidian, plugins, logs do app | subdomínios ativos, documentados e integrados ao fluxo operacional, com 3D do Obsidian funcionando ou causa-raiz fechada |
| 26 | AIOX bridge, Hermes e borda HTTPS | P0/P1 | estabilizar `aiox.ruptur.cloud`, corrigir a ponte até Hermes/Ollama e fechar a borda HTTPS | Shipyard + Infra + Edge | Docker host-gateway, endpoint do Hermes, nginx/Cloudflare, TLS, health check, `aiox-core doctor` | bridge AIOX saudável, teste Hermes respondendo e HTTPS acessível sem erro |

### 13.3 Entendimento canônico desta demanda

Quando este tópico for citado futuramente, o entendimento deve ser:
- **um único pacote de trabalho**
- **Obsidian + Excalidraw + 3D do vault + subdomínios**
- **validação técnica e restauração do render 3D**
- **publicação controlada em `obsidian.ruptur.cloud` e `excalidraw.ruptur.cloud`**
- **sem separar a solicitação em tarefas soltas, salvo se eu pedir explicitamente**

### 13.4 Regra semântica para backlog e débito técnico

Quando eu falar em:
- **backlog**
- **débito técnico**
- **dívida técnica**
- **pendência**
- **atividade**

isso deve ser entendido como **task executável**, ou seja:
- item acionável;
- com dono/responsável;
- com próxima ação clara;
- com saída esperada;
- com possibilidade de virar implementação, checklist ou issue.

### 13.5 Regra de pré-criação e validação

Quando eu disser, ou quando você disser em tom de intenção futura:
- "vamos fazer isso depois"
- "vamos fazer"
- "precisamos fazer"
- "quando formos fazer"
- "depois a gente faz"
- "isso precisa entrar"

o fluxo correto é:
1. eu **proponho a task** em linguagem clara;
2. eu digo algo como: **"Planejei a task X. Você confirma a adição?"**;
3. só depois da sua confirmação eu trato como **criação/adicionamento oficial**;
4. se não houver confirmação, fica apenas como **intenção / proposta**.

Regra prática:
- **intenção verbal** não vira criação automática;
- **criação** exige **validação explícita** do Diego;
- **backlog/débito técnico** viram task, mas só entram oficialmente após confirmação.

---

## 14. Responsáveis e dependências por frente

### 14.1 SecOps
Responsável principal:
- **SecOps / Shipyard**

Depende de:
- inventário limpo
- secrets formalizados
- CI funcionando
- acesso controlado aos ambientes

Entrega esperada:
- Wazuh, Falco, Trivy, TruffleHog, OPA/Gatekeeper, Keycloak e Zero Trust saindo do papel

### 14.2 Observabilidade
Responsável principal:
- **Observabilidade / Shipyard**

Depende de:
- runtime estável
- DNS/domínios corretos
- storage para logs e traces
- secrets fechados

Entrega esperada:
- Langfuse, Prometheus, Grafana e Uptime Kuma operacionais

### 14.3 Segredos / identidade
Responsável principal:
- **Shipyard + Infra + SecOps**

Depende de:
- mapeamento de credenciais
- owner por ambiente
- estratégia de produção versus dev

Entrega esperada:
- Infisical e GCP Secret Manager com papéis claros

### 14.4 Infra / IaC / automação
Responsável principal:
- **Infra / Shipyard**

Depende de:
- state estruturado
- hosts corretos
- repositórios migrados
- paths legados removidos

Entrega esperada:
- Terraform + Ansible + GitOps funcionando como dupla de execução

### 14.5 A2A / Jarvis / HITL
Responsável principal:
- **Jarvis / Produto / Shipyard**

Depende de:
- observabilidade
- segredos
- persistência
- fluxo humano de aceite

Entrega esperada:
- o sistema de agentes deixa de ser só visão e vira operação supervisionada

### 14.6 Cloud / edge / rede
Responsável principal:
- **Infra + Shipyard + Edge**

Depende de:
- Cloudflare formalizado
- GCP organizado
- DNS/origin/SSL consistente

Entrega esperada:
- topologia cloud coerente e auditável

---

## 15. Plano de execução em 30/60/90 dias

### 15.1 Próximos 30 dias — fechar a base
Objetivo: sair do “plano bonito” e entrar na infraestrutura confiável.

Prioridades:
- [ ] Infisical
- [ ] GCP Secret Manager como produção
- [ ] provisionamento real do broker de credenciais no Infisical + host
- [ ] Langfuse
- [ ] Wazuh
- [ ] Trivy
- [ ] Terraform canônico
- [ ] Ansible limpo
- [ ] Cloudflare governado

Resultado esperado ao fim de 30 dias:
- segredos não ficam mais soltos
- observabilidade da IA existe
- segurança mínima tem telemetria
- execução do Shipyard fica mais confiável

### 15.2 60 dias — consolidar governança e operação
Objetivo: sair da instalação básica e entrar em operação repetível.

Prioridades:
- [ ] Keycloak
- [ ] OPA / Gatekeeper
- [ ] TruffleHog
- [ ] Prometheus
- [ ] Grafana
- [ ] Uptime Kuma
- [ ] HITL operacional
- [ ] Tailscale padronizado
- [ ] Playbooks de operação escritos

Resultado esperado ao fim de 60 dias:
- identidade e acesso mais maduros
- painel operacional único
- rotina de validação contínua
- menos dependência de memória humana

### 15.3 90 dias — avançar para resiliência e orquestração
Objetivo: sair da operação reativa e entrar em sistema adaptativo.

Prioridades:
- [ ] Chaos Engineering
- [ ] LitmusChaos ou escolha equivalente
- [ ] Falco
- [ ] LangGraph / LangChain / LangFlow definidos
- [ ] Pub/Sub para eventos A2A
- [ ] Cloud Run avaliado/ativado
- [ ] Firestore/Firebase decidido para HITL
- [ ] políticas de segurança e drift automatizadas

Resultado esperado ao fim de 90 dias:
- segurança, observabilidade e execução mais próximas de um sistema vivo
- agentes e humanos operando com mais previsibilidade
- caos controlado e revisão contínua entrando no ciclo

---

## 16. Tabela curta: visão → operação

| Frente | Hoje | Meta |
|---|---|---|
| Segredos | visões e discussões | cofre canônico e uso em playbooks |
| Observabilidade | intenção e backlog | tracing e métricas rodando |
| SecOps | roadmap | scans, runtime security e políticas ativas |
| IaC/DevOps | base existe | execução limpa e repetível |
| A2A/HITL | arquitetura em discussão | supervisão humana com fluxo real |
| Cloud/edge | fragmentado | governança formal e topologia estável |
| Chaos | conceitual | piloto controlado e depois rotina |
