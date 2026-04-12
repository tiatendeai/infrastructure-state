# Status — Migração Operacional Jarvis

Atualizado em: 2026-04-12

## Decisão de ferramental

### Ansible
Usado para:

- inventário de hosts
- preflight de conectividade
- preparação das Oracle como staging bruto
- export da KVM2
- bootstrap futuro de KVM2/Mac/Oracle
- instalação e configuração de serviços

### Terraform
Usado para:

- provisionar/reprovisionar Oracle
- criar/destruir VMs e recursos cloud
- manter o estado declarativo da infraestrutura

## Estado confirmado até agora

### KVM2
Tem estado persistente fora do Git:

- `kvm2_ruptur_db_data` (~616M)
- `kvm2_baileys_data` (~32M)
- `kvm2_traefik_letsencrypt` (~56K)
- `kvm2_warmup_runtime_data` (~12K)
- `kvm2_whisper_models` (~4K)
- `n8n_n8n_data` (~179M)
- `langfuse_langfuse_postgres_data` (~44M)
- `langfuse_langfuse_clickhouse_data` (~2.0G)
- `langfuse_langfuse_minio_data` (~224K)
- `/root/J.A.R.V.I.S./data` (~236K)

Conclusão:

**não é seguro destruir a KVM2 sem exportar antes.**

### Oracle

- `oracle-prod`:
  - ~9.9G livres
  - contém estado Docker legado do host2
- `oracle-test`:
  - ~40G livres
  - escolhida como staging principal do bruto da KVM2

### Terraform Oracle

Plano atual observado:

- 1 instância já gerenciada em state: `oci_core_instance.vps_x86_1`
- plano propõe criar:
  - `vps_x86_2`
  - `vps_arm_high`

Conclusão:

**o Terraform está com drift parcial; não deve ser usado de forma destrutiva antes da preservação dos dados.**

## O que vai para o Git

Pode ir para o Git:

- playbooks Ansible
- inventários
- documentação de migração
- manifesto de export
- checksums
- scripts de restore/rebuild
- trilha de reconstrução

Não vai para o Git:

- dumps de banco
- volumes Docker
- certificados
- sessões do Baileys
- credenciais do n8n
- `.env`
- dados brutos de cliente
- bruto exportado da KVM2

## Ordem segura

1. Exportar KVM2 para `oracle-test`
2. Validar manifest/checksum
3. Exportar também o estado útil das Oracle, se necessário
4. Só então decidir destruição/reprovisionamento Oracle
5. Só então destruir/limpar KVM2
6. Reerguer KVM2 com Ollama + Jarvis Core mínimo
