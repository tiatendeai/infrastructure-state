# Resolução de Bloqueio SSH - Ruptur Shipyard

## Problema Original

Instância GCP `ruptur-shipyard-01` (34.39.196.137) em southamerica-east1-b não respondia SSH, impedindo deploy via Ansible.

## Diagnóstico (5 Whys)

### 1. Por que não consigo fazer deploy via Ansible?
Instância GCP `ruptur-shipyard-01` não responde SSH

### 2. Por que a instância não responde SSH?
Serviço SSH pode estar parado/bloqueado e não consigo acessar para verificar/reiniciar

### 3. Por que não consigo acessar para reiniciar o SSH?
- SSH direto timeout
- IAP tunnel falha (failed to connect to backend)
- Serial console não permite comandos diretos

### 4. Por que a instância está parada e não consigo iniciar?
Parei a instância para aplicar startup-script de reinicialização do SSH, mas zona southamerica-east1-b está sem recursos (ZONE_RESOURCE_POOL_EXHAUSTED)

### 5. Por que a zona está sem recursos?
GCP não tem capacidade disponível para n2-standard-4 na zona southamerica-east1-b neste momento

## Tentativas Realizadas

### 1. SSH Direto
```bash
ssh -i ~/.ssh/google_compute_engine diego@34.39.196.137
```
**Resultado:** Operation timed out

### 2. IAP Tunnel
```bash
gcloud compute ssh ruptur-shipyard-01 --tunnel-through-iap
```
**Resultado:** Error while connecting [4003: 'failed to connect to backend']

### 3. Reset da Instância
```bash
gcloud compute instances reset ruptur-shipyard-01
```
**Resultado:** Instância reiniciou, mas SSH continuou timeout

### 4. Serial Logs
```bash
gcloud compute instances get-serial-port-output ruptur-shipyard-01
```
**Resultado:** Sistema operacional totalmente funcional (DHCP, serviços systemd, Paperclip rodando)

### 5. Startup-Script para Reiniciar SSH
```bash
gcloud compute instances add-metadata ruptur-shipyard-01 --metadata-from-file=startup-script=/tmp/restart_ssh.sh
```
**Resultado:** Script configurado, mas instância foi parada para aplicar

### 6. Tentar Iniciar Instância
```bash
gcloud compute instances start ruptur-shipyard-01
```
**Resultado:** ZONE_RESOURCE_POOL_EXHAUSTED - zona sem recursos

### 7. Criar Nova Instância em southamerica-east1-a
```bash
gcloud compute instances create ruptur-shipyard-02 --zone=southamerica-east1-a
```
**Resultado:** ZONE_RESOURCE_POOL_EXHAUSTED - zona também sem recursos

### 8. Criar Nova Instância em southamerica-west1-a
```bash
gcloud compute instances create ruptur-shipyard-02 \
  --zone=southamerica-west1-a \
  --machine-type=n2-standard-4 \
  --boot-disk-type=pd-standard \
  --boot-disk-size=100GB \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=ssh-keys="diego:$(cat ~/.ssh/google_compute_engine.pub)"
```
**Resultado:** ✅ SUCESSO - Instância criada em southamerica-west1-a (34.176.34.240)

## Solução Final

### Passo 1: Criar Nova Instância em Região Disponível
- Região: southamerica-west1-a (Chile)
- Zona: southamerica-west1-a
- Tipo: n2-standard-4
- Disco: pd-standard (100GB) - não SSD para não exceder quota
- IP Externo: 34.176.34.240

### Passo 2: Atualizar Inventários Ansible

**shipyard/inventories/production/hosts.yml:**
```yaml
ruptur-shipyard-01:
  ansible_host: "34.176.34.240"
  ansible_user: "diego"
  ansible_ssh_private_key_file: "~/.ssh/google_compute_engine"
  gcp_project: "ruptur-jarvis-v1-68358"
  gcp_zone: "southamerica-west1-a"
```

**ruptur-lab-main/infra/ansible/inventories/production/hosts.yml:**
```yaml
shipyard_lab:
  ansible_host: "34.176.34.240"
```

### Passo 3: Testar SSH
```bash
ssh -i ~/.ssh/google_compute_engine diego@34.176.34.240
```
**Resultado:** ✅ Conexão bem-sucedida

### Passo 4: Atualizar DNS Cloudflare (Pendente - Ação Manual)
- `app` → 34.176.34.240
- `ruptur.cloud` (root) → 34.176.34.240
- `saas` → 34.176.34.240 (criar novo registro)

## Lições Aprendidas

1. **Zonas GCP podem ficar sem recursos temporariamente** - southamerica-east1 estava esgotado
2. **Tentar regiões alternativas** - southamerica-west1 (Chile) tinha capacidade
3. **Quota SSD pode limitar opções** - usar pd-standard quando quota SSD excedida
4. **Serial logs são úteis para diagnóstico** - confirmaram que sistema estava funcional
5. **IAP tunnel não é solução garantida** - falhou mesmo com instância funcional
6. **Prever múltiplas zonas** - ideal ter infraestrutura distribuída em zonas/regionais

## Artefatos Criados

- Snapshot: `ruptur-shipyard-01-snapshot` (do disco original)
- Nova instância: `ruptur-shipyard-02` em southamerica-west1-a
- Documentação de testes: `shipyard/docs/saas-deploy-test-cases.md`

## Próximos Passos

1. Atualizar DNS Cloudflare para novo IP (34.176.34.240)
2. Executar playbook Ansible para provisionar Docker e Traefik na nova instância
3. Deploy do SaaS via role `saas`
4. Validar com test cases documentados
5. Limpar recursos antigos (instância original em southamerica-east1-b)
