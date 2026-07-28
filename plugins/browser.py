"""Browser automation plugin (Playwright).

Highlights:
- A persistent session so logins survive across commands.
- `connect_existing` attaches to a Chrome you launched yourself with
  --remote-debugging-port=9222 (so you can open a site, then tell HOMA to act).
- `extract_form` returns questions/inputs + options + selectors so the LLM can
  answer arbitrary quizzes, surveys, and forms generically.
"""
from playwright.async_api import async_playwright

from config import settings
from tools.registry import Tool, ToolRegistry


class BrowserSession:
    def __init__(self):
        self._pw = None
        self.browser = None
        self.context = None
        self.page = None

    async def _start(self):
        if self._pw is None:
            self._pw = await async_playwright().start()

    async def ensure(self):
        if self.page and not self.page.is_closed():
            return self.page
        await self._start()
        if self.browser is None:
            self.browser = await self._pw.chromium.launch(
                headless=settings.HEADLESS,
                args=["--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-gpu", "--disable-blink-features=AutomationControlled"],
            )
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (HOMA Assistant)",
                viewport={"width": 1280, "height": 800},
            )
        self.page = await self.context.new_page()
        return self.page

    async def attach(self, cdp_url: str):
        await self._start()
        self.browser = await self._pw.chromium.connect_over_cdp(cdp_url)
        self.context = (self.browser.contexts or [await self.browser.new_context()])[0]
        pages = self.context.pages
        self.page = pages[0] if pages else await self.context.new_page()
        return self.page

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
        self._pw = self.browser = self.context = self.page = None


session = BrowserSession()


async def connect_existing(cdp_url: str = ""):
    url = cdp_url or settings.CHROME_CDP_URL or "http://127.0.0.1:9222"
    page = await session.attach(url)
    return {"attached": url, "current_url": page.url, "title": await page.title()}


async def goto(url: str):
    page = await session.ensure()
    await page.goto(url, wait_until="domcontentloaded", timeout=45000)
    return {"url": page.url, "title": await page.title()}


async def read_text(selector: str = "body", max_chars: int = 6000):
    page = await session.ensure()
    el = await page.query_selector(selector)
    text = (await el.inner_text()) if el else ""
    return {"selector": selector, "text": text[:max_chars]}


async def click(selector: str):
    page = await session.ensure()
    await page.click(selector, timeout=15000)
    await page.wait_for_load_state("domcontentloaded")
    return {"clicked": selector, "url": page.url}


async def type_text(selector: str, text: str, submit: bool = False):
    page = await session.ensure()
    await page.fill(selector, text)
    if submit:
        await page.press(selector, "Enter")
    return {"typed_into": selector, "submitted": submit}


async def fill_form(fields: list[dict]):
    """fields: [{selector, value, type}] where type is text|select|check|radio."""
    page = await session.ensure()
    done = []
    for f in fields:
        sel, val, typ = f["selector"], f.get("value"), f.get("type", "text")
        if typ == "text":
            await page.fill(sel, val or "")
        elif typ == "select":
            await page.select_option(sel, val)
        elif typ in ("check", "radio"):
            await page.check(sel)
        done.append(sel)
    return {"filled": done}


async def inspect():
    page = await session.ensure()
    js = """() => {
      const out = [];
      const nodes = document.querySelectorAll(
        'a,button,input,select,textarea,[role=button],[role=radio]');
      nodes.forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        let sel = el.tagName.toLowerCase();
        if (el.id) sel += '#' + el.id;
        else if (el.name) sel += '[name=\\"' + el.name + '\\"]';
        out.push({selector: sel, tag: el.tagName.toLowerCase(),
          type: el.type || null,
          text: (el.innerText || el.value || el.placeholder || '').trim().slice(0,80)});
      });
      return out.slice(0, 80);
    }"""
    return {"elements": await page.evaluate(js)}


