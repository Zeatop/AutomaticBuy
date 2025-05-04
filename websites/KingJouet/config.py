# websites/KingJouet/config.py
import os
from pathlib import Path

# URLs principales
BASE_URL = "https://www.king-jouet.com"
LOGIN_URL = f"{BASE_URL}/exec/login.aspx?ReturnUrl=%2fmy%2f"
CART_URL = f"{BASE_URL}/exec/panier.aspx"

# Sélecteurs CSS pour les éléments importants du site
SELECTORS = {
    # Cookies et popups
    "cookie_accept_button": "#onetrust-accept-btn-handler",
    "popup_close_button": ".popup-close",
    
    # Navigation
    "search_input": "#algoliaSearch",
    "search_button": ".btn.btn-orange.py-3.w-full.my-2.mx-auto.z-110",
    
    # Page d'accueil
    "logo": "#logo_header",
    "main_menu": "#logo_header",
    
    # Page de recherche
    "product_items": ".ais-Hits-list.list-articles",
    "product_name": ".product-libelle",
    "product_price_euros": ".font-bold.text-xl.md:text-2xl.text-[#dd1e35]",
    "product_price_cents": ".cents",
    "product_availability": ".dispo.text-xs.text-kj-green.text-dispo.hover:text-zinc-400",
    "sort_dropdown": "#orderBySelect",
    
    # Page produit
    "product_title": ".product-name h1",
    "product_price_detail_euros": ".prix.text-2xl.lg:text-4xl.font-bold.text-[#dd1e35]",
    "product_price_detail_cents": ".cents",
    "add_to_cart_preco_button": "#addToCartPrecoBtn",
    "add_to_cart_button": "#addToCartWebBtn",
    
    
    # Panier
    # On pourrait ne regarder que les cart_item plutôt que de s'embêter à séparer les préco et non préco
    "cart_items_available": ".relative divide-y", # Le premier sont les produits disponibles
    "cart_items_preco": ".relative divide-y", # Le deuxième sont les produits en précommande
    "cart_item": ".panier-article-row border-b",
    # On ne peut modifier et voir la quantité que dans le panier
    "quantity_input": ".px-2",
    "remove_item": "btn btn-circle p-4 bg-neutral-200 border-none font-semibold btn-process", # Le premier sert à remove un item
    "add_remove_item": "btn btn-circle p-4 bg-neutral-200 border-none font-semibold btn-process", # Le second sert à ajouter un item
    "cart_total": ".attribut-value.text-right.block.font-bold.text-lg.md:text-xl",
    "proceed_to_checkout": "#btn_confirmation_pc",
    # Impossible de vider le panier en un clic
    "empty_cart": ".text-sm.underline.cursor-pointer",
    
    # Connexion
    "account-button": ".kj-icon-compte1.text-3xl.lg:text-4xl",
    "email_input": "#login-email-input",
    "password_input": "#login-password-input",
    "login_button": ".btn.btn-orange.btn-process.w-1/2.ml-2",
    "create_account_button": ".create-account",
    
    # Checkout
    # Même classes pour toutes les méthodes de livraison
    "delivery_options": ".relative.w-fulls",
    "card_owner": "#cardHolderName",
    "card_number": "#encryptedCardNumber",
    "card_expiration": "#encryptedExpiryDate",
    "card_security_code": "#encryptedSecurityCode",
    "place_order_button": "#btn_confirmation"
}

# Temporisations spécifiques (en millisecondes)
TIMEOUTS = {
    "page_load": 30000,
    "search_results": 10000,
    "add_to_cart": 5000,
    "checkout_step": 15000
}

# Paramètres de navigation
VIEWPORT_SIZE = {
    "width": 1280,
    "height": 800
}

# Agent utilisateur à utiliser (simule un navigateur standard)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Délais entre les actions pour simuler un comportement humain (en secondes)
HUMAN_DELAYS = {
    "min": 1.0,
    "max": 3.0,
    "typing_min": 0.05,
    "typing_max": 0.15
}

# Informations de test pour le checkout
TEST_USER = {
    "email": os.getenv("KING_JOUET_TEST_EMAIL", ""),
    "password": os.getenv("KING_JOUET_TEST_PASSWORD", ""),
    "first_name": "Test",
    "last_name": "Utilisateur",
    "address": "123 Rue de Test",
    "postal_code": "75000",
    "city": "Paris",
    "phone": "0612345678"
}