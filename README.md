# BeePlay AI 阅读站 / AI handbook

- 阅读入口 / Reading index: https://hss1981hss1981-star.github.io/beeplay-ai-handbook/
- 网页与下载文档全文 / Full website and document text: https://hss1981hss1981-star.github.io/beeplay-ai-handbook/llms-full.txt
- 同步状态与校验值 / Sync status and checksums: https://hss1981hss1981-star.github.io/beeplay-ai-handbook/sync-status.json
- 内容来源 / Authoritative source: https://beeplay-product-map.hss1981hss1981.chatgpt.site/

## 同步 / Synchronization

GitHub Actions 每小时第 17 分钟检查公开主站，也可在 Actions 中手动运行。实际执行可能受 GitHub 排队影响，并非即时同步。每次从主站中英文 JSON 重新生成全部章节，复制当前链接的下载资料，并生成 Word/Excel 纯文本。任何下载或校验失败都不会发布，不覆盖上一份成功版本。

GitHub Actions checks the public source at minute 17 of each hour and supports manual runs. Execution may be delayed by GitHub scheduling. Each run rebuilds chapters from bilingual canonical JSON, copies linked downloads, and extracts Office text. A failed fetch or validation prevents deployment, preserving the last successful version.

公开仓库的定时工作流可能在长期无仓库活动后被 GitHub 停用；维护人应关注 Actions 失败通知与同步时间，必要时重新启用。此仓库仅包含公开资料的生成程序，不使用用户密码或额外访问令牌。

Scheduled workflows in public repositories may be disabled by GitHub after prolonged repository inactivity. Maintainers should monitor Actions failures and sync timestamps and re-enable if required. No user password or additional access token is stored here.

## AI 阅读范围 / Reading coverage

纯文本包含全部公开网页和编号释义，`llms-full.txt` 还包含当前 Word/Excel 下载文件的文字。表格文本保留单元格坐标；图示保留原图下载。AI 应明确报告实际读取了哪些章节，不应把仅打开目录当成读完。站点无登录和 JavaScript 要求，但不能解除 AI 工具自身的联网或上下文限制。

The full-text export includes public pages, reference definitions and linked Office documents. Spreadsheet cells retain coordinates; diagrams remain downloadable. AI readers should report actual coverage instead of claiming completeness after opening only the index. No login or JavaScript is required; tool networking and context limits still apply.
