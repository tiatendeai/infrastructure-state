# PRD: Framework Maestro

**Documento de Requisitos do Produto (v1.0)**

---

## 📅 1. Visão Geral

O **Framework Maestro** é uma infraestrutura de orquestração de agentes de IA projetada para gerenciar projetos complexos (ex: Zaya, Dr. Flávio) através de inteligência modular, injetável e efêmera. O sistema utiliza Antigravity como host e um Vault Central como fonte de habilidades.

---

## 🛠️ 2. Especificações Técnicas (Stack)

O Maestro opera como uma malha de ferramentas integradas via **MCP (Model Context Protocol)** e Webhooks.

| Componente | Ferramenta | Função no Framework |
|---|---|---|
| **Host** | Antigravity (Claude Desktop) | Local de Execução e Orquestração |
| **Vault** | GitHub (`ruptur-skills`) | Fonte da Verdade (Skills 2.1) |
| **Infraística** | n8n | Automação de Workflows e Deploy |
| **Conhecimento** | Context7 | Bússola Técnica (Docs em tempo real) |
| **Dados / State** | Notion / PostgreSQL | Persistência de Tickets, Mensagens e Status |
| **Comunicação** | Slack / Telegram | Interface de Notificação |

---

## 🏗️ 3. Requisitos de Infraestrutura

### O Modelo de Sincronização (A Trindade de Ambientes)
1.  **Ambiente LOCAL (Work-in-progress)**: Onde a missão ocorre na pasta `.agents/maestro_ativo/`.
2.  **Ambiente DEV (Evolução)**: Onde os workflows do n8n são testados via scripts `sync_dev.sh`.
3.  **Ambiente PROD (Referência)**: O espelhamento final no GitHub (`main`) e Servidores KVM.

---

## ⚖️ 4. Regras de Governança (Business Logic)

### G1: Protocolo de Injeção Cirúrgica
- Nenhuma skill deve residir permanentemente na raiz do projeto.
- Inteligência é um recurso "alugado" do Vault via comando `/ruptur_maestro`.

### G2: Doutrina Context7 (Truth-First)
- O agente é proibido de sugerir código baseado em memória interna para bibliotecas mapeadas no Context7.
- O fluxo de `Resolve ID` -> `Query Docs` é **bloqueante**.

### G3: Ciclo de Vida da Missão
- **Gatekeeping**: Só inicia missão com registro JSON.
- **Registry**: Registro em tempo real de cada subtarefa.
- **Destruction**: Hibernação total após a missão.

---

## 📈 5. Métricas de Sucesso (KPIs)

- **Token Efficiency**: Redução de tokens desperdiçados em contextos irrelevantes.
- **Deterministic Success Rate**: Taxa de missões concluídas sem intervenção manual de correção.
- **Repository Hygiene**: Zero arquivos de prompt ou restos de debug no core do projeto após a hibernação.

---

> [!CAUTION]
> **Segurança**: Caminhos absolutos devem ser utilizados para referenciar o Vault (`/Users/diego/dev/GitHub/ruptur-skills/`) para garantir que o Maestro sempre consulte a versão de produção das habilidades, sem depender de clones locais desatualizados.
