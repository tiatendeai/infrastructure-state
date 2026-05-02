# MagicRouteer

Novo espaço local do Estaleiro para o serviço `magicrouteer`, preparado no padrão **GCP First + Ollama local + Terraform + Ansible**.

## O que é cada camada

- **State:** fonte canônica de governança, identidade, memória e reconciliação.
- **Shipyard / Estaleiro:** executor operacional; onde vivem tasks, adapters, runbooks e a trilha auditável.
- **Jarvis:** maestro do ecossistema; coordena, não é rebatizado aqui.
- **MagicRouteer:** serviço/stack do Estaleiro; nasce subordinado ao padrão do ecossistema.

## Contrato inicial

- runtime alvo: **GCP / Ruptur Cloud Lab**
- inferência local: **Ollama**
- modelo default atual: `qwen3:4b`
- provisionamento: **Terraform**
- convergência do host/runtime: **Ansible**
- segredos fora do Git: **Infisical** e/ou **GCP Secret Manager**

## Caminhos canônicos

- contexto local: `./AGENTS.md`
- contexto do Estaleiro: `../AGENTS.md`
- bootstrap do agente: `../contexts/agent_bootstrap.md`
- memória runtime GCP: `../contexts/jarvis-gcp-memory.md`
- State canônico: `../../state/AGENTS.md`
- Ansible: `../adapters/provisioning/ansible/`
- Terraform: `../adapters/ruptur-forge/terraform/`

## Regra operacional

1. Terraform provisiona a base no GCP.
2. Ansible converte o host/runtime.
3. Decisão durável sobe para o State.
4. Sessão oficial continua no Omega.
5. Segredo real não entra em commit.

## Próximos pontos de extensão

- `../adapters/provisioning/ansible/playbooks/magicrouteer_gcp.yml`
- `../adapters/provisioning/ansible/roles/magicrouteer/`
- `../adapters/ruptur-forge/terraform/projects/magicrouteer/`
- `./docs/OPERATING_MODEL.md`
