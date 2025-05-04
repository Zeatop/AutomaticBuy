# websites/common/base_page.py
import time
import random
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Union, Dict, Any, List, Callable

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

from config.settings import (
    DEFAULT_TIMEOUT, 
    DEFAULT_WAIT_TIME, 
    RETRY_COUNT, 
    SCREENSHOTS_DIR
)
from utils.logger import get_logger

class BasePage:
    """
    Classe de base pour toutes les pages web.
    Fournit des méthodes communes pour interagir avec les pages.
    """
    
    def __init__(self, page: Page, base_url: str = ""):
        """
        Initialise une nouvelle instance de BasePage.
        
        Args:
            page: L'instance de Page Playwright
            base_url: L'URL de base du site
        """
        self.page = page
        self.base_url = base_url
        self.logger = get_logger(self.__class__.__name__)
        
    def navigate(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigue vers une URL et attend que la page soit chargée.
        
        Args:
            url: L'URL à laquelle naviguer
            wait_until: Événement à attendre ('load', 'domcontentloaded', 'networkidle')
        """
        full_url = url if url.startswith(('http://', 'https://')) else f"{self.base_url}{url}"
        self.logger.info(f"Navigation vers: {full_url}")
        
        try:
            self.page.goto(full_url, wait_until=wait_until, timeout=DEFAULT_TIMEOUT)
        except PlaywrightTimeoutError:
            self.logger.warning(f"Timeout lors de la navigation vers {full_url}. Capture d'écran prise.")
            self.take_screenshot(f"navigation_timeout_{self._get_timestamp()}")
            # On continue malgré le timeout, car la page peut être partiellement chargée
    
    def wait_for_selector(self, selector: str, timeout: int = DEFAULT_TIMEOUT) -> Locator:
        """
        Attend qu'un élément soit présent dans le DOM.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            timeout: Durée maximale d'attente en millisecondes
            
        Returns:
            Locator: Référence à l'élément trouvé
            
        Raises:
            Exception: Si l'élément n'est pas trouvé après le timeout
        """
        self.logger.debug(f"Attente du sélecteur: {selector}")
        try:
            return self.page.wait_for_selector(selector, timeout=timeout)
        except PlaywrightTimeoutError as e:
            self.logger.error(f"Élément non trouvé: {selector}")
            self.take_screenshot(f"element_not_found_{selector.replace(':', '_')}")
            raise Exception(f"Élément non trouvé: {selector}") from e
    
    def wait_for_navigation(self, timeout: int = DEFAULT_TIMEOUT, wait_until: str = "networkidle") -> None:
        """
        Attend que la navigation soit terminée.
        
        Args:
            timeout: Durée maximale d'attente en millisecondes
            wait_until: Événement à attendre ('load', 'domcontentloaded', 'networkidle')
        """
        self.logger.debug("Attente de la fin de la navigation")
        try:
            self.page.wait_for_load_state(wait_until, timeout=timeout)
        except PlaywrightTimeoutError:
            self.logger.warning(f"Timeout en attendant la navigation ({wait_until})")
            self.take_screenshot(f"navigation_wait_timeout_{self._get_timestamp()}")
    
    def click(self, selector: str, force: bool = False, retry_count: int = RETRY_COUNT) -> None:
        """
        Clique sur un élément avec mécanisme de réessai.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            force: Forcer le clic même si l'élément n'est pas visible
            retry_count: Nombre de tentatives en cas d'échec
        """
        self.logger.debug(f"Clic sur l'élément: {selector}")
        
        for attempt in range(retry_count):
            try:
                # Attendre que l'élément soit présent
                element = self.wait_for_selector(selector)
                
                # Faire défiler jusqu'à l'élément
                element.scroll_into_view_if_needed()
                
                # Attendre un court instant pour s'assurer que l'élément est cliquable
                time.sleep(0.5)
                
                # Cliquer sur l'élément
                element.click(force=force)
                return
                
            except Exception as e:
                self.logger.warning(f"Échec du clic sur {selector} (tentative {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    # Attendre un délai aléatoire avant de réessayer
                    time.sleep(random.uniform(0.5, 2.0))
                else:
                    self.take_screenshot(f"click_failed_{selector.replace(':', '_')}")
                    raise Exception(f"Impossible de cliquer sur l'élément: {selector} après {retry_count} tentatives") from e
    
    def fill(self, selector: str, value: str, retry_count: int = RETRY_COUNT) -> None:
        """
        Remplit un champ de formulaire avec une valeur.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            value: La valeur à entrer dans le champ
            retry_count: Nombre de tentatives en cas d'échec
        """
        masked_value = '*' * len(value) if 'password' in selector.lower() else value
        self.logger.debug(f"Remplissage du champ {selector} avec la valeur: {masked_value}")
        
        for attempt in range(retry_count):
            try:
                element = self.wait_for_selector(selector)
                element.fill(value)
                return
            except Exception as e:
                self.logger.warning(f"Échec du remplissage de {selector} (tentative {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(0.5, 2.0))
                else:
                    self.take_screenshot(f"fill_failed_{selector.replace(':', '_')}")
                    raise Exception(f"Impossible de remplir le champ: {selector} après {retry_count} tentatives") from e
    
    def select_option(self, selector: str, value: Union[str, List[str]], retry_count: int = RETRY_COUNT) -> None:
        """
        Sélectionne une option dans un menu déroulant.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            value: La valeur à sélectionner (ou liste de valeurs)
            retry_count: Nombre de tentatives en cas d'échec
        """
        self.logger.debug(f"Sélection de l'option {value} dans {selector}")
        
        for attempt in range(retry_count):
            try:
                element = self.wait_for_selector(selector)
                element.select_option(value=value if isinstance(value, list) else [value])
                return
            except Exception as e:
                self.logger.warning(f"Échec de la sélection dans {selector} (tentative {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(0.5, 2.0))
                else:
                    self.take_screenshot(f"select_failed_{selector.replace(':', '_')}")
                    raise Exception(f"Impossible de sélectionner l'option dans: {selector} après {retry_count} tentatives") from e
    
    def is_visible(self, selector: str, timeout: int = DEFAULT_WAIT_TIME) -> bool:
        """
        Vérifie si un élément est visible sur la page.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            timeout: Durée maximale d'attente en millisecondes
            
        Returns:
            bool: True si l'élément est visible, False sinon
        """
        try:
            return self.page.is_visible(selector, timeout=timeout)
        except Exception:
            return False
    
    def wait_until(self, condition: Callable[[], bool], timeout: int = DEFAULT_TIMEOUT, interval: int = 1000) -> bool:
        """
        Attend jusqu'à ce qu'une condition soit remplie.
        
        Args:
            condition: Une fonction qui renvoie True lorsque la condition est remplie
            timeout: Durée maximale d'attente en millisecondes
            interval: Intervalle entre les vérifications en millisecondes
            
        Returns:
            bool: True si la condition a été remplie, False si timeout
        """
        self.logger.debug("Attente d'une condition personnalisée")
        start_time = time.time()
        end_time = start_time + (timeout / 1000)
        
        while time.time() < end_time:
            if condition():
                return True
            time.sleep(interval / 1000)
        
        self.logger.warning("Timeout en attendant qu'une condition soit remplie")
        return False
    
    def take_screenshot(self, name: str = None) -> str:
        """
        Prend une capture d'écran de la page actuelle.
        
        Args:
            name: Nom de base pour le fichier (sans extension)
            
        Returns:
            str: Chemin vers la capture d'écran
        """
        timestamp = self._get_timestamp()
        name = name if name else f"screenshot_{timestamp}"
        filename = f"{name}_{timestamp}.png"
        path = SCREENSHOTS_DIR / filename
        
        self.logger.info(f"Capture d'écran prise: {path}")
        self.page.screenshot(path=str(path))
        return str(path)
    
    def get_text(self, selector: str, default: str = "") -> str:
        """
        Récupère le texte d'un élément.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            default: Valeur par défaut si l'élément n'est pas trouvé
            
        Returns:
            str: Le texte de l'élément ou la valeur par défaut
        """
        try:
            element = self.wait_for_selector(selector)
            return element.text_content() or default
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer le texte de {selector}: {str(e)}")
            return default
    
    def get_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        """
        Récupère la valeur d'un attribut d'un élément.
        
        Args:
            selector: Le sélecteur CSS ou XPath de l'élément
            attribute: Nom de l'attribut
            default: Valeur par défaut si l'attribut n'est pas trouvé
            
        Returns:
            str: La valeur de l'attribut ou la valeur par défaut
        """
        try:
            element = self.wait_for_selector(selector)
            return element.get_attribute(attribute) or default
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer l'attribut {attribute} de {selector}: {str(e)}")
            return default
        
    def wait_for_url(self, url_pattern: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Attend que l'URL de la page corresponde à un modèle.
        
        Args:
            url_pattern: Modèle d'URL à attendre (peut être une chaîne partielle ou une expression régulière)
            timeout: Durée maximale d'attente en millisecondes
        """
        self.logger.debug(f"Attente de l'URL correspondant à: {url_pattern}")
        try:
            self.page.wait_for_url(url_pattern, timeout=timeout)
        except PlaywrightTimeoutError:
            current_url = self.page.url
            self.logger.warning(f"Timeout en attendant l'URL {url_pattern}, URL actuelle: {current_url}")
            self.take_screenshot(f"url_wait_timeout_{self._get_timestamp()}")
    
    def _get_timestamp(self) -> str:
        """
        Génère un horodatage formaté pour les noms de fichiers.
        
        Returns:
            str: Horodatage au format YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def retry_on_exception(self, func: Callable, *args, retry_count: int = RETRY_COUNT, **kwargs) -> Any:
        """
        Exécute une fonction avec mécanisme de réessai en cas d'exception.
        
        Args:
            func: La fonction à exécuter
            *args: Arguments positionnels à passer à la fonction
            retry_count: Nombre de tentatives en cas d'échec
            **kwargs: Arguments nommés à passer à la fonction
            
        Returns:
            Any: Le résultat de la fonction
            
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        last_exception = None
        func_name = getattr(func, "__name__", "fonction anonyme")
        
        for attempt in range(retry_count):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Échec de {func_name} (tentative {attempt+1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(0.5, 2.0))
        
        self.logger.error(f"Échec complet de {func_name} après {retry_count} tentatives")
        raise last_exception