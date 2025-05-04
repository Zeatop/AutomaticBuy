# websites/KingJouet/pages/cart_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time, parse_price, clean_text
from websites.KingJouet.config import CART_URL, SELECTORS, TIMEOUTS

class CartPage(BasePage):
    """
    Page du panier du site King Jouet.
    Permet de consulter et modifier le contenu du panier.
    """
    
    def __init__(self, page):
        """
        Initialise la page du panier.
        
        Args:
            page: L'instance de Page Playwright
        """
        super().__init__(page, CART_URL)
        self.logger = get_logger(self.__class__.__name__)
    
    def navigate(self):
        """
        Accède directement à la page du panier.
        
        Returns:
            self: Pour permettre le chaînage des méthodes
        """
        self.logger.info(f"Navigation directe vers la page du panier: {CART_URL}")
        super().navigate(CART_URL)
        return self
    
    def get_cart_items(self):
        """
        Récupère les articles présents dans le panier.
        
        Returns:
            list: Liste de dictionnaires représentant les articles du panier
        """
        self.logger.info("Récupération des articles du panier")
        
        try:
            # Attendre que le panier soit chargé
            self.wait_for_selector(SELECTORS["cart_items_available"], timeout=TIMEOUTS["page_load"])
            
            # Sélectionner tous les éléments d'article du panier
            cart_item_selector = SELECTORS["cart_item"]  # À vérifier selon la structure du site
            cart_item_elements = self.page.query_selector_all(cart_item_selector)
            
            cart_items = []
            for element in cart_item_elements:
                try:
                    # Nom du produit
                    name_element = element.query_selector(SELECTORS["cart_item_name"])
                    name = clean_text(name_element.text_content()) if name_element else "Produit inconnu"
                    
                    # Prix unitaire
                    euros_element = element.query_selector(SELECTORS["cart_item_price_detail_euros"])
                    cents_element = element.query_selector(SELECTORS["cart_item_price_detail_cents"])
                    if euros_element and cents_element:
                        price_text = euros_element.text_content() + "," + cents_element.text_content()
                    
                    try:
                        price = parse_price(price_text)
                    except ValueError:
                        price = 0.0
                    
                    # Quantité
                    quantity_element = element.query_selector(SELECTORS["item_quantity"])
                    quantity = int(quantity_element.get_attribute("value") or "1") if quantity_element else 1
                    
                    # Prix total
                    total_price = price * quantity
                    
                    # Ajouter l'article au panier
                    cart_items.append({
                        "name": name,
                        "price": price,
                        "quantity": quantity,
                        "total_price": total_price
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Erreur lors de l'extraction des informations d'un article: {str(e)}")
            
            return cart_items
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des articles du panier: {str(e)}")
            self.take_screenshot("get_cart_items_error")
            return []
    
    def get_cart_total(self):
        """
        Récupère le montant total du panier.
        
        Returns:
            float: Montant total du panier
        """
        self.logger.info("Récupération du montant total du panier")
        
        try:
            # Sélectionner l'élément contenant le total
            total_euros = self.page.query_selector(SELECTORS["cart_total_euros"])
            total_cents = self.page.query_selector(SELECTORS["cart_total_cents"])
            if not total_euros:
                return 0.0
            
            # Extraire le montant total
            total_text = total_euros.text_content()+ "," + (total_cents.text_content() if total_cents else "0")
            return parse_price(total_text)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du montant total: {str(e)}")
            return 0.0
    
    def update_quantity(self, item_index, new_quantity):
        """
        Met à jour la quantité d'un article dans le panier.
        
        Args:
            item_index: Index de l'article à modifier
            new_quantity: Nouvelle quantité
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        self.logger.info(f"Mise à jour de la quantité de l'article {item_index} à {new_quantity}")
        self.wait_for_selector(SELECTORS["cart_items_available"], timeout=TIMEOUTS["page_load"])
        add_button = self.page.query_selector(SELECTORS["change_quantity_item"])[1]
        remove_button = self.page.query_selector(SELECTORS["change_quantity_item"])[0]
        
        try:
            # Sélectionner tous les éléments d'article du panier
            cart_item_selector = SELECTORS["cart_item"]  # À vérifier selon la structure du site
            cart_item_elements = self.page.query_selector_all(cart_item_selector)
            
            if item_index >= len(cart_item_elements):
                self.logger.error(f"Index d'article {item_index} hors limites (max: {len(cart_item_elements) - 1})")
                return False
            
            # Sélectionner l'élément de quantité de l'article
            quantity_element = cart_item_elements[item_index].query_selector(SELECTORS["item_quantity"])
            if not quantity_element:
                self.logger.error("Élément de quantité non trouvé")
                return False
            
            # Obtenir la quantité actuelle
            current_quantity = int(quantity_element.get_attribute("value") or "1")
            
            # Si la nouvelle quantité est la même, rien à faire
            if current_quantity == new_quantity:
                return True
            
            # Sinon, mettre à jour la quantité
            if new_quantity > current_quantity:
                # Augmenter la quantité
                add_button = self.page.query_selector_all(add_button)
                for _ in range(new_quantity - current_quantity):
                    add_button.click()
                    wait_random_time(0.5, 1.0)
            else:
                # Diminuer la quantité
                remove_button = self.page.query_selector_all(remove_button)
                for _ in range(current_quantity - new_quantity):
                    remove_button.click()
                    wait_random_time(0.5, 1.0)
            
            # Attendre que le panier soit mis à jour
            self.wait_for_navigation(timeout=TIMEOUTS["add_to_cart"])
            
            # Vérifier si la mise à jour a réussi
            updated_quantity_element = cart_item_elements[item_index].query_selector(SELECTORS["quantity_input"])
            updated_quantity = int(updated_quantity_element.get_attribute("value") or "1") if updated_quantity_element else 0
            
            return updated_quantity == new_quantity
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la quantité: {str(e)}")
            self.take_screenshot("update_quantity_error")
            return False
    
    def proceed_to_checkout(self):
        """
        Procède au paiement.
        
        Returns:
            CheckoutPage: Instance de la page de paiement
        """
        self.logger.info("Procéder au paiement")
        
        try:
            # Cliquer sur le bouton de paiement
            self.click(SELECTORS["proceed_to_checkout"])
            
            # Attendre que la page de paiement soit chargée
            self.wait_for_navigation(timeout=TIMEOUTS["checkout_step"])
            
            # Importer ici pour éviter les imports circulaires
            from websites.KingJouet.pages.checkout_page import CheckoutPage
            return CheckoutPage(self.page)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du passage au paiement: {str(e)}")
            self.take_screenshot("proceed_to_checkout_error")
            # Malgré l'erreur, essayer de créer une instance de CheckoutPage
            from websites.KingJouet.pages.checkout_page import CheckoutPage
            return CheckoutPage(self.page)
    
    def is_empty(self):
        """
        Vérifie si le panier est vide.
        
        Returns:
            bool: True si le panier est vide, False sinon
        """
        return self.is_visible(SELECTORS["empty_cart"])