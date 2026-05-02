# Runbook — 2026-04-13 — Religacao do core do Ruptur no KVM2

> **LEITURA ATUAL:** este runbook é **histórico**. O presente operacional do ecossistema é o **shipyard** no **Ruptur Cloud Lab / GCP**. KVM2 é legado.

## Objetivo

Materializar, na época, o menor stack funcional do Ruptur no KVM2 para recolocar o Jarvis sobre o Ruptur.

## Premissas

- KVM2 continuava sendo o core crítico por economia e controle, **naquele momento histórico**.
- Plataformas externas entram como alivio tatico, nao como ownership do core.
- O caminho critico do dia e `ruptur-db` + `ruptur-backend` + canal minimo.

## Ordem operacional

1. validar `docker compose` do `deploy/kvm2` com `kvm2.env` e `backend.env` reais;
2. subir `ruptur-db`;
3. subir `ruptur-backend`;
4. validar `GET /health` local;
5. validar webhook/canal;
6. so depois avaliar `baileys`, `whisper`, `ruptur-web`, `traefik` e DNS.

## Regras

- nao criar stack paralela antes de religar a stack existente;
- nao trocar ownership do core por conveniencia de provider;
- registrar evidências em `state` e docs relevantes;
- so promover edge publico quando o core estiver funcional.

## Tarefas de hoje

- [ ] `ruptur-db` no ar
- [ ] `ruptur-backend` no ar
- [ ] health local aprovado
- [ ] webhook/canal minimo aprovado
- [ ] integracao com Jarvis comprovada

## Leitura canônica atual

Hoje o mesmo tipo de operação deve ser lido assim:

- `shipyard` como Estaleiro
- `state` como memória canônica
- `Ruptur Cloud Lab / GCP` como runtime atual
- `KVM2` apenas como histórico de uma fase anterior
