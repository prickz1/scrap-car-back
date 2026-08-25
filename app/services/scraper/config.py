URL_BASE = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-mg?sp=2"
TOTAL_PAGINAS = 100
MAX_LOTES = 50

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});
window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}, app: {}};
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({state: Notification.permission})
        : originalQuery(parameters);
"""

SELETOR_CARD = 'div.olx-adcard__content'
SELETOR_LINK = 'a[data-testid="adcard-link"]'
SELETOR_TITULO = 'h2'
SELETOR_PRECO = 'h3.olx-adcard__price'
SELETOR_LOCALIZACAO = 'p.olx-adcard__location'
SELETOR_QUILOMETRAGEM = 'div.olx-adcard__detail[aria-label*="quilômetro"]'
