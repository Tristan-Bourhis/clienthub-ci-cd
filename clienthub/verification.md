# Vérifications réalisées le 1er octobre 2026

## API autonome

Image construite puis exécutée avec `docker run`, avant Compose.
`GET http://127.0.0.1:5000/health` : HTTP 200, `{"status":"ok"}`.
Le conteneur `clienthub-api-standalone` a ensuite été arrêté.

## Déploiement final

```text
NAME              STATUS                PORTS
clienthub-api-1    Up (healthy)          127.0.0.1:5000->5000/tcp
clienthub-db-1     Up (healthy)          3306/tcp, 33060/tcp (non publiés)
clienthub-web-1    Up                    127.0.0.1:8080->80/tcp
```

Les trois services sont sur le réseau bridge dédié `clienthub_internal`.
La base n'a aucun port publié. Ce réseau n'utilise pas l'option Docker
`internal: true`, qui empêchait ici la publication des ports web/API.
L'isolation retenue est un réseau dédié et l'absence de publication MySQL ;
elle ne constitue pas un filtrage absolu des connexions depuis l'hôte Linux.

## Initialisation automatique

Le journal du premier démarrage MySQL contient :

```text
[Entrypoint]: /usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/01-init.sql
```

Le fichier SQL final a également été testé sur un volume temporaire vierge,
avec un projet Compose distinct `clienthub-initcheck`. Résultat :

```text
id  name           HEX(name)
1   Alice Martin   416C696365204D617274696E
2   Bob Dupont     426F62204475706F6E74
3   Chloé Bernard  43686C6FC3A9204265726E617264
```

L'encodage UTF-8 est explicite dans `init.sql` et dans la connexion PyMySQL.

## Preuve de lecture MySQL et persistance

Un quatrième client, `Client preuve persistance`, a été inséré directement
en SQL. Les conteneurs et le réseau ClientHub ont ensuite été supprimés avec
`docker compose down` puis recréés avec `docker compose up -d --wait`, sans
supprimer le volume. Le quatrième client était toujours présent.

Ce client a été renommé directement dans MySQL. La requête HTTP suivante
a retourné les données modifiées sans reconstruire les données de l'API :

```json
[
  {"id": 1, "name": "Alice Martin"},
  {"id": 2, "name": "Bob Dupont"},
  {"id": 3, "name": "Chloé Bernard"},
  {"id": 4, "name": "Client modifié dans MySQL"}
]
```

Le quatrième client est conservé pour rendre la démonstration consultable.
Les trois premiers viennent d'`init.sql`.

## Tests automatisés

Commande : `python3 tests/check_http.py`.

```text
test_clients_from_database ... ok
test_health ... ok
test_portal ... ok
test_unknown_route ... ok
Ran 4 tests
OK
```

Le portail Nginx a aussi été ouvert dans le navigateur. La vérification
automatisée a contrôlé HTTP 200 et la présence du texte ClientHub.
