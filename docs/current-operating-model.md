# Modelo Operacional Atual

Este documento consolida o presente do ecossistema Ruptur em uma leitura curta e canônica.

## Nomes canônicos

- **State**: memória canônica viva, governança, mapas e rastreabilidade
- **Shipyard**: Estaleiro operacional, execução, tasks, runners e adapters
- **Ruptur Cloud Lab / GCP**: runtime operacional atual
- **Infisical**: cofre canônico de segredos e credenciais
- **Terraform**: IaC declarativa principal
- **Ansible**: configuração e sustentação de hosts
- **Obsidian + Excalidraw**: mapas vivos, navegação visual e leitura rápida
- **Rusty RDK**: referência de evolução de runtime/SDK em Rust

## Contrato de segredos

O mapa canônico de nomes, escopos e consumo de segredos fica em:

- `docs/INFISICAL_SECRET_MAP.md`
- `state/registry/infisical-secret-contract.json`

Regra operacional:

- o segredo real vive no Infisical
- o Git guarda apenas o contrato
- ausência de segredo é tratada como estado explícito

## Legado histórico

Ficam como legado, apenas para rastreabilidade:

- `infrastructure-state` (nome anterior do estaleiro)
- `KVM2`
- `Hostinger`
- `oracle-*`

## Catálogo de serviços e objetivos

### Catálogo canônico

- `shipyard-lab`: laboratório de inteligência / infraestrutura no GCP
- `magicrouteer`: serviço de roteamento/coordenação AI local-first preparado para GCP + Ollama
- `ruptur-backend`: backend do ecossistema
- `ruptur-web`: frontend do ecossistema
- `baileys`: gateway de integração
- `whisper`: runtime de IA / áudio
- `n8n`: automação
- `redis`: memória curta / estado operacional
- `langfuse`: observabilidade de agentes
- `infisical`: segredos
- `temporal`: workflows resilientes
- `uptime-kuma`: monitoramento

### Objetivos vivos

1. reduzir consumo de tokens e custo de contexto
2. estabilizar sessão, login, revogação e auditoria
3. separar falha real de ausência explícita de credencial
4. estabilizar TLS/SSL e sync de memória longa
5. manter a borda Cloudflare e os DNSs coerentes
6. eliminar ambiguidade entre presente operacional e legado histórico
7. manter o State e o Shipyard sincronizados com a fila real

## Fila P0 atual

- **Tokens e contexto**: budget, preflight, RTK e disciplina de prompt
- **Sessão e login**: revogação, auditoria, segurança e observabilidade
- **Triagem de falhas**: causalidade, impacto e drift de runtime
- **Linear auth**: credencial ausente tratada como ausência explícita, não falha ambígua
- **Supabase TLS/SSL**: trust store, CA bundle e memória longa
- **Cloudflare / DNS**: borda `aiox.ruptur.cloud`, auth e proxy
- **AIOX bridge**: Hermes / Ollama / health doctor

## Regra de leitura

Quando houver conflito entre histórico e presente:

1. prevalece o **State**
2. a execução acontece no **Shipyard**
3. o alvo atual é **Ruptur Cloud Lab / GCP**
4. o legado fica documentado, mas não dirige a operação

## Regra de segredos

- segredos reais vivem no **Infisical**
- Git guarda apenas contratos, nomes e placeholders
- Ansible e runtimes recebem valores materializados na hora da execução
