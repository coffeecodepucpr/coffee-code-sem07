# Entregas | Semana 07

Português · [English](README.en.md)

Aqui ficam as entregas de quem fez a Semana 07. A lista com o projeto de cada pessoa está no [README principal](../README.md#entregas-da-turma).

## Como entregar

1. Faça um **fork** deste repositório (botão *Fork*, no canto superior direito).
2. No seu fork, crie a pasta `entregas/Nome Sobrenome/`, com o seu nome e sobrenome.
3. Coloque seus arquivos dentro dela, seguindo a estrutura abaixo.
4. Faça commit e push no seu fork.
5. Abra um **Pull Request** para este repositório e preencha o modelo que aparece.

Depois do merge, a sua entrega entra na tabela do README principal.

> **Prefere manter o projeto no seu próprio repositório?** Também vale. Mande o link no Discord ou [abra uma issue](../../../issues/new) aqui com o link da pasta da semana, e ele entra na tabela do mesmo jeito. Só capriche no `README.md`, como explicado abaixo, porque é ele que vai aparecer primeiro.

## Estrutura esperada

```text
entregas/Nome Sobrenome/
└── pipeline-coleta/
    ├── coleta/
    │   ├── __init__.py
    │   ├── __main__.py
    │   └── ...
    ├── tests/
    ├── requirements.txt
    ├── .gitignore
    └── README.md
```

- Não envie a pasta `.venv`, arquivos `__pycache__` nem um arquivo `.env`.
- Não envie as pastas `dados/` (o banco) e `logs/`: elas são resultado das execuções. O `.gitignore` deve deixá-las de fora.
- Nomes de arquivo em minúsculas, separados por hífen ou sublinhado e **com extensão**.
- Altere só arquivos dentro da sua pasta.

## O que o seu README precisa ter

O `README.md` da sua pasta é a capa do seu projeto. Quem abrir precisa entender, sem você explicar:

- **o nome do projeto** como título;
- **uma frase** dizendo o que o pipeline coleta e onde guarda;
- **como instalar** (`pip install -r requirements.txt`), **como ligar o site de treino**, **como rodar** (`python -m coleta`) e **como testar** (`pytest`);
- **os códigos de saída** do programa e onde ficam o banco e o log;
- **o que foi testado e o que não foi**, como pede o `docs/entregavel.md`.

## Já entregou em outra semana?

Sem problema repetir o mesmo projeto. Só lembre que cada semana é uma pasta completa: envie a versão atualizada dele aqui também.
