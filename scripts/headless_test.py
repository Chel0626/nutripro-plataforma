from playwright.sync_api import sync_playwright
import json
import time

LOG_PATH = 'scripts/headless_console.json'
URL = 'http://127.0.0.1:8080/paciente/1/plano/novo'

console_messages = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context()
    page = context.new_page()

    def _on_console(msg):
        try:
            console_messages.append({'type': msg.type, 'text': msg.text})
        except Exception as e:
            console_messages.append({'type': 'error', 'text': f'console callback error: {e}'})

    page.on('console', _on_console)

    print('navegando para', URL)
    page.goto(URL, wait_until='networkidle')
    time.sleep(0.5)

    # tenta focar um input visível e digitar 'arroz' para ativar o autocomplete
    focused = page.evaluate("""
    (() => {
        const inputs = Array.from(document.querySelectorAll('input'));
        for (const i of inputs) {
            const rect = i.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0 && window.getComputedStyle(i).visibility !== 'hidden') {
                i.focus();
                return true;
            }
        }
        return false;
    })();
    """)

    if not focused:
        print('não conseguiu focar input visível; procurando por textarea...')
        page.evaluate("(() => { const t = document.querySelector('textarea'); if(t){ t.focus(); return true } return false })();")

    # digita devagar para simular usuário
    page.keyboard.type('arroz')
    time.sleep(2)

    # esperar um pouco para possíveis requisições/erros
    time.sleep(1)

    # captura possível HTML parcial para inspeção
    try:
        html = page.content()
        with open('scripts/paciente1_plano_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
    except Exception:
        pass

    browser.close()

with open(LOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(console_messages, f, ensure_ascii=False, indent=2)

print('console logs salvos em', LOG_PATH)
