# utils/helpers.py
import re
import csv
import json
import time
import random
import string
import smtplib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Union, Optional, Tuple

from config.settings import (
    NOTIFICATION_EMAIL,
    NOTIFICATION_SMS,
    NOTIFICATION_ENABLED,
    DATA_DIR,
    SCREENSHOTS_DIR
)
from utils.logger import get_logger

logger = get_logger(__name__)

# ---- Génération de données aléatoires ----

def generate_random_string(length: int = 8) -> str:
    """
    Génère une chaîne de caractères aléatoire.
    
    Args:
        length: Longueur de la chaîne à générer
    
    Returns:
        str: Chaîne aléatoire
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_fake_email(domain: str = None) -> str:
    """
    Génère un email aléatoire.
    
    Args:
        domain: Domaine de l'email (par défaut, aléatoire parmi gmail.com, yahoo.com, outlook.com)
    
    Returns:
        str: Email généré
    """
    domains = ['gmail.com', 'yahoo.com', 'outlook.com'] if domain is None else [domain]
    username = generate_random_string(random.randint(6, 12)).lower()
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_fake_phone(country_code: str = "+33") -> str:
    """
    Génère un numéro de téléphone aléatoire.
    
    Args:
        country_code: Code pays du numéro
    
    Returns:
        str: Numéro de téléphone généré
    """
    number = ''.join(random.choices(string.digits, k=9))
    return f"{country_code}{number}"

def generate_fake_address() -> Dict[str, str]:
    """
    Génère une adresse aléatoire en France.
    
    Returns:
        Dict: Adresse générée avec rue, code postal, ville, etc.
    """
    street_numbers = list(range(1, 100))
    street_types = ['rue', 'avenue', 'boulevard', 'impasse', 'place']
    street_names = ['des Lilas', 'de Paris', 'Victor Hugo', 'Jean Jaurès', 'Pasteur']
    postal_codes = ['75001', '69001', '33000', '59000', '13001', '31000']
    cities = ['Paris', 'Lyon', 'Bordeaux', 'Lille', 'Marseille', 'Toulouse']
    
    return {
        'street_number': str(random.choice(street_numbers)),
        'street_type': random.choice(street_types),
        'street_name': random.choice(street_names),
        'postal_code': random.choice(postal_codes),
        'city': random.choice(cities),
        'country': 'France'
    }

def generate_fake_payment_card() -> Dict[str, str]:
    """
    Génère des informations de carte de paiement fictives.
    REMARQUE: À utiliser uniquement pour des tests - ne génère pas de numéros valides.
    
    Returns:
        Dict: Informations de carte générées
    """
    card_types = ['visa', 'mastercard', 'amex']
    expiry_months = [str(m).zfill(2) for m in range(1, 13)]
    current_year = datetime.now().year
    expiry_years = [str(current_year + i) for i in range(1, 6)]
    
    return {
        'type': random.choice(card_types),
        'number': ''.join(random.choices(string.digits, k=16)),
        'expiry_month': random.choice(expiry_months),
        'expiry_year': random.choice(expiry_years),
        'cvv': ''.join(random.choices(string.digits, k=3))
    }

# ---- Formatage et manipulation de dates ----

def format_date(date: Union[datetime, str], output_format: str = "%d/%m/%Y") -> str:
    """
    Formate une date selon le format spécifié.
    
    Args:
        date: Date à formater (datetime ou str)
        output_format: Format de sortie
    
    Returns:
        str: Date formatée
    """
    if isinstance(date, str):
        # Essaie de détecter le format d'entrée
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]:
            try:
                date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Format de date non reconnu: {date}")
    
    return date.strftime(output_format)

def add_days_to_date(date: Union[datetime, str], days: int, output_format: str = "%d/%m/%Y") -> str:
    """
    Ajoute un nombre de jours à une date.
    
    Args:
        date: Date initiale (datetime ou str)
        days: Nombre de jours à ajouter (négatif pour soustraire)
        output_format: Format de sortie
    
    Returns:
        str: Nouvelle date formatée
    """
    if isinstance(date, str):
        # Essaie de détecter le format d'entrée
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]:
            try:
                date = datetime.strptime(date, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Format de date non reconnu: {date}")
    
    new_date = date + timedelta(days=days)
    return new_date.strftime(output_format)

def get_current_date(output_format: str = "%d/%m/%Y") -> str:
    """
    Obtient la date actuelle dans le format spécifié.
    
    Args:
        output_format: Format de sortie
    
    Returns:
        str: Date actuelle formatée
    """
    return datetime.now().strftime(output_format)

# ---- Parseurs de prix et de devises ----

def parse_price(price_str: str) -> float:
    """
    Extrait un prix à partir d'une chaîne de caractères.
    Gère différents formats (1,234.56€, €1.234,56, etc.).
    
    Args:
        price_str: Chaîne contenant un prix
    
    Returns:
        float: Prix extrait
    """
    # Supprimer les espaces et les symboles de devise
    price_str = re.sub(r'[€$£\s]', '', price_str)
    
    # Détecter le format
    if ',' in price_str and '.' in price_str:
        # Format avec séparateur de milliers et décimal
        if price_str.index(',') < price_str.index('.'):
            # Format 1,234.56
            price_str = price_str.replace(',', '')
        else:
            # Format 1.234,56
            price_str = price_str.replace('.', '').replace(',', '.')
    elif ',' in price_str:
        # Si seule la virgule est présente, on considère que c'est le séparateur décimal
        price_str = price_str.replace(',', '.')
    
    # Extraire le nombre
    match = re.search(r'(\d+\.?\d*)', price_str)
    if match:
        return float(match.group(1))
    
    raise ValueError(f"Format de prix non reconnu: {price_str}")

def format_price(price: float, currency: str = "€", decimal_separator: str = ",", thousands_separator: str = " ") -> str:
    """
    Formate un prix selon les conventions locales.
    
    Args:
        price: Prix à formater
        currency: Symbole de devise
        decimal_separator: Séparateur décimal
        thousands_separator: Séparateur de milliers
    
    Returns:
        str: Prix formaté
    """
    # Formater le nombre avec séparateurs
    price_str = f"{price:,.2f}"
    
    # Remplacer les séparateurs selon les conventions locales
    if thousands_separator != ",":
        price_str = price_str.replace(",", "TEMP")
    
    if decimal_separator != ".":
        price_str = price_str.replace(".", decimal_separator)
    
    if thousands_separator != ",":
        price_str = price_str.replace("TEMP", thousands_separator)
    
    # Ajouter le symbole de devise
    return f"{price_str} {currency}"

# ---- Validation d'emails et de numéros de téléphone ----

def is_valid_email(email: str) -> bool:
    """
    Vérifie si un email est valide.
    
    Args:
        email: Email à vérifier
    
    Returns:
        bool: True si l'email est valide, False sinon
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str, country_code: str = "+33") -> bool:
    """
    Vérifie si un numéro de téléphone est valide.
    
    Args:
        phone: Numéro à vérifier
        country_code: Code pays attendu
    
    Returns:
        bool: True si le numéro est valide, False sinon
    """
    # Supprimer les espaces et caractères de formatage
    phone = re.sub(r'[\s\-\.\(\)]', '', phone)
    
    # Vérifier le format selon le pays
    if country_code == "+33":  # France
        pattern = r'^\+33[1-9]\d{8}$'
    elif country_code == "+1":  # USA/Canada
        pattern = r'^\+1\d{10}$'
    else:
        # Format générique
        pattern = r'^\+\d{1,4}\d{8,12}$'
    
    return bool(re.match(pattern, phone))

