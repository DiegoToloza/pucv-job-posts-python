# src/test_linkedin_print.py
from __future__ import annotations

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout, Error as PWError
from utils import config

BASE = "https://www.linkedin.com/jobs/search/"

def build_search_url(keywords: str, location: str, f_tpr_seconds: int) -> str:
    loc_param = f"geoId={location}" if str(location).isdigit() else f"location={location}"
    return f"{BASE}?keywords={keywords}&{loc_param}&f_TPR=r{f_tpr_seconds}"

def accept_cookies(page):
    # distintos banners según idioma/experimentos
    selectors = [
        "button[aria-label*='cookies' i]",
        "button:has-text('Aceptar todas')",
        "button:has-text('Aceptar todo')",
        "button:has-text('Aceptar')",
        "button:has-text('Accept all')",
        "button:has-text('Accept')",
        "button:has-text('I agree')",
    ]
    for sel in selectors:
        btn = page.locator(sel)
        if btn.count():
            try:
                btn.first.click()
                page.wait_for_timeout(500)
                break
            except Exception:
                pass

def ensure_login(page):
    try:
        page.goto("https://www.linkedin.com/feed/", timeout=40_000)
    except PWTimeout:
        pass

    if any(k in page.url for k in ("login", "authwall", "checkpoint")):
        page.goto("https://www.linkedin.com/login", timeout=60_000)
        page.wait_for_selector("input#username", timeout=60_000)

        user = getattr(config, "LINKEDIN_USER", "")
        pwd = getattr(config, "LINKEDIN_PASSWORD", "")
        if user and pwd:
            page.fill("input#username", user)
            page.fill("input#password", pwd)
            page.click("button[type='submit']")
        else:
            print("Sin credenciales en .env — inicia sesión manualmente en la ventana.")

        # espera hasta salir de login/checkpoint/authwall
        for _ in range(120):  # ~4 min
            if page.is_closed():
                return
            if not any(k in page.url for k in ("checkpoint", "authwall", "login")):
                break
            page.wait_for_timeout(2000)

def wait_results(page) -> bool:
    # espera a que aparezca cualquier lista de resultados o links de jobs
    try:
        page.wait_for_selector(
            ",".join([
                "ul.scaffold-layout__list-container li",
                "li.jobs-search-results__list-item",
                "div.job-card-container--clickable",
                "[data-results-list]",
                "a[href*='/jobs/view/']"
            ]),
            timeout=25_000,
        )
        return True
    except PWTimeout:
        return False

def results_container(page):
    for sel in [
        "section.two-pane-serp-page__results-list",
        "div.jobs-search-results-list",
        "[data-results-list]",
        "div.scaffold-layout__list",
    ]:
        loc = page.locator(sel).first
        if loc.count():
            return loc
    # fallback: body (scroll de página completa)
    return page.locator("body")

def cards_locator(page):
    # usamos anchors a /jobs/view/ que son estables entre layouts
    return page.locator(
        "ul.scaffold-layout__list-container li a[href*='/jobs/view/'], "
        "li.jobs-search-results__list-item a[href*='/jobs/view/'], "
        "a.job-card-container__link[href*='/jobs/view/'], "
        "a[href*='/jobs/view/']"
    )

def click_see_more(page):
    btn = page.locator("button.show-more-less-html__button:not([aria-expanded='true'])")
    if btn.count():
        try:
            btn.first.click()
        except Exception:
            pass

def extract_title_and_desc(page) -> tuple[str | None, str | None]:
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    # Título (varios layouts posibles)
    title = None
    for sel in [".top-card-layout__title",
                ".job-details-jobs-unified-top-card__job-title",
                "h1.t-24.t-bold"]:
        el = soup.select_one(sel)
        if el:
            title = el.get_text(strip=True)
            break
    # Descripción en TEXTO (para consola legible)
    desc = None
    for sel in [".description__text--rich .show-more-less-html__markup",
                "div.jobs-description__content",
                "div.jobs-box__html-content",
                "section.show-more-less-html"]:
        el = soup.select_one(sel)
        if el:
            desc = el.get_text(" ", strip=True)
            break
    return title, desc

def scroll_results(page, max_scrolls: int = 10):
    cont = results_container(page)
    for _ in range(max_scrolls):
        if page.is_closed():
            return
        before = cards_locator(page).count()
        try:
            cont.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        except Exception:
            try:
                cont.focus()
                page.keyboard.press("PageDown")
            except Exception:
                pass
        page.wait_for_timeout(900)
        after = cards_locator(page).count()
        if after <= before:
            break

if __name__ == "__main__":
    keywords = (getattr(config, "LINKEDIN_KEYWORDS", "") or "devops").strip()
    location = str(getattr(config, "LINKEDIN_LOCATION", "Chile") or "Chile")
    f_tpr = getattr(config, "LINKEDIN_F_TPR_SECONDS", None) or int(getattr(config, "LINKEDIN_HOURS", 4)) * 3600

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        # reusar sesión si existe
        try:
            context = browser.new_context(storage_state="state.json")
        except Exception:
            context = browser.new_context()
        page = context.new_page()

        try:
            ensure_login(page)
            if page.is_closed():
                raise RuntimeError("La pestaña se cerró durante el login.")

            url = build_search_url(keywords, location, f_tpr)
            page.goto(url, timeout=60_000)
            accept_cookies(page)

            if not wait_results(page):
                # reintento suave: espera la red y vuelve a chequear
                try:
                    page.wait_for_load_state("networkidle", timeout=10_000)
                except PWTimeout:
                    pass
                if not wait_results(page):
                    raise RuntimeError("No se detectó el contenedor de resultados (authwall/cookies/ubicación).")

            # carga más elementos con scroll (como el scraper viejo)
            scroll_results(page, max_scrolls=10)

            printed = 0
            while True:
                if page.is_closed():
                    print("Pestaña cerrada — fin.")
                    break

                cards = cards_locator(page)
                count = cards.count()
                if count == 0:
                    print("No hay cards en la lista.")
                    break

                for i in range(count):
                    if page.is_closed():
                        break
                    try:
                        # click en el anchor de la card
                        cards.nth(i).click(timeout=10_000)
                        page.wait_for_selector(
                            ".top-card-layout__title, .job-details-jobs-unified-top-card__job-title, h1.t-24.t-bold",
                            timeout=20_000,
                        )

                        click_see_more(page)
                        title, desc = extract_title_and_desc(page)
                        printed += 1
                        print(f"\n[{printed}] {title or '(sin título)'}")
                        if desc:
                            # imprime primeros 700 chars para no saturar
                            print(desc[:700] + ("..." if len(desc) > 700 else ""))
                        else:
                            print("(sin descripción)")

                    except PWTimeout:
                        continue
                    except PWError as e:
                        if "Target page" in str(e) or "Target closed" in str(e):
                            print("El navegador/pestaña se cerró.")
                            break
                        continue
                    except Exception as e:
                        print("Error en card:", e)
                        continue

                # intenta cargar más por scroll adicional
                before = count
                scroll_results(page, max_scrolls=3)
                after = cards.count()
                if after <= before:
                    break

        finally:
            try:
                context.storage_state(path="state.json")
            except Exception:
                pass
            context.close()
            browser.close()
