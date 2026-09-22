# Nuos 仓库链接迁移审计

日期：2026-09-22。仓库：`Nuos/ai-news-radar`。目标分支：`master`。

## 一、交付结果

链接迁移及回归检查分成 18 笔提交，每笔仅涉及一个文件，累计涉及 17 个不同文件。本报告另作第 19 笔单文件提交，不与代码或其他资料混合提交。

GitHub 比较基线：`c0bc3d4176abda6e7b3d5eed607a72bb92dd0cf4`。

通过最终回归检查的版本：`cebd467463014f6a780926ab621aa8471a83a87e`。

[查看迁移差异](https://github.com/Nuos/ai-news-radar/compare/c0bc3d4176abda6e7b3d5eed607a72bb92dd0cf4...cebd467463014f6a780926ab621aa8471a83a87e)。已核对累计文件差异；除新增的只读测试外，现有文件仅变更链接、链接相关显示文字及对应测试地址。

## 二、迁移范围

GitHub 仓库用户名、安装与维护命令统一为 Nuos；站点与数据入口统一为 `https://nuos.github.io/ai-news-radar/`，没有创建或假设新的自定义域名。

处理范围包括插件配置、中英文 README、两套 Skill 的说明与命令、演示脚本和录制文件、交接文档、版本说明、三份历史宣传稿、旧版页面元数据及前端测试地址。主页、经典界面、RSS 生成器及雷达数据地址已由此前的部署配置迁移，此次纳入回归验证。

原作者姓名、版权和 MIT 许可保留。原作者署名不再链接到旧 GitHub 用户页，避免把原作者名称错误链接到当前维护者。外部独立网站 `learnprompt.pro/skills/` 不属于 GitHub 用户名，保持原地址；其他信源及作者链接不变。

README 页脚中原属旧用户名的其他项目链接也按用户要求换为 Nuos。这只改变链接，不会自动创建这些仓库的 Fork；本次未逐一核验这些其他项目是否在 Nuos 名下存在。

## 三、单文件提交记录

| 提交 | 文件 | 内容 |
|---|---|---|
| `828cc8ca` | `.claude-plugin/marketplace.json` | 插件维护者、仓库及项目主页 |
| `73b286d8` | `skills/radar/README.md` | 雷达 Skill 安装与仓库入口 |
| `e1987630` | `skills/radar/assets/demo.sh` | 演示数据地址 |
| `6f36f826` | `README.md` | 中文说明、徽章、安装和仓库链接 |
| `077b86bc` | `README.en.md` | 英文说明、徽章、安装和仓库链接 |
| `3f15e73d` | `docs/GPT_HANDOFF.md` | 交接文档站点入口 |
| `42bb8d52` | `skills/ai-news-radar/SKILL.md` | 维护工作流命令 |
| `53dcd3ae` | `skills/radar/SKILL.md` | Fork 入口 |
| `b1cb4806` | `tests/test_nuos_links.py` | 第一阶段只读检查与全库盘点 |
| `c3d29260` | `skills/ai-news-radar/README.md` | 伯乐 Skill 说明与部署入口 |
| `43fb2170` | `skills/radar/assets/demo.tape` | 终端演示文字链接 |
| `9700cfa3` | `docs/release-notes-v0.9.md` | 版本说明站点入口 |
| `b1182c3b` | `legacy/index.html` | 旧版页面仓库链接、canonical 与分享元数据 |
| `7537ab55` | `docs/marketing/bole-skill-promo-draft-2026-05-11.md` | 宣传稿项目链接 |
| `845f18a8` | `docs/marketing/bole-skill-wechat-final-2026-05-11.md` | 微信文章项目链接 |
| `11942d2e` | `docs/marketing/bole-skill-wechat-final-reordered-2026-05-11.md` | 重排版文章项目链接 |
| `0d74aaca` | `tests/service-status.test.mjs` | Nuos 项目路径下的前端数据请求测试 |
| `cebd4674` | `tests/test_nuos_links.py` | 全库严格残留检查与迁移输入例外说明 |

## 四、实际验证结果

最终测试运行：[Test Radar / 35725306836](https://github.com/Nuos/ai-news-radar/actions/runs/35725306836)。

日志对应提交 `cebd467463014f6a780926ab621aa8471a83a87e`，Python 测试在 2026-09-22 12:07:34 UTC 输出 `258 passed in 4.78s`，没有警告；Node 测试输出 4 项通过、0 项失败。移动版、经典版和服务状态模块的 JavaScript 语法检查均成功。工作流最终状态为 `success`。

第一阶段盘点实际扫描 121 个已被 Git 跟踪的文本文件，定位其余旧链接；随后逐文件迁移。最终测试 `test_repository_has_no_unmigrated_links` 重新扫描整个 Git 跟踪文本集合，包含生成的 JSON 和历史文档，不再只警告：任何未被说明的旧用户名或旧站点链接都会导致测试失败。该测试在最终版本上已通过。

仅保留以下必需的旧地址输入，不把它们当作线上链接：

| 文件 | 用途 | 已知匹配行数上限 |
|---|---|---|
| `scripts/fork_setup.py` | 识别上游旧配置并替换为本仓库配置的匹配值 | 3 |
| `tests/test_fork_setup.py` | 验证上述迁移行为的旧输入测试样本 | 2 |

如果删除或改写这些旧输入，迁移工具将无法识别上游地址，或使测试失去验证意义。运行入口、说明文档、新闻数据路径均未设豁免。测试还限制豁免文件的匹配行数，防止继续积累无关旧链接。

## 五、验证边界与复现

本次没有改动新闻抓取器、工作流调度、密钥、付费来源或邮箱设置；没有改写 Git 历史、二进制截图或已经发布在仓库外的文章。静态链接一致性通过不等于所有外部链接目标均经过联网可用性检查。

可在已安装开发依赖的仓库中复现：

```bash
python -m pytest -q
python -m pytest -q -s tests/test_nuos_links.py
node --test tests/service-status.test.mjs
node --check assets/app.js
node --check classic/assets/app.js
node --check assets/service-status.js
```

第二条命令会额外显示扫描数量、残留文件及被明确保留的迁移输入位置，不输出文件正文或凭据。
