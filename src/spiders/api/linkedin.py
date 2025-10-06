# src/spiders/api/linkedin.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from classes.job import Job
from utils.enums import Website, Position, Modality
from utils import config
from utils.fetch import linkedin_fetch


BASE_UI = "https://www.linkedin.com/jobs/search/"
BASE_GUEST = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


@dataclass
class _Link:
    url: str
    date: datetime
    modality: Modality


class LinkedInSpider:
    def __init__(self):
        self.website = Website.LINKEDIN
        self.f_tpr_seconds: int = (
            getattr(config, "LINKEDIN_F_TPR_SECONDS", None)
            or int(getattr(config, "LINKEDIN_HOURS", 4)) * 3600
        )
        self.location = str(getattr(config, "LINKEDIN_LOCATION", "Chile") or "Chile")
        self.keywords = str(getattr(config, "LINKEDIN_KEYWORDS", "")).strip()
        self.max_pages = int(getattr(config, "LINKEDIN_MAX_PAGES", 6))
        self.headless = str(getattr(config, "LINKEDIN_HEADLESS", "0")).lower() in ("1", "true", "yes")

    def run(self) -> List[Job]:
        # Si falla la UI (ERR_HTTP_RESPONSE_CODE_FAILURE / checkpoint), se usa guest automáticamente
        if not self.headless:
            try:
                return self._run_ui()
            except Exception:
                pass
        return self._run_guest()

    # ---------- UI ----------

    def _run_ui(self) -> List[Job]:
        jobs: List[Job] = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            try:
                context = browser.new_context(storage_state="state.json")
            except Exception:
                context = browser.new_context()
            page = context.new_page()

            try:
                self._ensure_login(page)

                for position in Position:
                    kw = self.keywords or position.value
                    url = self._build_search_url_ui(kw)
                    try:
                        page.goto(url, timeout=60_000, wait_until="domcontentloaded")
                    except Exception as e:
                        raise RuntimeError(f"goto failed: {e}")  # dispara fallback

                    self._accept_cookies(page)
                    if not self._wait_results(page):
                        try:
                            page.wait_for_load_state("networkidle", timeout=10_000)
                        except PWTimeout:
                            pass
                        if not self._wait_results(page):
                            continue

                    self._force_links_same_tab(page)
                    self._scroll_results(page, max_scrolls=10)

                    while True:
                        if page.is_closed():
                            break
                        cards = self._cards_locator(page)
                        count = cards.count()
                        if count == 0:
                            break

                        for i in range(count):
                            if page.is_closed():
                                break
                            try:
                                li = cards.nth(i)
                                a = li.locator("a[href*='/jobs/view/']")
                                if a.count():
                                    a.first.click(timeout=10_000)
                                else:
                                    li.click(timeout=10_000)

                                page.wait_for_selector(
                                    ".top-card-layout__title, .job-details-jobs-unified-top-card__job-title, h1.t-24.t-bold",
                                    timeout=20_000,
                                )

                                html = page.content()
                                soup = BeautifulSoup(html, "html.parser")
                                job_url = self._extract_job_url(page, soup)
                                modality = self._guess_modality_from_detail(soup)
                                date = datetime.utcnow()

                                job = Job(
                                    title="",
                                    company="",
                                    url=job_url,
                                    published_at=date,
                                    position=position,
                                    website=self.website,
                                )
                                job.set_linkedin_html(html, date, modality)
                                jobs.append(job)

                            except PWTimeout:
                                continue
                            except Exception:
                                continue

                        before = count
                        self._scroll_results(page, max_scrolls=3)
                        after = self._cards_locator(page).count()
                        if after <= before:
                            break

            finally:
                try:
                    context.storage_state(path="state.json")
                except Exception:
                    pass
                context.close()
                browser.close()

        return jobs

    def _build_search_url_ui(self, keywords: str) -> str:
        loc = f"geoId={self.location}" if self.location.isdigit() else f"location={self.location}"
        return f"{BASE_UI}?keywords={keywords}&{loc}&f_TPR=r{self.f_tpr_seconds}"

    def _ensure_login(self, page):
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
            for _ in range(120):
                if page.is_closed():
                    return
                if not any(k in page.url for k in ("checkpoint", "authwall", "login")):
                    break
                page.wait_for_timeout(2000)

    def _accept_cookies(self, page):
        for sel in (
            "button[aria-label*='cookies' i]",
            "button:has-text('Aceptar todas')",
            "button:has-text('Aceptar todo')",
            "button:has-text('Aceptar')",
            "button:has-text('Accept all')",
            "button:has-text('Accept')",
            "button:has-text('I agree')",
        ):
            btn = page.locator(sel)
            if btn.count():
                try:
                    btn.first.click()
                    page.wait_for_timeout(400)
                    break
                except Exception:
                    pass

    def _wait_results(self, page) -> bool:
        try:
            page.wait_for_selector(
                ",".join([
                    "ul.scaffold-layout__list-container li",
                    "li.jobs-search-results__list-item",
                    "li[data-occludable-job-id]",
                    "[data-results-list]",
                    "a[href*='/jobs/view/']"
                ]),
                timeout=25_000,
            )
            return True
        except PWTimeout:
            return False

    def _results_container(self, page):
        for sel in (
            "section.two-pane-serp-page__results-list",
            "div.jobs-search-results-list",
            "[data-results-list]",
            "div.scaffold-layout__list",
        ):
            loc = page.locator(sel).first
            if loc.count():
                return loc
        return page.locator("body")

    def _force_links_same_tab(self, page):
        try:
            page.evaluate("document.querySelectorAll(\"a[target='_blank']\").forEach(a => a.removeAttribute('target'));")
        except Exception:
            pass

    def _cards_locator(self, page):
        return page.locator(
            "li.jobs-search-results__list-item, "
            "li[data-occludable-job-id], "
            "ul.scaffold-layout__list-container li, "
            "div.job-card-container--clickable"
        )

    def _scroll_results(self, page, max_scrolls: int = 10):
        cont = self._results_container(page)
        for _ in range(max_scrolls):
            if page.is_closed():
                return
            before = self._cards_locator(page).count()
            try:
                cont.evaluate("el => el.scrollBy(0, el.scrollHeight)")
            except Exception:
                try:
                    cont.focus()
                    page.keyboard.press("PageDown")
                except Exception:
                    pass
            page.wait_for_timeout(900)
            after = self._cards_locator(page).count()
            if after <= before:
                break

    def _extract_job_url(self, page, soup: BeautifulSoup) -> str:
        canon = soup.select_one("link[rel='canonical']")
        if canon and canon.get("href"):
            return canon["href"].split("?")[0]
        a = soup.select_one("a.base-card__full-link, a.topcard__button, a.topcard__org-name-link, a[href*='/jobs/view/']")
        if a and a.get("href") and a["href"].startswith("http"):
            return a["href"].split("?")[0]
        return page.url.split("?")[0]

    def _guess_modality_from_detail(self, soup: BeautifulSoup) -> Modality:
        txt = soup.get_text(" ", strip=True).lower()
        if "remoto" in txt or "remote" in txt:
            return Modality.REMOTO
        if "híbrido" in txt or "hibrido" in txt or "hybrid" in txt:
            return Modality.HIBRIDO
        return Modality.PRESENCIAL

    # ---------- Guest ----------

    def _run_guest(self) -> List[Job]:
        jobs: List[Job] = []
        for position in Position:
            links = self._collect_links_guest(position)
            for ln in links:
                j = self._build_job_from_detail_guest(ln, position)
                if j:
                    jobs.append(j)
        return jobs

    def _collect_links_guest(self, position: Position) -> List[_Link]:
        links: List[_Link] = []
        seen: set[str] = set()
        for page in range(self.max_pages):
            params = {
                "keywords": self.keywords or position.value,
                "f_TPR": f"r{self.f_tpr_seconds}",
                "start": page * 25,
            }
            params["location"] = self.location if not self.location.isdigit() else "Chile"
            url = f"{BASE_GUEST}?{urlencode(params)}"
            html = linkedin_fetch(url)
            if not html:
                break
            cards = self._parse_list_html_guest(html)
            if not cards:
                break
            for c in cards:
                if c.url in seen:
                    continue
                seen.add(c.url)
                links.append(c)
        return links

    def _parse_list_html_guest(self, html: str) -> List[_Link]:
        soup = BeautifulSoup(html, "html.parser")
        out: List[_Link] = []
        for it in soup.select(".base-card, .job-search-card"):
            a = it.select_one("a.base-card__full-link, a.result-card__full-card-link")
            if not a or not a.get("href"):
                continue
            url = a["href"].split("?")[0]
            posted = self._extract_relative_date(it)
            modality = self._extract_modality_hint(it)
            out.append(_Link(url=url, date=posted, modality=modality))
        return out

    def _extract_relative_date(self, node) -> datetime:
        now = datetime.utcnow()
        t = node.select_one("time")
        txt = (t.get("datetime") or t.get_text() or "").strip().lower() if t else ""
        if not txt:
            extra = node.select_one(".job-search-card__listdate, .job-search-card__listdate--new")
            txt = extra.get_text(strip=True).lower() if extra else ""
        try:
            if any(w in txt for w in ("hour", "hora")):
                n = _first_int(txt) or 1
                return now - timedelta(hours=n)
            if any(w in txt for w in ("day", "día", "dias", "días")):
                n = _first_int(txt) or 1
                return now - timedelta(days=n)
            if any(w in txt for w in ("week", "semana")):
                n = _first_int(txt) or 1
                return now - timedelta(weeks=n)
        except Exception:
            pass
        return now

    def _extract_modality_hint(self, node) -> Modality:
        text = node.get_text(" ", strip=True).lower()
        if "remoto" in text or "remote" in text:
            return Modality.REMOTO
        if "híbrido" in text or "hibrido" in text or "hybrid" in text:
            return Modality.HIBRIDO
        return Modality.PRESENCIAL

    def _build_job_from_detail_guest(self, link: _Link, position: Position) -> Optional[Job]:
        html = linkedin_fetch(link.url)
        if not html:
            return None
        job = Job(
            title="",
            company="",
            url=link.url,
            published_at=link.date,
            position=position,
            website=self.website,
        )
        job.set_linkedin_html(html, link.date, link.modality)
        return job


def _first_int(s: str) -> Optional[int]:
    buf = ""
    for ch in s:
        if ch.isdigit():
            buf += ch
        elif buf:
            break
    return int(buf) if buf else None