# ---- Gestion de fichiers CSV/JSON ----

def read_csv(filename: str, directory: Path = DATA_DIR) -> List[Dict[str, str]]:
    """
    Lit un fichier CSV et retourne son contenu.
    
    Args:
        filename: Nom du fichier CSV
        directory: Répertoire contenant le fichier
    
    Returns:
        List[Dict]: Liste de dictionnaires représentant les lignes du CSV
    """
    file_path = directory / filename
    logger.debug(f"Lecture du fichier CSV: {file_path}")
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier CSV {file_path}: {str(e)}")
        raise

def write_csv(data: List[Dict[str, Any]], filename: str, directory: Path = DATA_DIR) -> str:
    """
    Écrit des données dans un fichier CSV.
    
    Args:
        data: Données à écrire (liste de dictionnaires)
        filename: Nom du fichier CSV
        directory: Répertoire où écrire le fichier
    
    Returns:
        str: Chemin du fichier créé
    """
    file_path = directory / filename
    logger.debug(f"Écriture dans le fichier CSV: {file_path}")
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            if data:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        return str(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans le fichier CSV {file_path}: {str(e)}")
        raise

def read_json(filename: str, directory: Path = DATA_DIR) -> Union[Dict[str, Any], List[Any]]:
    """
    Lit un fichier JSON et retourne son contenu.
    
    Args:
        filename: Nom du fichier JSON
        directory: Répertoire contenant le fichier
    
    Returns:
        Dict ou List: Contenu du fichier JSON
    """
    file_path = directory / filename
    logger.debug(f"Lecture du fichier JSON: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier JSON {file_path}: {str(e)}")
        raise

def write_json(data: Union[Dict[str, Any], List[Any]], filename: str, directory: Path = DATA_DIR, indent: int = 4) -> str:
    """
    Écrit des données dans un fichier JSON.
    
    Args:
        data: Données à écrire
        filename: Nom du fichier JSON
        directory: Répertoire où écrire le fichier
        indent: Indentation pour le formatage du JSON
    
    Returns:
        str: Chemin du fichier créé
    """
    file_path = directory / filename
    logger.debug(f"Écriture dans le fichier JSON: {file_path}")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        return str(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans le fichier JSON {file_path}: {str(e)}")
        raise

# ---- Manipulation de chaînes de caractères ----

def clean_text(text: str) -> str:
    """
    Nettoie une chaîne de caractères (supprime les espaces multiples, caractères spéciaux, etc.).
    
    Args:
        text: Texte à nettoyer
    
    Returns:
        str: Texte nettoyé
    """
    # Supprimer les caractères de contrôle et les espaces multiples
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_numbers(text: str) -> List[float]:
    """
    Extrait tous les nombres d'une chaîne de caractères.
    
    Args:
        text: Texte contenant des nombres
    
    Returns:
        List[float]: Liste des nombres extraits
    """
    # Recherche les nombres décimaux (avec virgule ou point) ou entiers
    pattern = r'(\d+[.,]?\d*)'
    matches = re.findall(pattern, text)
    
    # Convertir en float
    return [float(match.replace(',', '.')) for match in matches]

# ---- Utilitaires réseau ----

def get_ip_info() -> Dict[str, Any]:
    """
    Obtient des informations sur l'adresse IP publique actuelle.
    
    Returns:
        Dict: Informations sur l'IP (adresse, pays, etc.)
    """
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Impossible d'obtenir les informations IP. Code: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations IP: {str(e)}")
        return {}

def check_connection(url: str = "https://www.google.com", timeout: int = 5) -> bool:
    """
    Vérifie si la connexion Internet est active.
    
    Args:
        url: URL à vérifier
        timeout: Délai d'attente en secondes
    
    Returns:
        bool: True si la connexion est active, False sinon
    """
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code < 400
    except Exception:
        return False

# ---- Gestion des notifications ----

def send_email_notification(subject: str, message: str, to_email: str = NOTIFICATION_EMAIL) -> bool:
    """
    Envoie une notification par email.
    
    Args:
        subject: Sujet de l'email
        message: Corps du message
        to_email: Destinataire
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    if not NOTIFICATION_ENABLED:
        logger.info("Notifications désactivées. Email non envoyé.")
        return False
    
    if not to_email:
        logger.warning("Adresse email de notification non configurée.")
        return False
    
    try:
        # Cette fonction nécessite une configuration supplémentaire pour fonctionner
        # avec un serveur SMTP spécifique. Voici un exemple avec Gmail:
        
        # Configuration de l'expéditeur
        from_email = "votre_email@gmail.com"
        password = "votre_mot_de_passe_app"  # Mot de passe d'application
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        
        # Envoi du message
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email de notification envoyé à {to_email}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

def send_sms_notification(message: str, to_number: str = NOTIFICATION_SMS) -> bool:
    """
    Envoie une notification par SMS (exemple avec Twilio).
    
    Args:
        message: Corps du message
        to_number: Numéro de téléphone du destinataire
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    if not NOTIFICATION_ENABLED:
        logger.info("Notifications désactivées. SMS non envoyé.")
        return False
    
    if not to_number:
        logger.warning("Numéro de téléphone pour notification non configuré.")
        return False
    
    # Cette fonction nécessite un service tiers comme Twilio pour fonctionner
    # Voici un exemple avec l'API Twilio:
    try:
        # Pour que cela fonctionne, vous devez installer le package twilio
        # pip install twilio
        
        # Décommenter et configurer si vous utilisez Twilio
        """
        from twilio.rest import Client
        
        # Configuration Twilio
        account_sid = 'votre_account_sid'
        auth_token = 'votre_auth_token'
        from_number = 'votre_numero_twilio'
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        logger.info(f"SMS de notification envoyé à {to_number}, SID: {message.sid}")
        """
        
        # Pour l'instant, simulons l'envoi
        logger.info(f"Simulation: SMS de notification envoyé à {to_number}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du SMS: {str(e)}")
        return False

# ---- Opérations sur le panier ----

def calculate_cart_total(items: List[Dict[str, Union[str, float, int]]]) -> Dict[str, float]:
    """
    Calcule le total d'un panier d'achat.
    
    Args:
        items: Liste des articles du panier avec prix et quantité
    
    Returns:
        Dict: Total du panier avec détails (sous-total, taxes, etc.)
    """
    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
    tax_rate = 0.20  # TVA à 20%
    taxes = subtotal * tax_rate
    total = subtotal + taxes
    
    return {
        'subtotal': round(subtotal, 2),
        'tax_rate': tax_rate,
        'taxes': round(taxes, 2),
        'total': round(total, 2)
    }

def verify_cart_items(expected_items: List[Dict[str, Any]], actual_items: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Vérifie si le contenu du panier correspond aux articles attendus.
    
    Args:
        expected_items: Articles attendus dans le panier
        actual_items: Articles réellement dans le panier
    
    Returns:
        Tuple[bool, List[str]]: (Résultat de la vérification, Liste des différences)
    """
    differences = []
    all_match = True
    
    # Vérifier que tous les articles attendus sont présents
    for expected in expected_items:
        found = False
        for actual in actual_items:
            if expected.get('id') == actual.get('id'):
                found = True
                
                # Vérifier la quantité
                if expected.get('quantity') != actual.get('quantity'):
                    all_match = False
                    differences.append(
                        f"Quantité incorrecte pour l'article {expected.get('name')}: "
                        f"attendue {expected.get('quantity')}, "
                        f"trouvée {actual.get('quantity')}"
                    )
                
                # Vérifier le prix
                if abs(expected.get('price', 0) - actual.get('price', 0)) > 0.01:
                    all_match = False
                    differences.append(
                        f"Prix incorrect pour l'article {expected.get('name')}: "
                        f"attendu {expected.get('price')}, "
                        f"trouvé {actual.get('price')}"
                    )
                
                break
        
        if not found:
            all_match = False
            differences.append(f"Article {expected.get('name')} non trouvé dans le panier")
    
    # Vérifier qu'il n'y a pas d'articles supplémentaires
    for actual in actual_items:
        found = any(expected.get('id') == actual.get('id') for expected in expected_items)
        if not found:
            all_match = False
            differences.append(f"Article supplémentaire trouvé dans le panier: {actual.get('name')}")
    
    return all_match, differences

# ---- Utilitaires de screenshot améliorés ----

def take_full_page_screenshot(page, filename: str = None, directory: Path = SCREENSHOTS_DIR) -> str:
    """
    Prend une capture d'écran de la page entière.
    
    Args:
        page: Instance de Page Playwright
        filename: Nom du fichier (sans extension)
        directory: Répertoire où sauvegarder la capture
    
    Returns:
        str: Chemin vers la capture d'écran
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename if filename else f"full_page_{timestamp}"
    filepath = directory / f"{filename}.png"
    
    logger.debug(f"Capture d'écran de la page entière: {filepath}")
    page.screenshot(path=str(filepath), full_page=True)
    
    return str(filepath)

def take_element_screenshot(page, selector: str, filename: str = None, directory: Path = SCREENSHOTS_DIR) -> str:
    """
    Prend une capture d'écran d'un élément spécifique.
    
    Args:
        page: Instance de Page Playwright
        selector: Sélecteur CSS ou XPath de l'élément
        filename: Nom du fichier (sans extension)
        directory: Répertoire où sauvegarder la capture
    
    Returns:
        str: Chemin vers la capture d'écran
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename if filename else f"element_{timestamp}"
    filepath = directory / f"{filename}.png"
    
    logger.debug(f"Capture d'écran de l'élément {selector}: {filepath}")
    element = page.locator(selector)
    element.screenshot(path=str(filepath))
    
    return str(filepath)

# ---- Utilitaires divers ----

def wait_random_time(min_seconds: float = 0.15, max_seconds: float = 2.0) -> None:
    """
    Attend un temps aléatoire pour simuler un comportement humain.
    
    Args:
        min_seconds: Durée minimale en secondes
        max_seconds: Durée maximale en secondes
    """
    duration = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Attente de {duration:.2f} secondes")
    time.sleep(duration)

def humanize_text_input(text: str, error_rate: float = 0.05, delay_range: Tuple[float, float] = (0.05, 0.2)) -> Tuple[str, List[float]]:
    """
    Simule une saisie humaine avec erreurs et délais variables.
    
    Args:
        text: Texte à "humaniser"
        error_rate: Taux d'erreur à simuler (probabilité de frappe erronée)
        delay_range: Plage de délai entre les frappes (en secondes)
    
    Returns:
        Tuple[str, List[float]]: (Texte avec erreurs, Liste des délais entre frappes)
    """
    keys = list(text)
    delays = []
    result = []
    
    for i, char in enumerate(keys):
        # Simuler une erreur de frappe
        if random.random() < error_rate:
            # Ajouter un caractère erroné
            keyboard_neighbors = {
                'a': 'qszw', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx', 'e': 'wrsdf',
                'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb', 'i': 'uojk', 'j': 'huiknm',
                'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
                'p': 'ol', 'q': 'asw', 'r': 'edft', 's': 'qawedxz', 't': 'rfgy',
                'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
                'z': 'asx', '0': '9', '1': '2', '2': '13', '3': '24', '4': '35',
                '5': '46', '6': '57', '7': '68', '8': '79', '9': '80'
            }
            
            if char.lower() in keyboard_neighbors:
                error_char = random.choice(keyboard_neighbors[char.lower()])
                if char.isupper():
                    error_char = error_char.upper()
                result.append(error_char)
                
                # Simuler un backspace après un court délai
                delays.append(random.uniform(0.1, 0.3))
                result.append('\b')  # Backspace
            
        # Ajouter le caractère correct
        result.append(char)
        
        # Ajouter un délai variable entre les frappes
        delays.append(random.uniform(delay_range[0], delay_range[1]))
        
        # Parfois ajouter une pause plus longue (comme si on réfléchissait)
        if random.random() < 0.1:
            delays[-1] += random.uniform(0.3, 1.0)
    
    return ''.join(result), delays