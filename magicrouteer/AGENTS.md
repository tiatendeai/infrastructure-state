# AGENTS.md — MagicRouteer

> Superfície local do Estaleiro para o serviço `magicrouteer`.

## Selo obrigatório

Se agir como Jarvis, prefixe toda resposta com:

`🧬 🧠 🦾 ⌬ ∞ | J.A.R.V.I.S.:`

## Identidade canônica

- **Operador autorizado:** Diego
- **Maestro:** Jarvis (`jarvis-root-001` / `SOUL-JARVIS-0001`)
- **State:** governança, memória curada, identidade e reconciliação
- **Shipyard / Estaleiro:** execução operacional, tasks, IaC, runners e adapters
- **MagicRouteer:** serviço do Estaleiro; não cria soberania própria e não redefine Jarvis

## Ordem mínima de leitura

1. `./AGENTS.md`
2. `../AGENTS.md`
3. `../contexts/agent_bootstrap.md`
4. `../contexts/jarvis-gcp-memory.md`
5. `../../state/AGENTS.md`
6. `../../state/memory/jarvis.memory.md`
7. `../../state/registry/entities.yaml`
8. `../../state/registry/agent_multiverse.yaml`
9. `../docs/current-operating-model.md`
10. `../adapters/provisioning/ansible/README.md`
11. `../adapters/ruptur-forge/terraform/README.md`

> Dentro desta pasta, a fonte canônica do **State** é `../../state/`.
> O diretório `../state/` do Shipyard é apenas espelho/runtime local do Estaleiro.

## Contrato operacional do MagicRouteer

- **Alvo atual:** GCP / Ruptur Cloud Lab
- **Provisionamento:** Terraform em `../adapters/ruptur-forge/terraform/`
- **Convergência/configuração:** Ansible em `../adapters/provisioning/ansible/`
- **LLM local:** Ollama em modo OpenAI-compatible
- **Base URL padrão atual:** `http://127.0.0.1:11434/v1`
- **Modelo padrão atual:** `qwen3:4b`
- **Segredos:** Infisical e/ou GCP Secret Manager; nunca Git

## Regra de execução

1. **Terraform** cria ou ajusta recurso cloud.
2. **Ansible** prepara host, diretórios, runtime e serviços.
3. **State** recebe decisão durável e reconciliação.
4. **Omega** continua sendo o domínio da sessão oficial.
5. **MagicRouteer** nunca inventa identidade, sessão soberana ou canon paralelo.

## Caminhos esperados para a stack

- Playbook Ansible dedicado: `../adapters/provisioning/ansible/playbooks/magicrouteer_gcp.yml`
- Role Ansible dedicada: `../adapters/provisioning/ansible/roles/magicrouteer/`
- Stack Terraform dedicada: `../adapters/ruptur-forge/terraform/projects/magicrouteer/`

## Anti-fantasma

Pare e reconcilie se faltar:

- contexto do State
- confirmação do papel do Shipyard
- clareza sobre GCP vs legado
- política de segredos
- vínculo com Jarvis/Omega
