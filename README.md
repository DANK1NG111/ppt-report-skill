# PPT 汇报制作 Skill

基于用户真实 PPTX 模板和材料生成主要对象可编辑、事实可追溯的汇报演示文稿。开发中，验收状态见 `development_log.md`。

Python 3.11 以上。创建虚拟环境后运行 `python -m pip install -e '.[dev]'`。基础验证为 `python -m pytest`，CLI 帮助为 `python scripts/create_presentation.py --help`。

用户原模板始终保留，工作副本位于 `assets/templates/base_template.pptx`。测试内容必须标注 TEST FIXTURE。模板使用须遵守原作者条款。
