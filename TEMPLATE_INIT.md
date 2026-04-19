# Template de Inicialização

## 1. Criar um novo projeto

```bash
cp -R ruptur-farm-framework meu-projeto
cd meu-projeto
```

Se estiver usando este repositório como template, clone ou copie a pasta e renomeie o diretório conforme o projeto.

## 2. Rodar o bootstrap

```bash
bash scripts/ruptur.sh init
```

Esse comando:
- cria `.env` a partir de `.env.example` se necessário
- garante diretórios runtime
- inicializa log e estado base

## 3. Definir variáveis do ambiente

Edite `.env`:

```env
RUPTUR_HOME=./
RUPTUR_ENV=local
RUPTUR_STATE_PATH=./state
RUPTUR_MODE=STANDARD
```

## 4. Personalizar o projeto

Se quiser declarar a identidade do projeto, copie o template:

```bash
cp templates/project.yaml.tpl project.yaml
```

Depois substitua os placeholders:

- `{{PROJECT_NAME}}`
- `{{PROJECT_SLUG}}`
- `{{PROJECT_TYPE}}`
- `{{OWNER}}`
- `{{DATE_CREATED}}`
- `{{STACK}}`
- `{{ENV}}`

## 5. Criar a primeira task

Copie o template:

```bash
cp templates/task.json.tpl tasks/minha-primeira-task.json
```

Preencha os campos e mantenha o contrato definido em `contracts/task.schema.json`.

## 6. Executar a primeira task

```bash
bash scripts/ruptur.sh run tasks/minha-primeira-task.json STANDARD
```

## 7. Validar a execução

Confira:
- `kernel/state.json`
- `registry/runs/`
- `logs/execution.log`

Antes de executar de verdade, você também pode validar a task:

```bash
bash scripts/ruptur.sh validate tasks/minha-primeira-task.json STANDARD
```

E verificar a saúde do ambiente:

```bash
bash scripts/ruptur.sh doctor
```

## 8. Limpar runtime efêmero

```bash
bash scripts/ruptur.sh clean
```

Esse comando preserva `kernel/state.json`, `registry/runs/` e `logs/execution.log`.

## 9. Resetar artefatos operacionais

```bash
bash scripts/ruptur.sh reset
```

Use `reset` quando quiser limpar runtime, registry, logs e voltar o state ao baseline.

Esse fluxo não depende de integrações externas para o uso básico.
