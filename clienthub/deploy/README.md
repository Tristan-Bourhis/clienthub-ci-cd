# Déploiement automatique Azure — port 8007

Chaque push sur `main` déclenche, dans l'ordre :

1. **Unit** : installation des dépendances et `python -m unittest discover -s tests -p 'test_*.py' -v`.
2. **E2E** : MySQL temporaire initialisé par SQL, lancement de Gunicorn depuis
   les sources et `python tests/run_e2e.py`. Les requêtes HTTP réelles vérifient
   `/health`, `/who`, `/clients` (lecture MySQL), le portail et une 404.
3. **Build/push** : seulement si les deux jobs réussissent, construction de
   l'image, smoke test `/health`, login Docker Hub et push `latest` + SHA complet.
4. **Deploy** : transfert SSH, pull du tag SHA, `docker compose up -d --wait`,
   vérification HTTP locale puis publique et capture du portail avec Chromium.

Les pull requests et la branche de préparation `clienthub-azure` exécutent
les tests et le build sans publier ni déployer. Aucun clic d'approbation ni
commande manuelle n'est nécessaire après un push sur `main`, une fois les
prérequis ci-dessous configurés.

## Configuration initiale de la VM et de GitHub

La VM doit disposer de Docker Engine, du plugin Compose, de curl et openssl.
L'utilisateur SSH doit pouvoir utiliser Docker sans sudo interactif. Le port
22 doit être accessible aux runners GitHub, et le port TCP 8007 doit être ouvert
dans le NSG Azure et le pare-feu de la VM. Le port MySQL n'est pas publié.

Secrets GitHub requis (Settings → Secrets and variables → Actions) :

| Secret | Contenu |
| --- | --- |
| `DOCKERHUB_USERNAME` | Compte Docker Hub |
| `DOCKERHUB_TOKEN` | Jeton autorisé à publier l'image |
| `DOCKERHUB_IMAGE` | Nom d'image, simple ou `compte/image` (variable également acceptée) |
| `AZURE_HOST` | IP publique ou nom DNS de la VM, sans protocole ni port |
| `AZURE_USER` | Utilisateur SSH |
| `AZURE_SSH_KEY` | Clé privée SSH dédiée, sans passphrase interactive |
| `AZURE_KNOWN_HOSTS` | Ligne known_hosts de la VM dont l'empreinte a été vérifiée auprès de l'administrateur |

La clé publique correspondante doit être autorisée sur la VM. La vérification
de la clé hôte est stricte ; ne pas accepter une empreinte inconnue à l'aveugle.
Les secrets ne sont pas committés. Les anciens mots de passe d'exemple présents
dans l'historique étaient uniquement des valeurs locales de démonstration ;
ils ne sont pas utilisés sur Azure. Les mots de passe MySQL Azure sont générés
au premier déploiement et conservés dans `~/clienthub-8007/.env` (permissions 600).

## Idempotence et accès

Le projet Compose se nomme toujours `clienthub-8007`. Relancer un déploiement
utilise les mêmes services et le même volume, sans multiplier les conteneurs.
L'image déployée est celle du SHA testé, jamais un `latest` potentiellement déplacé.
Flask sert aussi le portail pour fournir l'application via un seul port attribué.
Le Compose local à trois services conserve son serveur Nginx.

- `http://IP_PUBLIQUE:8007/` : portail ClientHub
- `http://IP_PUBLIQUE:8007/health` : HTTP 200 et `{"status":"ok"}`
- `http://IP_PUBLIQUE:8007/who` : identité
- `http://IP_PUBLIQUE:8007/clients` : clients MySQL

La capture est conservée comme artefact `clienthub-azure-<SHA>` dans GitHub Actions.
Elle n'est produite qu'après un vrai déploiement et des vérifications réussies.
Un redéploiement Compose peut entraîner une brève interruption ; il ne s'agit
pas d'une architecture garantissant le zéro downtime.
