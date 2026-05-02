# Modelo Operacional — MagicRouteer

## Identidade e hierarquia

- **Alpha** ancora a gênese.
- **State** governa identidade, memória curada e reconciliação.
- **Omega** governa a sessão oficial.
- **Shipyard** executa infra, automação e mudança controlada.
- **MagicRouteer** é uma stack do Shipyard; não é uma camada soberana nova.

## Como fazemos aqui

### Terraform

Usado para **provisionar** ou **ajustar** recursos declarativos no GCP:

- VM
- IP
- disco
- service account
- rede
- bindings de infra quando entrarem no escopo aprovado

Raiz canônica no Estaleiro:

- `../adapters/ruptur-forge/terraform/`
- stack dedicada: `../adapters/ruptur-forge/terraform/projects/magicrouteer/`

### Ansible

Usado para **convergir** o host e o runtime depois do provisionamento:

- diretórios
- systemd
- Docker/compose quando necessário
- arquivos de configuração
- smoke operacional

Raiz canônica no Estaleiro:

- `../adapters/provisioning/ansible/`
- playbook dedicado: `../adapters/provisioning/ansible/playbooks/magicrouteer_gcp.yml`
- role dedicada: `../adapters/provisioning/ansible/roles/magicrouteer/`

### Ollama

Contrato padrão atual do runtime local:

- provider: `ollama`
- base URL: `http://127.0.0.1:11434/v1`
- modelo default atual: `qwen3:4b`

Se o modelo mudar, a decisão deve ser reconciliada no State antes de virar padrão.

## Segredos

- segredo real vive em **Infisical** e/ou **GCP Secret Manager**
- Git guarda só contrato, nome, placeholder e documentação
- `.env`, tokens, dumps e credenciais não entram no repositório

## Checklist mínimo para agentes

1. Ler `./AGENTS.md`
2. Ler `../AGENTS.md`
3. Ler `../../state/AGENTS.md`
4. Confirmar que o alvo é GCP e não legado
5. Decidir se a mudança é de Terraform, de Ansible ou de ambos
6. Evitar segredos em texto puro
7. Registrar decisão durável no State
