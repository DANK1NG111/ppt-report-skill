# PPT 汇报制作 Skill

基于用户真实 PPTX 模板和材料生成主要对象可编辑、事实可追溯的汇报演示文稿。开发中，验收状态见 `development_log.md`。

Python 3.11 以上。创建虚拟环境后运行 `python -m pip install -e '.[dev]'`。基础验证为 `python -m pytest`，CLI 帮助为 `python scripts/create_presentation.py --help`。

用户原模板始终保留，工作副本位于 `assets/templates/base_template.pptx`。测试内容必须标注 TEST FIXTURE。模板使用须遵守原作者条款。

当前 Phase 0–13 已通过，Phase 14 正在验收。`create` 生成草稿，尚未接入后续结构 QA、视觉 QA 和自动修复；不能据此声称 V1 已完成。

```bash
python scripts/analyze_template.py --template assets/templates/base_template.pptx
python scripts/create_presentation.py --materials report.md --request request.json --output output/draft.pptx
```

`request.json` 示例：

```json
{"topic":"季度工作汇报","presentation_type":"work_report","duration":5,"target_slide_count":8,"template_mode":"STRICT_TEMPLATE"}
```

模板档案与预览分别位于 `assets/template_profiles/` 和 `assets/previews/`。生成草稿旁的 `build/` 包含来源事实、目录、逐页计划和对象写入记录。冲突时保存 conflicts.json 并拒绝生成。

macOS 若系统 Python 提示 Xcode 许可问题，可使用 Codex 应用附带 Python 建立 `.venv`，随后统一使用 `.venv/bin/python`。渲染依赖 LibreOffice/soffice，支持 `PPT_REPORT_SOFFICE` 指定路径；渲染时的字体替代会记录在 render_receipt.json，PPTX 原字体声明保留。
