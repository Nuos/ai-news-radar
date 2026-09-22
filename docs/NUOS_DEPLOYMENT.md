# Nuos AI News Radar 部署说明

配置日期：2026-09-22。仓库：`Nuos/ai-news-radar`，默认分支：`master`。

## 一、本站入口与运行方式

- 网站：https://nuos.github.io/ai-news-radar/
- 经典界面：https://nuos.github.io/ai-news-radar/classic/
- 数据目录：https://nuos.github.io/ai-news-radar/data/
- RSS：https://nuos.github.io/ai-news-radar/data/feed.xml
- 运行记录：https://github.com/Nuos/ai-news-radar/actions/workflows/update-news.yml

采用 GitHub Actions 抓取、仓库保存快照、GitHub Pages 发布的方式；不要求本地计算机常开，不需要 GPU。Pages 保持 `Deploy from a branch → master → /(root)`。已移除继承自上游的 `CNAME`，不要把上游域名重新写回本站。

## 二、调度与数据

本分支的工作流配置为每小时第 17 分（UTC）执行一次；GitHub 调度可能延迟，不是精确实时任务。支持 Actions 页面手动 `Run workflow`。更新工作流、脚本、测试、依赖、公开 OPML 或 persona 文件也会触发执行。数据提交本身不形成递归运行。

展示窗口为 24 小时，归档保留 21 天，OPML 默认读取公开示例，最多 10 个订阅源。原有内容分类、故事合并、双界面与 persona 管线保持使用。

上游 README 的“每 30 分钟”说明与本分支配置不同，以 `.github/workflows/update-news.yml` 为准。

## 三、凭据与安全

基础运行不需要 API Key。本次配置未写入任何密钥，没有配置付费源或私有邮箱。X API、SocialData、TikHub 的工作流开关默认明确为 `0`，添加 Key 本身不会自动开启；后续启用需自行明确设置对应 Repository Variable 为 `1` 并评估费用。

邮箱抓取、正文读取、邮箱数据混入主数据、邮箱摘要公开发布在此公开工作流中固定关闭。不要提交 `.env`、`feeds/follow.opml`、cookies 或邮箱正文。

DeepSeek 为可选增强：只在自行添加 `DEEPSEEK_API_KEY` Secret 后调用；可用 `DEEPSEEK_MODEL` Variable 选择服务商实际支持的模型。不配置时使用规则评分与原有免费降级路径，不会获得完整 LLM 点评与推荐理由。没有在本次配置中新增此密钥。

## 四、配置与验收机制

`scripts/fork_setup.py configure` 将主页及经典界面的本站元数据、RSS 站点地址、雷达 Skill 的 BASE_URL 和原始文件回退地址改为 Nuos；在 README 顶部加入本站入口，保留上游说明与归属。操作可重复执行；发现不是上游域名的自定义 CNAME 时会停止，避免误删用户域名。

工作流在非定时触发时执行 Python 语法检查、完整 pytest 测试和 JavaScript 语法检查；生成后拒绝发布空快照。数据提交后明确请求 Pages 重建，再检查主页、经典界面、4 个 JSON 数据端点及 RSS，共 7 个端点。只有线上最新数据的 generated_at 不早于本轮数据时，部署验证才成功。

抓取器会独立记录各信源的失败；“网站部署成功”不表示每个外部信源都抓取成功，应同时检查 `data/source-status.json`。验证器检查 HTTP 与数据新鲜度，不替代交互式浏览器测试。

## 五、故障恢复

若 GitHub 保持 fork 的工作流为禁用状态，在 Actions 页面启用，然后手动运行；已登录 GitHub CLI 时可执行：

```bash
gh workflow enable update-news.yml --repo Nuos/ai-news-radar
gh workflow run update-news.yml --repo Nuos/ai-news-radar --ref master
gh run list --repo Nuos/ai-news-radar --workflow update-news.yml --limit 5
```

如 `Rebuild GitHub Pages` 失败，检查 Pages 是否仍为 `master` 根目录、仓库是否允许 Actions，以及 workflow 是否获准 `contents: write` 和 `pages: write`；不要用明文 Personal Access Token 解决。

如校验显示旧快照，先检查 Pages 构建记录；不要仅以抓取步骤成功判断网站已经更新。

## 六、本地运行

```bash
git clone --depth 1 https://github.com/Nuos/ai-news-radar.git
cd ai-news-radar
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/fork_setup.py configure
python scripts/update_news.py --output-dir data --window-hours 24 --archive-days 21 --rss-opml feeds/follow.example.opml --rss-max-feeds 10
python scripts/persona_score.py --data-dir data
python scripts/generate_feed.py --data-dir data
python -m http.server 8080 --bind 127.0.0.1
```

浏览器打开 `http://127.0.0.1:8080/`。本地执行不会自动推送 GitHub。运行结果以 Actions 的实际状态和日志为准，本说明不预先宣称尚未完成的运行成功。