async def extract_form():
    """Generic question/answer extraction for quizzes, surveys, and forms.
    Returns each field with its label, type, options (with selectors), so the
    LLM can choose answers and then fill them."""
    page = await session.ensure()
    js = """() => {
      const q = [];
      const labelFor = (el) => {
        if (el.id) {
          const l = document.querySelector('label[for=\\"' + el.id + '\\"]');
          if (l) return l.innerText.trim();
        }
        const p = el.closest('label');
        if (p) return p.innerText.trim();
        return (el.getAttribute('aria-label') || el.placeholder || '').trim();
      };
      // radios/checkboxes grouped by name
      const groups = {};
      document.querySelectorAll('input[type=radio],input[type=checkbox]').forEach((el) => {
        const key = el.name || Math.random().toString();
        (groups[key] = groups[key] || []).push(el);
      });
      Object.entries(groups).forEach(([name, els]) => {
        q.push({kind: 'choice', name,
          question: els[0].closest('fieldset,li,div,tr,p')?.innerText?.trim()?.slice(0,200) || name,
          options: els.map((el) => ({label: labelFor(el),
            selector: el.id ? ('#' + el.id) : ('input[name=\\"' + name + '\\"][value=\\"' + el.value + '\\"]'),
            value: el.value}))});
      });
      document.querySelectorAll('select').forEach((el) => {
        q.push({kind: 'select', question: labelFor(el),
          selector: el.id ? ('#' + el.id) : ('select[name=\\"' + el.name + '\\"]'),
          options: [...el.options].map(o => ({label: o.text, value: o.value}))});
      });
      document.querySelectorAll('input[type=text],input[type=email],input[type=number],textarea').forEach((el) => {
        q.push({kind: 'text', question: labelFor(el),
          selector: el.id ? ('#' + el.id) : (el.name ? ('[name=\\"' + el.name + '\\"]') : el.tagName.toLowerCase())});
      });
      return q.slice(0, 60);
    }"""
    return {"fields": await page.evaluate(js)}


async def scroll(direction: str = "down", amount: int = 800):
    page = await session.ensure()
    dy = amount if direction == "down" else -amount
    await page.mouse.wheel(0, dy)
    return {"scrolled": dy}


async def go_back():
    page = await session.ensure()
    await page.go_back()
    return {"url": page.url}


async def screenshot(path: str = "screenshot.png"):
    page = await session.ensure()
    await page.screenshot(path=path, full_page=True)
    return {"saved": path}


def register(r: ToolRegistry) -> None:
    C = "browser"
    r.register(Tool("browser.connect_existing",
        "Attach to your already-open Chrome (launched with --remote-debugging-port=9222).",
        {"type": "object", "properties": {"cdp_url": {"type": "string"}}}, connect_existing, category=C))
    r.register(Tool("browser.goto", "Open a URL and return the page title.",
        {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}, goto, category=C))
    r.register(Tool("browser.read", "Read text from a part of the page.",
        {"type": "object", "properties": {"selector": {"type": "string", "default": "body"},
         "max_chars": {"type": "integer", "default": 6000}}}, read_text, category=C))
    r.register(Tool("browser.inspect", "List interactive elements (links/buttons/inputs) with selectors.",
        {"type": "object", "properties": {}}, inspect, category=C))
    r.register(Tool("browser.extract_form",
        "Extract all questions/inputs with their options and selectors (quizzes, surveys, forms).",
        {"type": "object", "properties": {}}, extract_form, category=C))
    r.register(Tool("browser.click", "Click an element by CSS selector.",
        {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}, click, category=C))
    r.register(Tool("browser.type", "Type text into an input; submit=true presses Enter.",
        {"type": "object", "properties": {"selector": {"type": "string"}, "text": {"type": "string"},
         "submit": {"type": "boolean", "default": False}}, "required": ["selector", "text"]}, type_text, category=C))
    r.register(Tool("browser.fill_form", "Fill multiple form fields at once.",
        {"type": "object", "properties": {"fields": {"type": "array", "items": {"type": "object",
         "properties": {"selector": {"type": "string"}, "value": {"type": "string"},
         "type": {"type": "string", "enum": ["text", "select", "check", "radio"]}},
         "required": ["selector"]}}}, "required": ["fields"]}, fill_form, category=C))
    r.register(Tool("browser.scroll", "Scroll the page up or down.",
        {"type": "object", "properties": {"direction": {"type": "string", "enum": ["up", "down"]},
         "amount": {"type": "integer", "default": 800}}}, scroll, category=C))
    r.register(Tool("browser.back", "Go back to the previous page.",
        {"type": "object", "properties": {}}, go_back, category=C))
    r.register(Tool("browser.screenshot", "Take a full-page screenshot.",
        {"type": "object", "properties": {"path": {"type": "string", "default": "screenshot.png"}}}, screenshot, category=C))
