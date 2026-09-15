#!/usr/bin/env python3
"""驗證 GitHub Pages 出到 data.json,而且 RI+ 個頁 fetch 得到。

呢個係 hosting 驗證嘅唯一標準:唔係 curl 到就算,要由真實 published page
嘅 origin 發 fetch。CORS 係瀏覽器行為,curl 睇唔出 preflight 同 redirect 問題。

用法:python3 verify_pages.py
"""
import subprocess
import sys

RI_PAGE = "https://cloud.marketing.hktvmall.com/testing_mainland/"
PAGES_URL = "https://fungtk.github.io/Mainland-SKU/data.json"


def curl_headers(url: str) -> dict[str, str]:
    out = subprocess.run(
        ["curl", "-s", "-D-", "-o", "/dev/null", "--max-time", "20",
         "-H", "Origin: https://cloud.marketing.hktvmall.com", url],
        capture_output=True, text=True).stdout
    head = {}
    for line in out.splitlines():
        if line.startswith("HTTP/"):
            head["status"] = line.split()[1]
        elif ":" in line:
            k, v = line.split(":", 1)
            head[k.strip().lower()] = v.strip()
    return head


def main() -> int:
    print("1. curl 睇 header")
    h = curl_headers(PAGES_URL)
    status = h.get("status", "?")
    acao = h.get("access-control-allow-origin")
    cache = h.get("cache-control")
    print(f"   status={status}  ACAO={acao}  cache-control={cache}")
    if status != "200":
        print(f"   ✗ 唔係 200。Pages 可能仲 deploy 緊,等一陣再試。")
        return 1
    if not acao:
        print("   ✗ 冇 Access-Control-Allow-Origin。")
        return 1

    print("2. 由真實 RI+ 頁面 origin 發 fetch")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("   ! 冇 playwright,跳過。呢步先係決定性測試。")
        return 1
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page()
        pg.goto(RI_PAGE, wait_until="domcontentloaded", timeout=45000)
        res = pg.evaluate("""async (url) => {
          try {
            const t0 = performance.now();
            const r = await fetch(url, { cache: 'no-store' });
            const j = await r.json();
            return { ok: r.ok, status: r.status, redirected: r.redirected,
                     ms: Math.round(performance.now() - t0),
                     rows: Array.isArray(j.rows) ? j.rows.length : null,
                     generated_at: j.generated_at || null };
          } catch (e) { return { error: String(e).slice(0, 120) }; } }""", PAGES_URL)
        b.close()
    print("  ", res)
    if not res.get("ok"):
        print("   ✗ RI+ 個頁 fetch 唔到。")
        return 1
    if res.get("redirected"):
        print("   ✗ 有 redirect。RI+ 個 S3 就係死喺 redirect 度。")
        return 1
    if not res.get("rows"):
        print("   ✗ fetch 到但 rows 係空。")
        return 1
    print(f"\n✓ 通過。{res['rows']} 行,{res['ms']} ms,冇 redirect。")
    print(f"  PT_BASE 要填:\"https://fungtk.github.io/Mainland-SKU/\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
