# ClientHub

## Intégration continue

Le workflow `../.github/workflows/clienthub-ci.yml` enchaîne quatre jobs :
tests unitaires → tests E2E HTTP avec MySQL → build/push Docker Hub →
déploiement SSH sur Azure au port **8007**, suivi d'un contrôle public et
d'une capture du portail. Le build n'a lieu qu'après réussite des deux suites.

Sur `main` uniquement (hors pull request), il se connecte à Docker Hub et
publie cette même image sous les tags `latest` et le SHA complet du commit.
La branche de préparation `clienthub-azure` et les pull requests vers `main`
testent l'application sans publier ni déployer. Les logs sont
affichés et les ressources CI sont nettoyées même en cas d'échec.

Configurer dans GitHub, Settings → Secrets and variables → Actions :

- Secret `DOCKERHUB_USERNAME` : identifiant Docker Hub.
- Secret `DOCKERHUB_TOKEN` : jeton Docker Hub avec droit d'écriture.
- Variable ou secret `DOCKERHUB_IMAGE` : nom complet, par exemple `moncompte/clienthub`.

Un nom simple comme `clienthub` est également accepté : le workflow ajoute
automatiquement le préfixe `DOCKERHUB_USERNAME/`.

Créer le dépôt correspondant dans Docker Hub. Ne jamais commiter le jeton.
Sur `main`, des paramètres manquants font explicitement échouer la publication.
Les mots de passe de la base de test sont générés à chaque exécution ; aucun
fichier `.env` personnel n'est nécessaire.

Voir [le guide Azure](deploy/README.md) pour les secrets SSH, les prérequis VM,
l'idempotence et la récupération de la capture. Le déploiement Azure reste
à vérifier après configuration des secrets ; aucune VM n'a encore été déployée.

Application locale composée d'une API Flask, d'un portail Nginx et de MySQL 8.4.

## Démarrer

Depuis le dossier `clienthub`, si `.env` n'existe pas encore, copier
`.env.example` vers `.env` et remplacer les valeurs `CHANGE_ME` par des mots
de passe aléatoires. Puis lancer :

```bash
docker compose up -d --build --wait
docker compose ps
python3 tests/check_http.py
```

- Portail : http://localhost:8080/
- Santé de l'API : http://localhost:5000/health
- Identité : http://localhost:5000/who (texte `Tristan Bourhis`, HTTP 200)
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

Les tests HTTP automatisés couvrent `/who`, `/health`, les trois clients initiaux,
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
