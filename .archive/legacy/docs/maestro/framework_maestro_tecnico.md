# Enciclopédia Técnica do Framework Maestro

Este documento fornece um mapeamento detalhado e reflexivo de cada componente técnico e metodológico que compõe o **Sistema Operacional de Inteligência** de Diego.

---

## 🏗️ 1. Dinâmica de Agentes e Orquestração

### Multi-agentes e Agentes em Debate
- **A Lógica**: O framework não confia em um único agente para tarefas complexas. Antes da execução, utiliza-se a skill `multiagentes_debate` para formar um **Squad de Especialistas**.
- **O Processo**: O agente "contrata" personas (lendo suas `SKILL.md`) que debatem a solução no chat. Isso cria uma camada de **Revisão Dialética**, onde diferentes perspectivas (ex: Sênior Backend vs. Auditor de Segurança) validam o plano.
- **Conformidade**: A "Missão" só avança após o consenso humano sobre o debate.

### Maestro vs. Master Skill (Skill Orchestrator)
- **Maestro (Antigravity)**: É o "Host" (Sistema Operacional). Ele gerencia o ciclo de vida (A Trindade).
- **Master Skill (`antigravity-skill-orchestrator`)**: É o cérebro de despacho. Ela não executa código, ela **pensa sobre quais ferramentas usar**. Usa um catálogo global (`CATALOG.md`) para buscar habilidades que não estão presentes localmente.

---

## 🧬 2. Evolução das Skills (2.0 vs. 2.1)

| Característica | Skill 2.0 (Legado/Consultoria) | Skill 2.1 (Atual/Cirúrgica) |
|---|---|---|
| **Arquitetura** | Monolítica, baseada em diálogo intenso. | Modular, baseada em diretórios e injeção. |
| **Foco** | Entrevista e "Roadmap" textual. | Ferramentas (scripts) e regras procedurais. |
| **Uso** | Ex: `00-andruia-consultant`. | Ex: +1200 skills no Vault `ruptur-skills`. |
| **Operação** | O agente "fala" como o especialista. | O agente "se torna" o especialista via `SKILL.md` + scripts anexos. |

> [!NOTE]
> A transição para 2.1 permitiu o **Surgical Injection**: o projeto não "fica com a skill" permanentemente; ele apenas a consome durante a sessão.

---

## 🧭 3. Doutrina de Consumo (Context7 & Tech-First)

Existe uma regra rígida de **"Verdade Baseada em Evidência"**:
- **Consumo Mandatório**: Sempre que uma tecnologia é introduzida ou editada (ex: configurar um nó de e-mail no n8n), o agente **deve** imediatamente realizar o fluxo: `mcp_context7-api_resolve-library-id` -> `query-docs`.
- **Armazenamento**: O conhecimento é "alugado". A IA extrai as diretrizes e as mantém ativas na sessão para consumo imediato.
- **Fim da Intuição**: Se a tech não está no Context7, o agente é proibido de improvisar sem autorização.

---

## 🚦 4. Infraestrutura de Controle (Plano de Comando)

A gestão do trabalho é feita através de uma **RAM de Diretórios** efêmeros.

### Ferramentas de Inteligência e Decisão
- **`maestro_ativo/`**: A pasta de trabalho atual.
- **`registro_atividades.json`**: O log de estado determinístico. Se o processo cair, a IA retoma exatamente de onde parou lendo este JSON.
- **`travas/` (Lock Files)**: Evita que dois agentes (ou o usuário + agente) operem na mesma ferramenta simultaneamente.
- **`caixa_entrada/`**: Local de despejo para insumos e payloads externos que serão processados pela missão.

### Uso de Diretórios Externos
O framework opera em modo **Cross-Repo**:
- Busca inteligência no Vault (`/Users/diego/dev/GitHub/ruptur-skills/`).
- Consulta memória institucional via `agent-memory-mcp`.
- Mantém o repositório do cliente limpo, usando caminhos absolutos para gerenciar bibliotecas globais de scripts.

---

## 🧠 5. Arquitetura Cognitiva e Mentalidades

### BDI (Belief-Desire-Intention)
O framework utiliza modelos de estados mentais:
- **Beliefs**: Fatos que o agente acredita sobre o projeto (extraídos do escaneamento de arquivos).
- **Desires**: Os objetivos finais do usuário.
- **Intentions**: Os planos de ação aos quais o agente se comprometeu.

### T2B2T (Triples-to-Beliefs-to-Triples)
- Um padrão de raciocínio semântico onde dados brutos (RDF/Triples) tornam-se Crenças da IA, que após deliberação, geram novos dados processados.

### Modos de Trabalho Especiais
- **Modo Loki**: Execução totalmente autônoma e paralela para startups e prototipação ultrarrápida (High Speed, High Risk).
- **Modo Consultor (2.0)**: Focado em diagnóstico e estratégia.
- **Modo Engenheiro (2.1)**: Focado em construção modular e deploy.

---

## 🔍 Modos Não Mapeados (Deteções)

- **Dispatching Parallel Agents**: Notei que o framework prevê o despacho de múltiplos agentes subjacentes para tarefas que podem ser executadas em paralelo, aumentando a vazão de desenvolvimento.
- **Subagent-Driven Development**: Uma metodologia onde o Maestro não faz o trabalho, ele **gere sub-agentes** que fazem as tarefas atômicas, mantendo o Maestro no nível estratégico.

---

> [!CAUTION]
> **A Mentalidade Maestro**: A maior ferramenta de controle aqui é a **Efemeridade**. Ao destruir a pasta de trabalho ao final (Hibernação), você garante que a "alma" técnica do projeto não se torne um lixão de prompts antigos, mantendo apenas o código limpo no Git.
