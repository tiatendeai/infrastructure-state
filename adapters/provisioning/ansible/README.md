# Ansible

Camada de configuração do host Debian e renderização do runtime em containers.

## Escopo da fase 1

- preparar host Debian 11
- instalar Docker Engine
- criar diretórios e redes do runtime
- renderizar compose/configuração para:
  - Traefik
  - Portainer
  - Postgres
  - Redis
  - n8n
  - MinIO

## Contrato operacional

- `site.yml` prepara o host inteiro
- `shipyard_compose_autostart` é `false` por padrão
- segredos reais entram por override local em `inventories/production/group_vars/secrets.yml` ou extra-vars externos
- o playbook carrega `secrets.yml` explicitamente antes de renderizar os templates
- exemplos rastreáveis ficam em `examples/production/`, nunca em `group_vars/`
- Uazapi permanece fora da VM
