# Casos de Teste - Deploy Ruptur SaaS

## Smoke Tests (Pré-Deploy)

### TC-001: Verificar Resolução DNS
**Objetivo:** Validar que os domínios resolvem para o IP correto do GCP

**Passos:**
1. Executar `nslookup app.ruptur.cloud`
2. Executar `nslookup ruptur.cloud`
3. Executar `nslookup saas.ruptur.cloud` (após criação)

**Resultado Esperado:**
- Todos devem resolver para `34.39.196.137`

**Critério de Sucesso:** ✓ DNS resolvendo para IP GCP

---

### TC-002: Verificar Conectividade HTTP
**Objetivo:** Validar que os domínios respondem na porta 443

**Passos:**
1. `curl -I https://app.ruptur.cloud`
2. `curl -I https://ruptur.cloud`
3. `curl -I https://saas.ruptur.cloud` (após criação)

**Resultado Esperado:**
- HTTP 200, 301, 302 ou 503 (container ainda não deployado)
- Header TLS presente

**Critério de Sucesso:** ✓ Resposta HTTP com TLS

---

### TC-003: Verificar Conectividade SSH
**Objetivo:** Validar acesso SSH ao host GCP

**Passos:**
1. `ssh -i ~/.ssh/google_compute_engine diego@34.39.196.137 "uptime"`

**Resultado Esperado:**
- Conexão bem-sucedida
- Uptime retornado

**Critério de Sucesso:** ✓ SSH funcional

---

## Smoke Tests (Pós-Deploy)

### TC-004: Verificar Container Rodando
**Objetivo:** Validar que o container Docker está rodando

**Passos:**
1. SSH no host
2. `docker ps | grep saas-web`
3. `docker logs saas-web --tail 20`

**Resultado Esperado:**
- Container com status "Up"
- Logs sem erros críticos

**Critério de Sucesso:** ✓ Container saas-web rodando

---

### TC-005: Verificar Warmup Manager
**Objetivo:** Validar que o Warmup Manager está acessível

**Passos:**
1. Acessar `https://app.ruptur.cloud/warmup/`
2. Verificar se a página carrega
3. Verificar console browser para erros

**Resultado Esperado:**
- Página carrega sem erros 500
- Assets carregados corretamente

**Critério de Sucesso:** ✓ Warmup Manager acessível

---

### TC-006: Verificar API Endpoints
**Objetivo:** Validar que endpoints da API respondem

**Passos:**
1. `curl https://app.ruptur.cloud/warmup/api/local/health`
2. `curl https://app.ruptur.cloud/warmup/api/local/instances`

**Resultado Esperado:**
- Resposta JSON válida
- Status HTTP 200

**Critério de Sucesso:** ✓ API respondendo

---

### TC-007: Verificar Front Lindona (Landing Page)
**Objetivo:** Validar que a landing page carrega

**Passos:**
1. Acessar `https://ruptur.cloud/`
2. Verificar se a página carrega
3. Verificar se cards de diagnóstico aparecem

**Resultado Esperado:**
- Página carrega
- UI renderizada corretamente

**Critério de Sucesso:** ✓ Landing page acessível

---

### TC-008: Verificar Traefik Routing
**Objetivo:** Validar que Traefik está roteando corretamente

**Passos:**
1. SSH no host
2. `docker logs traefik --tail 20 | grep saas`
3. Verificar dashboard Traefik (se disponível)

**Resultado Esperado:**
- Logs mostram routing para saas-web
- Sem erros de routing

**Critério de Sucesso:** ✓ Traefik roteando corretamente

---

### TC-009: Verificar Network Docker
**Objetivo:** Validar que container está na network correta

**Passos:**
1. SSH no host
2. `docker network inspect ruptur-edge`
3. Verificar se saas-web está na network

**Resultado Esperado:**
- Container saas-web listado na network ruptur-edge

**Critério de Sucesso:** ✓ Network configurada corretamente

