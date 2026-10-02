# ClientHub — CI/CD

Projet pédagogique d’intégration et de déploiement continus : application
ClientHub (Flask, Nginx et MySQL), tests automatisés, images Docker
et déploiement Azure avec GitHub Actions.

Voir [la documentation ClientHub](clienthub/README.md) pour lancer l’application.

## Tests unitaires et typage Python

La pipeline `.github/workflows/github-actions-demo.yml` se lance à chaque push
et peut également être lancée manuellement depuis GitHub Actions. Elle récupère
le code, installe Python 3.12, pytest et mypy, vérifie le typage, puis lance les
tests unitaires. Si mypy échoue, les tests ne sont pas exécutés.

## Exécution locale

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m mypy --strict lib.py test_lib.py
python -m pytest -v test_lib.py
```

`test_verage` contient trois assertions, dont une moyenne non entière.
`average([])` lève une exception `ValueError`.

## Démonstrations sur la branche exercice-python-ci

- `0227010` : code correct, mypy et pytest passent.
  [Exécution GitHub Actions](https://github.com/Tristan-Bourhis/clienthub-ci-cd/actions/runs/36709544390)
- `e6c2867` : remplacement de `/` par `//` dans `average` ; la moyenne de
  `[1, 2]` vaut alors `1` au lieu de `1.5`, ce qui fait échouer pytest.
  [Exécution GitHub Actions](https://github.com/Tristan-Bourhis/clienthub-ci-cd/actions/runs/36709615103)
- `ef82f3c` : moyenne corrigée et appel `add("2", 2)` ; mypy signale
  `Argument 1 to "add" has incompatible type "str"; expected "int"`.
  [Exécution GitHub Actions](https://github.com/Tristan-Bourhis/clienthub-ci-cd/actions/runs/36709621718)

La version finale rétablit `add(2, 2)` pour laisser la branche fonctionnelle.
Les versions volontairement incorrectes restent consultables dans l'historique.
