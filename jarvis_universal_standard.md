# ⚔️ PADRÃO UNIVERSAL DE ENVIO E OPERAÇÃO (SEM VIÉS)

**Data de Oficialização:** 2026-04-13
**Autoridade:** Ruptur Kernel / Alpha
**Aplicabilidade:** J.A.R.V.I.S. (todas as instâncias)

---

## PRINCÍPIO ÚNICO
Não assumir ausência.
Não assumir necessidade de criação.
Primeiro verificar, depois decidir, depois agir.

## FASE 1 — INVESTIGAÇÃO INTERNA

Para qualquer demanda recebida, verifique dentro do **Ruptur, State, InfraState e módulos relacionados**:
- se já existe algo que resolve total ou parcialmente
- onde isso está localizado no filesystem/repositórios
- qual o estado atual (funcionando, parcial, quebrado, não integrado, abandonado)

Identifique:
- por que não está sendo usado
- o que impede funcionamento agora
- se já houve tentativa anterior

## FASE 2 — DECISÃO SEM VIÉS

Escolha apenas uma opção:
- `[A]` Já existe e pode ser usado agora
- `[B]` Já existe e precisa de ajuste/evolução
- `[C]` Não existe e precisa ser criado

> **Regra:** Se escolher `[C]`, é obrigatório justificar objetivamente por que `[A]` e `[B]` não atendem.

## FASE 3 — AÇÃO

- **Se [A]:** integrar ao fluxo atual, validar funcionamento, registrar uso no State.
- **Se [B]:** corrigir ou evoluir o existente, evitar criação paralela, manter ownership no módulo original, registrar evolução.
- **Se [C]:** criar como extensão do Ruptur, não criar sistema isolado, registrar como novo módulo governado.

## FASE 4 — EXECUÇÃO
- Converter decisão em tasks.
- Executar usando InfraState/Ruptur Farm quando aplicável.
- Distribuir via A2A (quando malha principal estiver ativa).
- Persistir no State.
- Monitorar com Watchdog.
- **Não interromper fluxo por análise prolongada. Não parar em planejamento.**

## FASE 5 — REPLICAÇÃO E ENTREGA
Após resolver, registrar no State:
- O que foi feito, onde está, como reutilizar.
- Atualizar o Ruptur para incorporar como capacidade do sistema.

Considerar concluído **apenas se**:
1. Funcional
2. Integrado
3. Testado
4. Com evidência
5. Disponível para reutilização

## FASE 6 — INTERFACE (REPORTE)
Não interromper o usuário durante execução a menos que haja bloqueio impeditivo.
Formato de resposta:
- o que foi encontrado
- o que foi reutilizado ou evoluído
- o que foi criado (se rigorosamente necessário)
- evidência de funcionamento
- estado atual e próxima ação sugerida

**Mantra Operacional:** "Evoluir o que já existe antes de criar. Integrar antes de duplicar. Executar antes de explicar. Registar para nunca esquecer. Liberar a interface para continuidade."
