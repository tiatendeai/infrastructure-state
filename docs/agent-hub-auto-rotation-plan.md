# Agent Hub — Codex service-ready, login/logout e rotação no Paperclip

🧬 🧠 🦾 ⌬ ∞ | J.A.R.V.I.S.

Data de atualização: 2026-04-22

## Diagnóstico P0

O painel mostrava `Not logged in`, mas o runtime real do Paperclip estava autenticado no Codex.

Achado técnico:

- o Paperclip roda como usuário `paperclip`;
- o `CODEX_HOME` real do Paperclip é `/var/lib/paperclip/.codex`;
- o `auth.json` do Paperclip existe e indica autenticação ChatGPT ativa;
- a conta identificada é `tiatendeai@gmail.com`, plano `plus`;
- o estado operacional local marcava `quota_exceeded` / `exhausted`;
- o Agent Hub antigo consultava o Codex como usuário do painel (`diego`) e não como usuário `paperclip`;
- portanto a UI confundia **quota esgotada / probe errada** com **logout**.

Conclusão: o problema principal não era ausência de login. Era drift semântico entre `auth_state`, `quota_state` e `service_ready`.

## Contrato de estado correto

A UI e as APIs devem separar estes campos:

| Campo | Significado |
| --- | --- |
| `authState` | Se o Codex está autenticado no host do Paperclip |
| `quotaState` | Se a conta está bloqueada por quota/crédito |
| `serviceReady` | Se está autenticado e sem bloqueio operacional conhecido |
| `activeAccountId` | Conta selecionada no registry do Paperclip |
| `accountEmail` | Email extraído do token local sem expor segredo |
| `planType` | Plano ChatGPT extraído do token local |
| `blockers` | Lista explícita: `auth_missing`, `quota_exceeded`, `status_probe_warning` |

Regra: **nunca exibir `Not logged in` quando `auth.json` válido existir**. Nesse caso, se houver quota, mostrar `auth ok · bloqueado`.

## Blocos de resolução

### Bloco 0 — service-ready canônico

- Ler status pelo usuário `paperclip`.
- Forçar `HOME=/var/lib/paperclip` e `CODEX_HOME=/var/lib/paperclip/.codex`.
- Usar `codex login status`, não `codex status` sem TTY.
- Ler `auth.json` sem vazar tokens.
- Ler `service-account-state.json` para quota e cooldown.

### Bloco 1 — UI Agent Hub

- `/services` deve mostrar:
  - Auth: logado/não logado;
  - Quota: ok/esgotada;
  - Service-ready: sim/não;
  - conta, email, plano e último refresh;
  - botões de login/logout/status/rotação.

### Bloco 2 — login/logout no host

- Logout deve rodar como `paperclip` no host.
- Login com API key só pode rodar se o segredo estiver configurado.
- Quando não houver segredo, gerar fluxo de device auth e exibir código temporário apenas para a sessão autenticada do painel.
- Rotação para conta reserva sem segredo deve falhar de forma explícita: `sem segredo configurado`.

### Bloco 3 — rotação de contas

- `service-accounts.json` é registry/contrato.
- Infisical/GCP Secret Manager são cofre, não Git.
- O painel não deve inventar conta alternativa.
- Se `OPENAI_API_KEY_2` ou `OPENAI_API_KEY_3` não estiverem no host/cofre, a UI deve bloquear a rotação com mensagem clara.

### Bloco 4 — runtime Paperclip/Codex

- Agentes `codex_local` devem carregar `--skip-git-repo-check` para evitar falha em cwd não confiável.
- Quota precisa virar blocker operacional, não estado de logout.
- Próximo passo: atualizar cooldown/reset de quota automaticamente a partir de erro de execução ou billing quando disponível.

### Bloco 5 — auditoria e observabilidade

- Registrar ações de login/logout/rotação com timestamp.
- Nunca registrar token, refresh token, API key ou device code em logs permanentes.
- Registrar apenas: ação, usuário do painel, conta lógica, resultado e blocker.

## Execução aplicada em 2026-04-22

- `app/api/services/route.ts` do HITL no host passou a consultar o runtime real do Paperclip via `sudo -n -u paperclip`.
- `/services` passou a exibir `authState`, `quotaState`, `serviceReady`, email, plano, blockers e último refresh.
- `logout` passou a atuar no `CODEX_HOME=/var/lib/paperclip/.codex`.
- `login` com conta sem API key agora usa device auth quando aplicável ou acusa segredo ausente.
- Agentes `codex_local` no banco do Paperclip receberam `extraArgs: ["--skip-git-repo-check"]`.
- O patch também foi persistido no repositório fonte local do HITL e o build local passou.

## Definition of Done

- Painel não mostra falso `Not logged in` quando há auth válido.
- Logout remove autenticação do host do Paperclip.
- Login por device code ou API key muda o estado do runtime.
- Rotação só habilita contas com segredo real.
- Quota aparece como blocker próprio.
- Backlog e débito técnico permanecem atualizados no Shipyard.
