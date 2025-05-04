# tests/test_king_jouet_home.py
import pytest
from playwright.sync_api import sync_playwright
from websites.KingJouet.pages.home_page import HomePage
from config.settings import BROWSER_TYPE, HEADLESS

@pytest.fixture(scope="function")
def browser():
    """
    Fixture pour initialiser le navigateur.
    """
    with sync_playwright() as p:
        if BROWSER_TYPE == "chromium":
            browser = p.chromium.launch(headless=HEADLESS)
        elif BROWSER_TYPE == "firefox":
            browser = p.firefox.launch(headless=HEADLESS)
        elif BROWSER_TYPE == "webkit":
            browser = p.webkit.launch(headless=HEADLESS)
        else:
            browser = p.chromium.launch(headless=HEADLESS)
        
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    """
    Fixture pour initialiser la page.
    """
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def test_home_page_navigation(page):
    """
    Teste la navigation vers la page d'accueil et la gestion des popups.
    """
    home_page = HomePage(page)
    home_page.navigate()
    
    # Vérifier que l'élément du logo est visible, ce qui confirme que nous sommes sur la page d'accueil
    assert home_page.is_visible("#logo_header"), "Le logo King Jouet devrait être visible"

def test_search_function(page):
    """
    Teste la fonction de recherche.
    """
    home_page = HomePage(page)
    home_page.navigate()
    
    # Effectuer une recherche
    search_page = home_page.search_product("lego")
    
    # Vérifier que nous avons été redirigés vers la page de résultats de recherche
    assert "recherche" in page.url, "L'URL devrait contenir 'recherche'"
    
    # Vérifier que des résultats de recherche sont affichés
    assert search_page.is_visible(".ais-Hits-list"), "Les résultats de recherche devraient être visibles"

def test_cookie_consent(page):
    """
    Teste la gestion du consentement des cookies.
    """
    home_page = HomePage(page)
    
    # Naviguer sans gérer les cookies d'abord
    super(HomePage, home_page).navigate(home_page.base_url)
    
    # Vérifier si la bannière de cookies est présente
    has_cookies_banner = home_page.is_visible("#onetrust-accept-btn-handler", timeout=5000)
    
    if has_cookies_banner:
        # Accepter les cookies
        result = home_page.handle_cookie_consent()
        assert result, "La bannière de cookies aurait dû être acceptée"
        
        # Vérifier que la bannière a disparu
        assert not home_page.is_visible("#onetrust-accept-btn-handler", timeout=2000), "La bannière de cookies devrait avoir disparu"