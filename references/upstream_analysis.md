# 两个上游项目的分析与本项目整合

研究日期为2026-10-26；以下结论基于实际读取源码和规范的固定版本，不依赖项目宣传或Star数量。

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master/tree/78759bf62e9a1ef43e926ff9e50afa4cfe9a63cb)：README、SKILL.md、workflows/routing.md、templates/spec_lock_reference.md、scripts/pptx_delivery_check.py。
- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill/tree/c91369c449d34755d320a8b81d0734000d99d1ab)：README、SKILL.md、references/swiss-layout-lock.md、references/checklist.md及演讲者规范。

## 优点与适配结果

| 上游优点 | 对汇报Skill的价值 | 本次实际实现 |
|---|---|---|
| ppt-master：不同任务有明确路由，策略与执行分开 | 避免把模板填充、自由设计、仅检查和安装混为一谈 | SKILL的安装/模板制作/自带模板/检查/排练路由；doctor/rehearse入口 |
| ppt-master：先有设计规范和机器可读锁定，再生成 | 跨页维持模板、调色板、字体和逐页布局身份，变更可追踪 | design_spec.json/.md、锁定SHA、实际模板页与allowed_layout_ids、事实与payload漂移阻断 |
| ppt-master：文件存在不代表可交付，检查原生结构和引用 | 保留本项目已有原生PPTX、来源、全页渲染和交付门禁，并补安装实际自检 | doctor生成5页中文并检查PPTX→PDF→PNG、依赖和实际渲染状态 |
| guizang：登记版式骨架，图片比例先于图片制作 | 少出现标题轴漂移、空模板框、照片比例错配 | 使用模板登记layout_id；逐页规范保存视觉角色、节奏和图片槽位；用户模板优先 |
| guizang：稳定页面ID绑定备注和计时 | 重新排列页面时排练备注不串页 | 内容身份生成稳定ID；离线单HTML含当前/下一页、备注本地保存、计划与实际计时 |
| guizang：静态回退、明确排练控制 | 实际汇报时不依赖网络或图形加速 | 排练HTML内嵌真实渲染页图，不用CDN或WebGL；暂停/重置、默认关闭自动翻页、后台暂停 |
| 两者：URL/Skill目录让Agent容易接手 | 普通用户不需要逐条安装Python包 | BOOTSTRAP.md、setup.sh/setup.ps1、独立venv、Office检测/系统安装、技能注册与READY回执 |

本项目主要交付仍是可编辑PPTX。排练HTML是实际页图的辅助视图，不能作为原生可编辑性证据。未迁入上游源码、视觉模板、素材、赞助文案或运行时；上述模块按本项目数据模型自行实现。对应上游版本分别含MIT与AGPL-3.0标识，此处只是来源记录。

## 取舍

保留用户“材料正确、固定目录、真实模板、原生对象可编辑、全页QA”的要求。不会把现有严格模板替换成Swiss主题，也不会把网页PPT转成整页图片冒充可编辑PPTX。上游每次启动联网检查更新和多轮强制问答不适用于本项目的连续执行要求；本项目只在用户要求更新时更新仓库，普通可判断选择直接推进。

仓库README首屏指向BOOTSTRAP协议。有Shell和本地文件权限的Agent可从URL完成配置；宿主权限、系统包安装和当前会话技能刷新仍由实际环境决定。此次集成验收使用不含私有资产的本地发布包和全新虚拟环境；后续发布状态见 [项目仓库](https://github.com/DANK1NG111/ppt-report-skill)。
