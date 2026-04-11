# Linear Auth Model

## Objetivo

Definir o modelo de autenticação recomendado para o ecossistema Ruptur usando apenas mecanismos oficiais do Linear.

## Opções nativas do Linear

## 1. Personal API Key

### Vantagens

- simples para scripts locais
- rápida para discovery e bootstrap
- pode ser restringida por permissão e por team

### Limitações

- identidade acoplada a uma pessoa
- menos adequada para automação compartilhada e durável
- governança e rotação dependem do usuário

### Papel recomendado no Ruptur

- desenvolvimento local
- smoke tests
- break-glass operacional
- nunca como credencial estrutural da automação

## 2. OAuth 2.0 com ator de usuário (`actor=user`)

### Vantagens

- modelo oficial para aplicações integradas ao Linear
- boa escolha quando cada usuário deve agir em seu próprio nome
- refresh token oficial suportado

### Limitações

- menos adequado para service account central
- autoria distribuída por usuário pode dificultar automação centralizada

### Papel recomendado no Ruptur

- integrações futuras que precisem respeitar autoria humana individual
- não é o modo principal para Jarvis/n8n

## 3. OAuth 2.0 com ator de app (`actor=app`)

### Vantagens

- recomendado pelo Linear para agentes e service accounts
- mutações passam a aparecer como feitas pelo app
- separa a identidade da automação da identidade humana

### Limitações

- requer setup de OAuth app
- instalação e governança exigem administração adequada do workspace

### Papel recomendado no Ruptur

- **modo principal para automação compartilhada**
- base para n8n
- base para futura orquestração do Jarvis

## 4. OAuth `client_credentials`

### Vantagens

- server-to-server nativo
- elimina dependência de fluxo interativo de usuário
- gera token de app actor

### Limitações

- token tem validade finita e precisa ser renovado
- acesso do app é controlado no nível do workspace/app
- não substitui o caso de integração multiusuário com consentimento

### Papel recomendado no Ruptur

- **modo ideal para jobs headless**
- uso por worker, cron, n8n e control-plane
- preferencial quando a integração operar somente no workspace Ruptur

## Decisão recomendada

### Produção / backbone

Usar **OAuth 2.0 como base oficial**, com prioridade para:

1. **`actor=app`**
2. **`client_credentials`** para jobs server-to-server

### Local / desenvolvimento

Permitir **personal API key com escopo reduzido** como ferramenta de:

- discovery
- bootstrap
- debug local

## Escopos mínimos sugeridos

Solicitar apenas o necessário:

- `read` para leitura
- `comments:create` se o fluxo só comentar
- `write` quando houver atualização de issue/status
- `admin` **somente** se a integração realmente precisar criar/ler webhooks ou acessar endpoints administrativos

Escopos de agente como `app:assignable` e `app:mentionable` devem ser ativados apenas se houver caso real de uso.

## Modelo de segurança recomendado

## 1. Princípio de menor privilégio

- evitar `admin` por padrão
- evitar `write` quando `comments:create` resolver
- restringir personal API keys a teams específicos sempre que possível

## 2. Separação entre humano e automação

- humano: personal API key apenas para uso local
- automação: OAuth app próprio
- mutations automatizadas: preferir `actor=app`

## 3. Segredos fora do Git

Credenciais não devem ser versionadas.

Sugestão de convenção local:

- `LINEAR_API_URL=https://api.linear.app/graphql`
- `LINEAR_PERSONAL_API_KEY=`
- `LINEAR_OAUTH_CLIENT_ID=`
- `LINEAR_OAUTH_CLIENT_SECRET=`
- `LINEAR_OAUTH_ACCESS_TOKEN=`
- `LINEAR_OAUTH_REFRESH_TOKEN=`
- `LINEAR_WEBHOOK_SECRET=`
- `LINEAR_ORGANIZATION_ID=`
- `LINEAR_TEAM_ID=`
- `LINEAR_TEAM_KEY=INF`

> Esses nomes de variáveis são uma **convenção proposta para o repo**, não nomes oficiais exigidos pelo Linear.

## 4. Rotação e validade

- personal API keys devem ter inventário e rotação manual documentada
- OAuth tokens devem seguir o modelo oficial de expiração/refresh
- `client_credentials` deve ser renovado pelo serviço quando expirar ou ao receber `401`
- rotação de `client_secret` deve invalidar o token anterior por desenho do Linear

## 5. Gestão do app OAuth

O Linear recomenda criar um workspace apropriado para administrar o OAuth app, pois admins desse workspace terão acesso ao app.

## Posição final

### Backbone oficial do Ruptur

- **OAuth app**
- **`actor=app`**
- **`client_credentials`** para jobs headless

### Ferramenta auxiliar

- **personal API key** para operação local controlada

## Referências oficiais

- OAuth 2.0 authentication: https://linear.app/developers/oauth-2-0-authentication
- OAuth actor authorization: https://linear.app/developers/oauth-actor-authorization
- GraphQL / Authentication: https://linear.app/developers/graphql
- API and Webhooks: https://linear.app/docs/api-and-webhooks
