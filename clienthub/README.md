# ClientHub

## Intégration continue

Le workflow `../.github/workflows/clienthub-ci.yml` s'exécute à chaque push,
sur les pull requests et manuellement depuis GitHub Actions. Il construit
les images, initialise une base MySQL vierge, attend la disponibilité des
services et lance les quatre tests HTTP. Les logs sont affichés et les
conteneurs et volumes CI sont supprimés même si un test échoue.
Les identifiants éphémères de test sont définis dans le workflow ; aucun
fichier `.env` personnel ni secret GitHub n'est nécessaire.

Application locale composée d'une API Flask, d'un portail Nginx et de MySQL 8.4.

## Démarrer

Depuis le dossier `clienthub`, si `.env` n'existe pas encore, copier
`.env.example` vers `.env`. Ses mots de passe sont destinés à la démonstration
locale. Puis lancer :

```bash
docker compose up -d --build --wait
docker compose ps
python3 tests/check_http.py
```

- Portail : http://localhost:8080/
- Santé de l'API : http://localhost:5000/health
- Clients MySQL : http://localhost:5000/clients

Le Dockerfile installe Python, Flask, PyMySQL et Gunicorn, copie `app.py`, expose
5000 et démarre l'API avec Gunicorn. Pour tester l'API seule, avant Compose :

```bash
docker build -t clienthub-api:local .
docker run -d --name clienthub-api-standalone -p 127.0.0.1:5000:5000 clienthub-api:local
curl http://localhost:5000/health
docker stop clienthub-api-standalone
```

Ce test a déjà été effectué : le conteneur autonome existe et est arrêté.
Pour le réutiliser, utiliser `docker start clienthub-api-standalone` quand
Compose est arrêté afin de libérer le port 5000.

## Organisation

Les trois services partagent le réseau bridge dédié `clienthub_internal`.
Seuls Nginx et l'API publient des ports, sur l'interface locale.
MySQL est joignable par l'API sous le nom `db`, sur le port interne 3306.

Nginx sert `site/index.html` via un montage en lecture seule dans
`/usr/share/nginx/html`. Les données MySQL résident dans le volume nommé
`clienthub_mysql_data`. `init.sql`, monté dans `/docker-entrypoint-initdb.d/`,
crée la table et insère trois clients au premier démarrage sur un volume vide.

Le healthcheck MySQL exécute une requête sur la table avec l'utilisateur
applicatif. `depends_on: condition: service_healthy` fait attendre l'API jusqu'à
ce que cette requête réussisse. Un simple `depends_on` sans cette condition
ne garantirait que l'ordre de démarrage.

`/health` vérifie la disponibilité HTTP de l'API. `/clients` ouvre une connexion
MySQL à chaque requête avec `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` et
`DB_PASSWORD`, crée la table si nécessaire puis effectue un `SELECT` réel.
Si MySQL est indisponible, cet endpoint répond 503.

## Vérifier les données

```bash
docker compose exec db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysql --default-character-set=utf8mb4 -u"$MYSQL_USER" "$MYSQL_DATABASE" -e "SELECT * FROM clients;"'
curl http://localhost:5000/clients
docker compose logs --tail=30 api db
```

Les tests HTTP automatisés couvrent `/health`, les trois clients initiaux,
la page Nginx et une route inexistante. `verification.md` consigne les essais
réels, y compris la modification SQL visible via l'API et la persistance.

## Arrêter et relancer

```bash
docker compose stop
docker compose up -d --wait
```

`restart: "no"` évite le redémarrage automatique lors du lancement de Docker.
Les données survivent aux arrêts et à la recréation des conteneurs.
`init.sql` ne se rejoue pas sur un volume déjà initialisé : modifier ce fichier
ne met donc pas automatiquement à jour les données existantes.
Ne pas utiliser `docker compose down -v` si les données doivent être conservées.
