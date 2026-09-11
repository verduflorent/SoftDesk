# SoftDesk Support API

SoftDesk est une API REST de suivi de problèmes développée avec Django et Django REST Framework.

Elle permet à des utilisateurs authentifiés de créer des projets, gérer leurs contributeurs, créer des issues, les assigner à des contributeurs du projet et ajouter des commentaires.

## Stack

- Python 3.14+
- Django 6.1
- Django REST Framework 3.18
- SimpleJWT
- Poetry
- SQLite pour le développement

## Installation

### 1. Cloner le repository

```powershell
git clone https://github.com/verduflorent/SoftDesk.git
cd SoftDesk
```

### 2. Installer Poetry

Si Poetry n'est pas déjà disponible :

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 3. Installer les dépendances

```powershell
poetry install
```

### 4. Appliquer les migrations

```powershell
poetry run python manage.py migrate
```

### 5. Lancer le serveur

```powershell
poetry run python manage.py runserver
```

L'API est alors disponible sur :

```text
http://127.0.0.1:8000/api/
```

## Secret Django

En développement, une clé aléatoire est générée automatiquement si `DJANGO_SECRET_KEY` n'est pas définie.

Pour fournir explicitement une clé :

```powershell
$env:DJANGO_SECRET_KEY="votre-cle-secrete"
```

Aucun secret réel n'est stocké dans le repository.

## Authentification JWT

Obtenir un token :

```text
POST /api/token/
```

Corps JSON :

```json
{
  "username": "mon_utilisateur",
  "password": "mon_mot_de_passe"
}
```

Renouveler un access token :

```text
POST /api/token/refresh/
```

Pour appeler une route protégée :

```text
Authorization: Bearer <access_token>
```

## Endpoints principaux

```text
/api/users/
/api/projects/
/api/contributors/
/api/issues/
/api/comments/
/api/token/
/api/token/refresh/
```

Les commentaires sont référencés via leur UUID.

## Règles métier principales

- le créateur d'un projet devient automatiquement son auteur et son premier contributeur ;
- seuls les contributeurs d'un projet peuvent accéder à ses ressources ;
- seul l'auteur d'une ressource peut la modifier ou la supprimer ;
- une issue ne peut être assignée qu'à un contributeur de son projet ;
- seuls les contributeurs du projet peuvent créer des issues et commentaires liés à ce projet ;
- les listes sont paginées par groupes de 10 éléments ;
- les accès ORM aux relations principales sont optimisés avec `select_related()`.

## RGPD

L'API permet à un utilisateur de :

- consulter ses propres données ;
- les rectifier ;
- modifier ses consentements (`can_be_contacted`, `can_data_be_shared`) ;
- supprimer son compte ;
- s'inscrire uniquement s'il respecte l'âge minimum de 15 ans.

## Tests

Lancer la suite de tests automatisés :

```powershell
poetry run python manage.py test
```

Vérifier la configuration Django :

```powershell
poetry run python manage.py check
```

Les tests couvrent notamment l'isolation des projets, les permissions auteur/contributeur, l'assignation des issues et les commentaires.

## Structure simplifiée

```text
User
  │
Contributor
  │
Project
  │
Issue
  │
Comment
```

## Données locales

Les fichiers locaux et sensibles suivants sont ignorés par Git :

```text
.env
db.sqlite3
.venv/
__pycache__/
```

## Repository

https://github.com/verduflorent/SoftDesk
