# Automation d'Achats en Ligne avec Playwright

Un framework d'automatisation pour effectuer des achats en ligne sur différents sites web en utilisant Playwright et Python.

## Structure du Projet

```
automation_achats/
│
├── websites/
│   ├── site1/
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── base_page.py
│   │   │   ├── login_page.py
│   │   │   ├── search_page.py
│   │   │   ├── product_page.py
│   │   │   ├── cart_page.py
│   │   │   └── checkout_page.py
│   │   └── config.py  # Configuration spécifique au site1
│   │
│   ├── site2/
│   │   ├── __init__.py
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── base_page.py
│   │   │   └── ...
│   │   └── config.py
│   │
│   └── common/
│       ├── __init__.py
│       └── base_page.py  # Fonctionnalités communes à tous les sites
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── credentials.py
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
│
├── data/
│   ├── products.json
│   └── test_data.json
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_login.py
│   └── test_checkout.py
│
├── scripts/
│   ├── __init__.py
│   └── run_purchase.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Prérequis

- Python 3.8 ou supérieur
- Un environnement virtuel (recommandé)

## Installation


1. Créer et activer un environnement virtuel :
```bash
python -m venv env
source env/bin/activate  # Sous Linux/Mac
# ou
env\Scripts\activate     # Sous Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
Créer un fichier `.env` à la racine du projet avec le contenu suivant :
```
SENTRY_DSN=votre_dsn_sentry
ENVIRONMENT=development
```

## Usage

### Exécuter un achat automatisé

```bash
python -m scripts.run_purchase --site site1 --product product_id
```

### Exécuter les tests

```bash
pytest
```

## Plan de Développement

### Phase 1 : Mise en place de l'environnement et structure de base
1. Créer la structure de dossiers du projet
2. Configurer l'environnement virtuel Python
3. Créer et installer le fichier requirements.txt
4. Configurer le système de journalisation avec Sentry

### Phase 2 : Développer les composants fondamentaux
1. Créer le module de configuration (variables d'environnement, paramètres)
2. Développer la classe BasePage commune
3. Mettre en place les utilitaires de base (captures d'écran, helpers)

### Phase 3 : Implémenter le premier site
1. Choisir le site le plus simple/prioritaire pour commencer
2. Analyser la structure du site et identifier les sélecteurs clés
3. Implémenter les classes de pages spécifiques au site (login, search, product, cart, checkout)
4. Créer un script simple pour tester chaque page individuellement

### Phase 4 : Développer le flux d'achat complet
1. Créer le script principal qui orchestre le flux d'achat de bout en bout
2. Implémenter la gestion des erreurs et les mécanismes de réessai
3. Ajouter des points de journalisation stratégiques avec Sentry
4. Tester le flux complet en mode non-headless (visible) pour vérification

### Phase 5 : Ajouter des sites supplémentaires
1. Suivre le même modèle pour implémenter d'autres sites
2. Refactoriser et extraire les fonctionnalités communes si nécessaire
3. Créer une factory pour instancier le bon site en fonction des paramètres

### Phase 6 : Tests et robustesse
1. Développer des tests unitaires et d'intégration
2. Améliorer la gestion des erreurs et des cas particuliers
3. Ajouter des timeouts et des attentes conditionnelles adaptatives

### Phase 7 : Raffinement et automatisation
1. Configurer des exécutions programmées (cron, etc.)
2. Ajouter des notifications (email, SMS) sur succès/échec
3. Créer des rapports d'exécution et des statistiques

## Journalisation avec Sentry

Le projet utilise Sentry pour la journalisation des erreurs et le suivi des performances. Pour configurer Sentry :

1. Créez un compte sur [Sentry](https://sentry.io/) si vous n'en avez pas déjà un
2. Créez un nouveau projet pour cette application
3. Récupérez la DSN fournie par Sentry
4. Ajoutez cette DSN dans votre fichier `.env`

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.