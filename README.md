# Mainland-SKU — data host

呢個 repo **淨係**做一件事：用 GitHub Pages 出 `data.json`，畀
`https://cloud.marketing.hktvmall.com/testing_mainland/` 嗰個落地頁 `fetch()`。

揀 GitHub Pages 嘅原因（2026-09-15 由真實 RI+ 頁面 origin 實測）：

| Host | ACAO | Cache-Control | 延遲 |
|---|---|---|---|
| **GitHub Pages** | `*` | `max-age=600` | 537 ms |
| `raw.githubusercontent.com` | `*` | `max-age=300` | 2507 ms |
| `cdn.jsdelivr.net` | `*` | `max-age=604800` | 太長，唔用得 |

`data.json` 格式同每日更新流程見主 project 嘅 `docs/pipeline.md`。

**呢度嘅 `data.json` 而家係樣本資料，唔係真價錢。**

`.nojekyll` 係必要嘅，否則 Jekyll 會處理啲檔案。
