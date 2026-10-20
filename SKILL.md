---
name: ppt-report-skill
description: 基于用户提供的真实 PPTX 模板与汇报材料，制作可编辑的工作汇报、项目进展、学术或答辩演示文稿，并渲染和检查全部页面。
---

使用真实模板副本，保护用户原文件。默认 STRICT_TEMPLATE。保留主题、背景、固定 Logo 与主要字体体系。事实与数值必须来自材料，缺失项明确标注，冲突不得自动任选。

输入至少包含真实 PPTX 模板和汇报材料。支持 txt、md、docx、可提取文字的 pdf、pptx、xlsx 与直接文本。请求使用英文 JSON 字段，结构见 `src/ppt_report_skill/models.py` 的 PresentationRequest。按需读取 [汇报规则](references/report_rules.md)、[事实规则](references/content_rules.md)、[类型规则](references/presentation_types.md)。

先读取模板档案和全页预览。保留用户原文件，仅使用副本。主题、背景、Logo、边缘元素和署名沿用模板。STRICT_TEMPLATE 缺少所需布局时明确报错；FLEXIBLE_TEMPLATE 的自动新增布局当前尚未实现，不得把它当作已可用能力。

用材料原句提取事实，记录 source、location、original_text，核对日期、数值、单位与状态。发现冲突先阻止生成，不选取某个来源冒充已确认。缺材料写明确待补充项。固定目录保持文字和顺序。缺页数按时长与事实量推断并记录；显式页数无法承载事实时返回 CONSTRAINT_CONFLICT。

根据 Outline 和 SlidePlan 为每页匹配现有模板页面，克隆原生对象并写入文本。表格、普通图表、流程图均使用原生对象。图表保留单位、时间和嵌入数据工作簿。图片独立放置，保持比例，不自动联网搜图。详见 [布局规则](references/layout_rules.md) 与 [可编辑规则](references/editable_rules.md)。

在 Skill 根目录创建环境并安装依赖后运行：

```bash
python scripts/analyze_template.py --template assets/templates/base_template.pptx
python scripts/create_presentation.py --template assets/templates/base_template.pptx --materials material.md --request request.json --output output/draft.pptx
```

当前版本处于 Phase 14 验收，create 输出为 DRAFT_UNVALIDATED。中间档案、来源事实、冲突、规划和生成记录位于输出旁的 build 目录；这些是审查与后续修复依据，不是最终合格证明。

交付前必须执行 [QA 规则](references/qa_rules.md) 中的文件、内容和可编辑性检查，真实渲染每页并逐页查看，修复后重新生成和渲染。不得仅以文件存在、代码成功或自动检查通过宣布合格。结构 QA、视觉 QA、自动修复和最终交付 Pipeline 仍须按开发计划后续阶段实现验收。
