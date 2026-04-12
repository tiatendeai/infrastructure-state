# Ansible Ops — J.A.R.V.I.S.

Orquestração operacional do ecossistema para:

- Mac local (`localhost`)
- Hostinger KVM2 (`hostinger-kvm2`)
- Oracle staging (`oracle-prod`, `oracle-test`)
- Terraform Oracle (`vps-oracle/infra`)

## Objetivo desta camada

Usar o Ansible como plano de controle para:

1. inventariar infraestrutura
2. preparar staging bruto nas Oracle
3. gerar manifesto/export da KVM2
4. orquestrar o Terraform da Oracle com trilha de segurança
5. impedir destruição sem confirmação explícita

## Estrutura

```text
ops/ansible/
  ansible.cfg
  inventories/production/hosts.yml
  group_vars/all.yml
  playbooks/
    preflight.yml
    oracle_archive_prepare.yml
    kvm2_inventory.yml
    oracle_terraform.yml
  artifacts/
```

## Playbooks iniciais

### 1. Preflight

Valida conectividade, facts e presença de Docker.

```bash
ansible-playbook playbooks/preflight.yml
```

### 2. Preparar staging nas Oracle

Cria a estrutura canônica de arquivo bruto temporário:

```bash
ansible-playbook playbooks/oracle_archive_prepare.yml
```

### 3. Inventário da KVM2

Captura volumes, mounts e tamanhos do estado crítico.

```bash
ansible-playbook playbooks/kvm2_inventory.yml
```

### 4. Orquestrar Terraform Oracle

Por padrão este playbook **não destrói nada**.

Ele só avança quando há flags explícitas de intenção:

```bash
ansible-playbook playbooks/oracle_terraform.yml -e oracle_plan_enabled=true
```

Para qualquer ação destrutiva, além da flag, use uma confirmação explícita:

```bash
ansible-playbook playbooks/oracle_terraform.yml \
  -e oracle_destroy_enabled=true \
  -e oracle_destroy_confirmation=DESTROY-ORACLE
```

## Regras de segurança

- Nenhuma destruição roda por padrão.
- Nenhum dump bruto vai para Git.
- Git guarda manifesto, scripts e trilha de reconstrução.
- Oracle guarda bruto criptografado/staging temporário.
- KVM2 só pode ser derrubada depois de inventário + export validado.
