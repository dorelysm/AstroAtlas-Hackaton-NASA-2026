"""Records the silent README demo video and takes the README screenshots of the AstroAtlas app with Playwright.

    pip install playwright pymupdf        # Chrome must be installed (channel="chrome")
    python tools/demo/record_demo.py video  --out build/demo          # raw .webm + scenes.json (timestamps)
    python tools/demo/record_demo.py shots  --out docs/images         # README screenshots
    python tools/demo/record_demo.py both   --url http://localhost:8765/

By default it runs against the production app, so the video shows the real deployment and the live NASA imagery. The video has
no voice: every scene carries an on-screen caption. `tools/demo/make_media.py` turns the raw recording into MP4 and GIF.
"""
import argparse
import json
import pathlib
import time

from playwright.sync_api import Page, sync_playwright

PROD = "https://app-production-6cc653bd.up.railway.app/"
CURSOR_JS = """
(() => {
  if (document.getElementById('astro-cursor')) return;
  const c = document.createElement('div'); c.id = 'astro-cursor';
  c.style.cssText = 'position:fixed;z-index:2147483647;width:22px;height:22px;border-radius:50%;background:rgba(255,140,66,.55);'
    + 'border:2px solid #fff;pointer-events:none;transform:translate(-50%,-50%);left:-50px;top:-50px;transition:transform .12s';
  document.body.appendChild(c);
  const cap = document.createElement('div'); cap.id = 'astro-cap';
  cap.style.cssText = 'position:fixed;z-index:2147483646;left:50%;bottom:26px;transform:translateX(-50%);max-width:82%;'
    + 'padding:12px 22px;border-radius:12px;background:rgba(14,17,23,.88);color:#fff;font:600 21px/1.35 "Source Sans Pro",Segoe UI,sans-serif;'
    + 'text-align:center;border:1px solid #FF8C42;opacity:0;transition:opacity .35s;pointer-events:none;box-shadow:0 6px 24px rgba(0,0,0,.45)';
  document.body.appendChild(cap);
  document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  document.addEventListener('mousedown', () => { c.style.transform = 'translate(-50%,-50%) scale(.6)'; }, true);
  document.addEventListener('mouseup', () => { c.style.transform = 'translate(-50%,-50%) scale(1)'; }, true);
})();
"""


class Recorder:
    def __init__(self, page: Page):
        self.page = page
        self.t0 = time.time()
        self.scenes = []

    def start(self):
        self.t0 = time.time()

    def prep(self):
        self.page.evaluate(CURSOR_JS)

    def caption(self, text: str | None):
        self.page.evaluate("t => {const c=document.getElementById('astro-cap'); if(!c) return; "
                           "if(t){c.textContent=t;c.style.opacity=1}else{c.style.opacity=0}}", text)

    def scene(self, name: str, text: str | None):
        self.scenes.append({"name": name, "t": round(time.time() - self.t0, 2)})
        self.caption(text)

    def pause(self, s: float):
        self.page.wait_for_timeout(int(s * 1000))

    def scroll_to(self, locator, block: str = "start"):
        locator.first.evaluate("(e, b) => e.scrollIntoView({behavior: 'smooth', block: b})", block)
        self.pause(1.3)

    def click(self, locator, settle: float = 2.5):
        el = locator.first
        el.scroll_into_view_if_needed()
        box = el.bounding_box()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=28)
        self.pause(0.35)
        self.page.mouse.down()
        self.pause(0.08)
        self.page.mouse.up()
        self.pause(settle)


def open_app(pw, url: str, size: dict, video_dir: str | None = None, mobile: bool = False):
    browser = pw.chromium.launch(channel="chrome")
    kw = {"viewport": size, "accept_downloads": True}
    if video_dir:
        kw |= {"record_video_dir": video_dir, "record_video_size": size}
    if mobile:
        kw |= {"device_scale_factor": 2, "is_mobile": True, "has_touch": True}
    ctx = browser.new_context(**kw)
    page = ctx.new_page()
    page.goto(url + "?lang=en")
    page.wait_for_selector("img[alt^='Orbital view of']", timeout=120000)
    page.wait_for_timeout(2500)
    return browser, ctx, page


