# Nuos · GitHub 项目主页

一个浅色、响应式的静态项目主页，适用于 `https://nuos.github.io/`。

## 一、页面内容

- 固定展示 AI News Radar 与 OpenMontage，简介根据各自公开 README 整理，不将收录项目一概标作 Nuos 原创。
- AI News Radar 在线入口：<https://nuos.github.io/ai-news-radar/>。
- GitHub 入口：<https://github.com/Nuos>。
- X / Twitter 入口：<https://x.com/_nUOs_>。
- 最近项目区在页面打开时匿名读取 GitHub 最近更新的 12 个公开仓库，排除上方项目、主页仓库和已归档/禁用仓库后，最多显示 6 项。这不是完整仓库清单。
- 最近项目的简介直接使用 GitHub 仓库的 `description`；没有简介时显示提示，不编造说明。修改仓库 About → Description 即可更新此区域的简介。

固定简介来源：

- <https://github.com/Nuos/ai-news-radar#readme>
- <https://github.com/Nuos/OpenMontage#readme>

## 二、运行方式与边界

`index.html` 包含样式和脚本，不需要安装依赖、构建前端或提供 API Key。没有外部字体、统计脚本或第三方推广链接。最近项目只调用公开 GET 接口，明确使用 `credentials: omit`，不发送 token 或账户 Cookie。

GitHub API 请求 8 秒后超时；失败或限额不足时保留固定项目入口。手动刷新失败时，保留本页上次成功读取的列表。关闭 JavaScript 也能使用固定项目和个人链接。

最新项目由浏览器现场读取，不修改 GitHub 仓库文件，不依赖后台定时任务；固定项目简介需要编辑 HTML。

## 三、根域名部署

GitHub 用户站点必须使用专用仓库 `Nuos/nuos.github.io`。新闻项目站点 `/ai-news-radar/` 与根域名主页是两个独立站点，新增用户主页不需要移动或覆盖新闻项目。

本次准备页面时，专用仓库查询返回 404；当前连接没有新建仓库操作，因此页面文件准备与预览发布不代表根域名已经上线。

部署步骤：

1. 在 Nuos 账号下创建公开仓库 `nuos.github.io`，勾选 Add README。
2. 将本包的 `index.html` 和 `.nojekyll` 放在该仓库默认分支的根目录。可将本 README 作为维护说明。
3. Settings → Pages → Build and deployment：选择 **Deploy from a branch**，选择实际默认分支（通常为 `main`）及 **/(root)**，保存。
4. 等待 Pages 构建成功，再访问 <https://nuos.github.io/>。不要填写其他人的 CNAME 或自定义域名。

官方说明：

- <https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>
- <https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages>
- <https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user>

## 四、现有项目内预览

页面可以独立放在 `Nuos/ai-news-radar` 的 `home/index.html`，预览地址为：

<https://nuos.github.io/ai-news-radar/home/>

`home/` 只是预览目录，不是用户根域名；不会覆盖 `ai-news-radar/index.html`。全部项目入口使用明确的绝对地址，因此将同一 HTML 移到用户站点根目录不需要重新调整链接。

## 五、本地查看

直接打开 `index.html`，或在本目录执行：

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

浏览器访问 `http://127.0.0.1:8080/`。公开 API 受当前网络、浏览器策略及 GitHub 限额影响；静态内容不依赖该 API。

## 六、验证记录

2026-09-22，在 Chromium 中执行 8 项本地检查，全部通过：固定链接与 HTML 结构、公开仓库筛选及数量上限、不可信描述按文本渲染、接口失败降级、刷新失败保留已加载内容、异常响应处理、手机端无横向溢出、禁用 JavaScript 后固定入口可用。

动态接口测试使用明确的模拟响应，未将测试仓库写入页面，也不代表已验证访问者网络下的 GitHub API 可达性。已检查桌面与手机截图。网站是否已发布应以对应 Pages 部署记录与实际访问结果为准。