---

### TC-010: Verificar Volumes Montados
**Objetivo:** Validar que volumes estão montados corretamente

**Passos:**
1. SSH no host
2. `docker inspect saas-web | grep -A 10 Mounts`
3. Verificar se data e logs estão montados

**Resultado Esperado:**
- Volumes `/opt/ruptur/data/saas` e `/opt/ruptur/logs/saas` montados

**Critério de Sucesso:** ✓ Volumes montados

---

## Functional Tests

### TC-011: Verificar Conexão Supabase
**Objetivo:** Validar que o SaaS consegue conectar ao Supabase

**Passos:**
1. Verificar logs do container
2. Procurar erros de conexão Supabase
3. Testar endpoint que usa Supabase

**Resultado Esperado:**
- Sem erros de conexão
- Dados sendo persistidos

**Critério de Sucesso:** ✓ Supabase conectado

---

### TC-012: Verificar Conexão UAZAPI
**Objetivo:** Validar que o SaaS consegue conectar à UAZAPI

**Passos:**
1. Verificar logs do container
2. Procurar erros de conexão UAZAPI
3. Testar polling de instâncias

**Resultado Esperado:**
- Sem erros de conexão
- Instâncias sendo listadas

**Critério de Sucesso:** ✓ UAZAPI conectado

---

### TC-013: Verificar Warmup Scheduler
**Objetivo:** Validar que o scheduler está executando

**Passos:**
1. Verificar logs do container
2. Procurar mensagens de tick/scheduler
3. Verificar se warmup está rodando

**Resultado Esperado:**
- Logs mostram ticks do scheduler
- Warmup em execução

**Critério de Sucesso:** ✓ Scheduler rodando

---

## Security Tests

### TC-014: Verificar HTTPS/TLS
**Objetivo:** Validar que TLS está configurado corretamente

**Passos:**
1. `curl -I https://app.ruptur.cloud`
2. Verificar header SSL/TLS
3. Usar SSL Labs para teste profundo

**Resultado Esperado:**
- Certificado válido
- TLS 1.2+ habilitado

**Critério de Sucesso:** ✓ TLS funcional

---

### TC-015: Verificar Headers de Segurança
**Objetivo:** Validar headers de segurança HTTP

**Passos:**
1. `curl -I https://app.ruptur.cloud`
2. Verificar headers: X-Frame-Options, X-Content-Type-Options, etc.

**Resultado Esperado:**
- Headers de segurança presentes (via Traefik)

**Critério de Sucesso:** ✓ Headers configurados

---

## Performance Tests

### TC-016: Verificar Tempo de Resposta
**Objetivo:** Validar tempo de resposta aceitável

**Passos:**
1. `curl -w "@curl-format.txt" -o /dev/null -s https://app.ruptur.cloud/`
2. Medir time_total

**Resultado Esperado:**
- Tempo de resposta < 2s

**Critério de Sucesso:** ✓ Performance aceitável

---

## Rollback Tests

### TC-017: Verificar Rollback
**Objetivo:** Validar capacidade de rollback

**Passos:**
1. Parar container: `docker stop saas-web`
2. Reverter para versão anterior (se disponível)
3. Verificar se serviço volta

**Resultado Esperado:**
- Rollback executado com sucesso
- Serviço funcional

**Critério de Sucesso:** ✓ Rollback funcional

---

## Checklist de Deploy

- [ ] DNS atualizado (app, ruptur.cloud, saas)
- [ ] SSH funcional no host GCP
- [ ] Docker instalado e rodando
- [ ] Network ruptur-edge existe
- [ ] Traefik rodando
- [ ] Código SaaS copiado para host
- [ ] Arquivo .env copiado com segredos
- [ ] Docker image build bem-sucedido
- [ ] Container saas-web rodando
- [ ] Health check passando
- [ ] Logs sem erros críticos
- [ ] Smoke tests passando
- [ ] Functional tests passando
