# Playbook: Operação do Maestro (POP)

**Procedimento Operacional Padrão (POP) para o Ecossistema Maestro**

---

## 🏗️ 1. Início da Missão (O Gatilho)

Toda tarefa complexa que exija inteligência externa deve ser iniciada pelo comando:
> `/ruptur_maestro [DESCRIÇÃO DA MISSÃO]`

**Ação do Maestro:**
1.  **Escaneamento**: O Maestro lê o diretório local para entender o contexto.
2.  **Consulta ao Vault**: Baseado na missão, ele busca no diretório absoluto `/Users/diego/dev/GitHub/ruptur-skills/skills/` as habilidades necessárias.

---

## 🗣️ 2. Fase 1: O Debate (Consenso)

O Maestro não gera código antes desta fase ser concluída.

1.  **Declaração do Squad**: O Maestro lista os especialistas "contratados" (ex: `@ui-ux-pro`, `@security-auditor`).
2.  **Painel de Debate**: A IA simula um diálogo entre as personas sobre a melhor abordagem.
3.  **Aprovação Humana**: O usuário (Diego) deve validar o plano. "Aprovado" ou correções.

---

## ⚙️ 3. Fase 2: Registro Efêmero (A Execução)

Após a aprovação, o Maestro cria a infraestrutura de pensamento:

1.  **Diretório de Missão**: Criação de `.agents/maestro_ativo/`.
2.  **Registro de Atividades**: Criação do arquivo `registro_atividades.json`.
3.  **Injeção Cirúrgica**: Cópia temporária dos arquivos `SKILL.md` das skills selecionadas para a pasta ativa.
4.  **Execução**: O Maestro cumpre cada tarefa do JSON, registrando o progresso e o tempo.

> [!TIP]
> **Subpastas de Controle**: Use `caixa_entrada/` para novos insumos e `travas/` para arquivos `.lock` caso precise de paralelismo.

---

## ❄️ 4. Fase 3: Hibernação (O Fechamento)

Ao atingir 100% de conclusão no JSON:

1.  **Consolidação**: O Maestro gera um resumo final da missão.
2.  **Arquivamento**: O arquivo `registro_atividades.json` é movido para `.agents/maestro_historico/missao_[DATA].json`.
3.  **Higiene**: A pasta `maestro_ativo/` é **inteiramente deletada**. O projeto volta a ser um "Lienzo Blanco" de inteligência, mantendo apenas o código gerado.

---

## 📚 5. Manutenção do Vault (Skills 2.1)

Para novas habilidades seguirem o padrão Maestro:

1.  **Criação**: Use a skill `skill-creator`.
2.  **Estrutura**: Pasta contendo obrigatoriamente um `SKILL.md` com Frontmatter YAML.
3.  **Purificação**: Prompts brutos em `prompts_brutos/` devem ser traduzidos para o formato 2.1 para serem "Maestro-Ready".

---

> [!IMPORTANT]
> **A Regra de Ouro Context7**: Nunca utilize uma biblioteca, API ou framework sem antes realizar o `Resolve ID` e `Query Docs` no Context7. Essa é a bússola que impede a obsolescência.
