# 项目执行入口

本项目将真实材料转为可编辑的汇报 PPTX。制作任务先读 [SKILL.md](SKILL.md)。用户从仓库网址发起安装时先读 [BOOTSTRAP.md](BOOTSTRAP.md)，执行安装、自检和技能注册，不能只复述命令。

默认简体中文。事实、数字、日期、状态及固定目录不改写；模板原文件不修改；最终交付需要实际全页渲染、逐页复核及可编辑性验证。环境自检 READY 不等于演示文稿 DELIVERED。

改代码先检查当前状态；独立测试使用隔离目录。测试与改动规模相称。`pytest` 为本地完整检查；没有用户私有模板时用 `pytest -m 'not private_template'` 运行公开测试集。`python -m ppt_report_skill.cli doctor --smoke` 提供不依赖私有资产的完整制作与渲染自检。发布包使用 `scripts/package_release.py`，不包括用户模板、output、虚拟环境和本机配置。

若任务复杂到值得独立前向验证，可委派子 Agent 在隔离目录按真实用户请求运行 Skill；给它输入与完成判据，不预告预期答案，由主 Agent检查实际产物。
