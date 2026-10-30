# Submissions | Week 07

[Português](README.md) · English

This is where the submissions from people who did Week 07 live. The list with each person's project is in the [main README](../README.en.md#class-submissions).

## How to submit

1. **Fork** this repository (the *Fork* button, in the top right corner).
2. In your fork, create the folder `entregas/First Last/`, with your first and last name.
3. Put your files inside it, following the structure below.
4. Commit and push to your fork.
5. Open a **Pull Request** to this repository and fill in the template that shows up.

After the merge, your submission is added to the table in the main README.

> **Prefer to keep the project in your own repository?** That works too. Send the link on Discord or [open an issue](../../../issues/new) here with the link to the week's folder, and it goes into the table the same way. Just put some care into the `README.md`, as explained below, because it is the first thing people will see.

## Expected structure

```text
entregas/First Last/
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

- Do not send the `.venv` folder, `__pycache__` files or a `.env` file.
- Do not send the `dados/` (the database) and `logs/` folders: they are the output of runs. Your `.gitignore` should leave them out.
- File names in lowercase, separated by hyphens or underscores and **with an extension**.
- Only change files inside your own folder.

## What your README needs to have

The `README.md` in your folder is the cover of your project. Whoever opens it needs to understand, without you explaining:

- **the project name** as the title;
- **one sentence** saying what the pipeline collects and where it stores it;
- **how to install** (`pip install -r requirements.txt`), **how to start the training site**, **how to run** (`python -m coleta`) and **how to test** (`pytest`);
- **the program's exit codes** and where the database and the log are;
- **what was tested and what was not**, as `docs-eng/deliverable.md` asks.

## Already submitted in another week?

Repeating the same project is fine. Just remember that each week is a complete folder: send the updated version here too.
