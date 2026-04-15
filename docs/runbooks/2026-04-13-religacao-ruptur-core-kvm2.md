# Runbook — 2026-04-13 — Religacao do core do Ruptur no KVM2

## Objetivo

Materializar o menor stack funcional do Ruptur no KVM2 para recolocar o Jarvis sobre o Ruptur.

## Premissas

- KVM2 continua sendo o core critico por economia e controle.
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
- registrar evidencias em `state` e docs relevantes;
- so promover edge publico quando o core estiver funcional.

## Tarefas de hoje

- [ ] `ruptur-db` no ar
- [ ] `ruptur-backend` no ar
- [ ] health local aprovado
- [ ] webhook/canal minimo aprovado
- [ ] integracao com Jarvis comprovada