def record_video(url: str, out: pathlib.Path):
    out.mkdir(parents=True, exist_ok=True)
    size = {"width": 1280, "height": 720}
    t_ctx = time.time()
    with sync_playwright() as pw:
        browser, ctx, page = open_app(pw, url, size, video_dir=str(out))
        t_open = time.time()
        r = Recorder(page)
        r.prep()
        r.start()

        r.scene("intro", "AstroAtlas: find places on Earth that resemble Moon and Mars sites")
        r.pause(4.5)

        r.scene("featured", "A featured case: rehearse Mars lava-field operations with two Earth candidates")
        r.scroll_to(page.get_by_text("Featured case:"), "start")
        r.pause(3.0)
        r.click(page.get_by_role("button", name="Explore this case"), settle=3.5)

        r.scene("map", "An interactive map ranks Earth places by similarity to the chosen Mars site")
        r.scroll_to(page.get_by_role("heading", name="Places similar to Jezero (Mars)"), "start")
        r.pause(3.0)
        r.caption("Switch the map to field-site risk to see where operations are easier")
        r.click(page.get_by_text("Field risk", exact=True), settle=3.5)
        r.click(page.get_by_text("Similarity", exact=True), settle=1.5)

        r.scene("profile", "Each place gets a profile with NASA orbital views at the same 150 km scale")
        r.scroll_to(page.get_by_text("Visual comparison:"), "start")
        r.pause(4.0)
        r.click(page.get_by_text("Cloud-free (Blue Marble)"), settle=4.0)
        r.click(page.get_by_text("One day (MODIS)"), settle=3.0)

        r.scene("aspects", "Match by aspect and indicative field-site risks, with the limits of the analogy")
        page.mouse.wheel(0, 520)
        r.pause(3.5)
        r.scroll_to(page.get_by_text("Field-site risks (indicative)"), "start")
        r.pause(4.5)

        r.scene("sensitivity", "A sensitivity check shows how the rank changes when each aspect is removed")
        r.click(page.get_by_text("How robust is this place's rank?"), settle=2.5)
        r.scroll_to(page.get_by_text("How robust is this place's rank?"), "start")
        r.pause(5.5)

        r.scene("pdf", "Download a PDF site report for a geologist: match, reliability, risks and imagery")
        r.scroll_to(page.get_by_text("Download site report (PDF)"), "center")
        r.pause(1.0)
        with page.expect_download(timeout=60000) as dl:
            r.click(page.get_by_role("button", name="Download site report (PDF)"), settle=0.5)
        pdf_path = out / "report.pdf"
        dl.value.save_as(str(pdf_path))
        import base64
        import pymupdf
        png = pymupdf.open(str(pdf_path))[0].get_pixmap(dpi=85).tobytes("png")
        page.evaluate("""b64 => {const d=document.createElement('div'); d.id='astro-pdf';
          d.style.cssText='position:fixed;inset:0;z-index:2147483000;background:rgba(14,17,23,.92);display:flex;align-items:center;justify-content:center';
          d.innerHTML='<img style="height:94%;border-radius:6px;box-shadow:0 8px 40px #000" src="data:image/png;base64,'+b64+'">';
          document.body.appendChild(d)}""", base64.b64encode(png).decode())
        r.pause(5.5)
        page.evaluate("document.getElementById('astro-pdf').remove()")
        r.pause(0.8)

        r.scene("filters", "Narrow the search by volcanic terrain and by world region")
        r.scroll_to(page.get_by_text("Volcanic terrain only (basalt)"), "center")
        r.pause(2.0)
        page.get_by_test_id("stMultiSelect").locator("input").click()
        for _ in range(7):
            page.keyboard.press("Backspace")
            r.pause(0.35)
        page.keyboard.press("Escape")
        r.pause(4.0)

        r.scene("language", "Available in English and Spanish")
        page.evaluate("window.scrollTo(0,0); document.querySelector('section.stMain')?.scrollTo(0,0)")
        r.click(page.get_by_text("Español", exact=True), settle=3.5)
        r.click(page.get_by_text("English", exact=True), settle=2.5)

        r.scene("outro", "Open source (MIT) · built with open NASA, ESA and USGS data · github.com/dorelysm/AstroAtlas-Hackaton-NASA-2026")
        r.pause(5.5)
        r.caption(None)
        r.pause(0.6)

        end = time.time() - t_open
        video = page.video
        ctx.close()
        browser.close()
        webm = pathlib.Path(video.path())
        webm.rename(out / "demo.webm")
    trim = round(t_open - t_ctx, 2)          # seconds of loading at the start of the raw video to cut off
    meta = {"trim_start": trim, "duration": round(end, 2),
            "scenes": [{"name": s["name"], "t": round(s["t"] + trim, 2)} for s in r.scenes]}   # absolute times in the raw video
    (out / "scenes.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("video:", out / "demo.webm", "| scenes:", len(r.scenes), "| recorded seconds after load:", round(end, 1))


def take_shots(url: str, out: pathlib.Path):
    out.mkdir(parents=True, exist_ok=True)
    import pymupdf
    size = {"width": 1440, "height": 900}
    with sync_playwright() as pw:
        browser, ctx, page = open_app(pw, url, size)
        r = Recorder(page)
        page.screenshot(path=str(out / "01-home.png"))                                  # steps + featured card
        r.scroll_to(page.get_by_role("heading", name="Places similar to Jezero (Mars)"), "start")
        r.pause(2.5)
        page.screenshot(path=str(out / "02-map-similarity.png"))
        r.click(page.get_by_text("Field risk", exact=True), settle=3.0)
        page.screenshot(path=str(out / "03-map-risk.png"))
        r.click(page.get_by_text("Similarity", exact=True), settle=2.0)
        r.scroll_to(page.get_by_text("Visual comparison:"), "start")
        r.pause(4.0)
        page.screenshot(path=str(out / "04-profile.png"))
        r.scroll_to(page.get_by_text("Field-site risks (indicative)"), "start")
        r.pause(1.5)
        page.get_by_text("How robust is this place's rank?").click()
        r.pause(2.5)
        page.mouse.wheel(0, 120)
        r.pause(1.5)
        page.screenshot(path=str(out / "05-risks-sensitivity.png"))
        with page.expect_download(timeout=60000) as dl:
            page.get_by_role("button", name="Download site report (PDF)").click()
        dl.value.save_as(str(out / "report.pdf"))
        pymupdf.open(str(out / "report.pdf"))[0].get_pixmap(dpi=110).save(str(out / "06-pdf-report.png"))
        (out / "report.pdf").unlink()
        ctx.close()
        browser.close()
        browser, ctx, page = open_app(pw, url, {"width": 390, "height": 844}, mobile=True)
        page.screenshot(path=str(out / "07-mobile.png"))
        ctx.close()
        browser.close()
    print("screenshots in", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["video", "shots", "both"])
    ap.add_argument("--url", default=PROD)
    ap.add_argument("--out", default=None, help="output folder (default: build/demo for video, docs/images for shots)")
    a = ap.parse_args()
    if a.mode in ("video", "both"):
        record_video(a.url, pathlib.Path(a.out or "build/demo"))
    if a.mode in ("shots", "both"):
        take_shots(a.url, pathlib.Path(a.out or "docs/images") if a.mode == "shots" else pathlib.Path("docs/images"))
