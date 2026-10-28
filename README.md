# PPT 汇报制作 Skill

使用真实 PPTX 模板和汇报材料制作可编辑的工作汇报、项目进展、学术或答辩演示文稿。模板原文件不变；来源事实、数字、日期和状态保留在生成记录及备注中。标题、正文、表格、普通图表、流程节点与连接线均为 PowerPoint 原生对象，图片可单独替换。

## 把仓库链接发给 Agent 即可安装

将仓库地址 [DANK1NG111/ppt-report-skill](https://github.com/DANK1NG111/ppt-report-skill) 发给有本地文件和命令权限的 Agent，并说明“安装并配置这个 Skill”。Agent 按 [BOOTSTRAP.md](BOOTSTRAP.md) 克隆到稳定目录、创建独立环境、补齐依赖和渲染引擎、生成中文自检PPT，再注册技能。用户无需逐项手动安装 Python 包。

可以直接把下面这句话发给 Agent：

> 安装并配置 https://github.com/DANK1NG111/ppt-report-skill ，完成实际自检并注册 Skill，然后根据我的材料制作可编辑的汇报 PPT。

已有仓库时，一条命令配置：

```sh
# macOS / Linux；Claude Code把codex改为claude
sh setup.sh --install-system --agent codex
# Windows PowerShell
powershell -File setup.ps1 --install-system --agent codex
```

安装完成必须看到 `.runtime/setup_receipt.json` 为 READY。它表示真实制作与全页渲染通过，不只是依赖文件存在。macOS自动补Office使用已安装的Homebrew，Linux使用apt/dnf，Windows使用winget；权限或网络不满足时会保留具体错误和可重试日志。安装器不覆盖无关的现有Skill。

新安装自带本项目制作的简洁模板；有用户模板时通过 `--template` 指定。仓库不包含本机的西南交通大学私有模板，公开环境也能直接开始制作。

```sh
.venv/bin/ppt-report doctor --smoke
.venv/bin/ppt-report create --materials report.md --request request.json --output output/report.pptx
.venv/bin/ppt-report rehearse --receipt output/pipeline_receipt.json
```

Windows使用 `.venv/Scripts/`。已有 Python 3.11+ 的开发者也可运行 `python -m venv .venv` 后执行 `.venv/bin/python -m pip install -e '.[dev]'`。开发回归涉及本机私有模板时使用完整测试；公开安装验证使用自带模板和公开测试集。

默认生成 `output/final_presentation.pptx`，状态为 `READY_FOR_VISUAL_REVIEW`。输出目录旁的 `pipeline_receipt.json` 指向独立 `build/<run-id>/`，其中保留模板档案、来源事实、冲突、Outline、逐页方案、生成尝试、修复记录和全页渲染。指定 `--output /path/report.pptx` 可另存。`--draft` 只生成未验收草稿。

支持 txt、md、docx、可提取文字的 pdf、pptx、xlsx，以及 `--text` 直接文本。多份材料在 `--materials` 后依次列出；表格转为原生表格，材料内可提取的图片保留为独立对象。不会自动联网搜图。

## 请求格式

```json
{
  "topic": "季度工作汇报",
  "presentation_type": "work_report",
  "audience": "项目组",
  "duration": 5,
  "target_slide_count": 8,
  "required_sections": ["目标", "已完成工作", "成果", "问题", "下一步"],
  "focus_points": ["完成率"],
  "must_include": ["87.6%"],
  "template_mode": "STRICT_TEMPLATE",
  "speaker_notes": true
}
```

目标页数包含封面和结尾。固定目录逐字保留、顺序不变。未给类型、听众、时长、页数时采用保守推断并记录。页数过少不能容纳全部证据时返回 `CONSTRAINT_CONFLICT`。材料不足使用明确待补充项，数字冲突阻止生成。更多图表、图片、表格、流程图输入见 [请求与原生对象格式](references/request_format.md)。

`STRICT_TEMPLATE` 默认复用已有布局及其正文区域，保留主题、背景、Logo、字体、页眉页脚。独立图片可放入已有完整正文区域，防止误用背景或留下空装饰槽位。`FLEXIBLE_TEMPLATE` 允许从已有正文页派生缺少的布局。

## 检查与交付

```bash
.venv/bin/python scripts/validate_presentation.py --input output/final_presentation.pptx --build output/build/RUN_ID
.venv/bin/python scripts/render_presentation.py --input output/final_presentation.pptx --output output/rendered
.venv/bin/ppt-report finalize --receipt output/pipeline_receipt.json --review review.json --pdf
```

复核者实际查看全部渲染页面、核对事实与目录，并用 PowerPoint 打开当前文件确认无修复提示，再按 [复核字段示例](references/review.example.json) 填写 `review.json`。这一步由执行 Skill 的 Codex 或实际复核者完成，不需每阶段向用户确认。交付门禁检查 PPTX 和全部渲染产物哈希、页数、逐页记录及每个 Warning 的处置。成功后输出 `generation_report.md`、`delivery_receipt.json`、`visual_review.json` 与可选 `final_presentation.pdf`。改动文件后必须重新渲染和复核。

生成报告包含页数、模板、汇报类型、材料来源、待补充项、字体替代、兼容性与 QA 结果。控制台错误简明，技术堆栈保留在 `error.log`。字体缺失通常为 Warning；PPTX 字体声明保留，本机渲染替代写入回执。

## 验证与示例

```bash
.venv/bin/python scripts/run_regression.py
.venv/bin/python scripts/run_real_template_cases.py
.venv/bin/python scripts/run_native_case.py
.venv/bin/python scripts/audit_acceptance.py
```

三套固定材料位于 `tests/fixtures/{work_report,project_report,defense}`，均标为 TEST FIXTURE，不代表真实业务或用户个人经历。已验收的输出位于 `output/real_template_cases/`，原生对象综合案例位于 `output/native_case/`。回归独立使用 `output/regression/real_template_cases/`，不会覆盖已复核产物。最终状态与证据见 [FINAL_REPORT](FINAL_REPORT.md) 和 [开发日志](development_log.md)。

## 使用边界

文本提取、事实分类、冲突识别和模板分类采用规则及几何启发式。对语义改写的冲突、特殊母版或复杂组合对象，执行 Skill 的 Codex 仍需核对并修正计划；不得把规则通过当作事实已确认。扫描 PDF 不含 OCR；Excel 公式按原公式读取、不计算；非标准照片 EXIF 方向需先保存到像素。常用原生图表支持 column/bar/line/pie；复杂动画、三维图表和视频不在 V1 范围。

V1.1 的实现、验证证据和平台边界见 [整合验收报告](V1_1_REPORT.md)，两个上游项目的优点与取舍见 [整合分析](references/upstream_analysis.md)。每次完整生成保留 design_spec.json/.md，锁定模板、版式、事实和逐页角色；rehearse导出独立HTML，包含当前/下一页、稳定ID备注和计划/实际计时，可断网使用。

原始用户模板与其副本不纳入 Git 分发。模板作者的署名和授权条件沿用原模板第21页说明；使用该示例模板仍应遵守其原有使用范围。项目代码不会修改原始模板。
