# 开发与验证

按用户计划 Phase 0–30 顺序实现、测试、修复、验收后更新 `development_log.md`。每阶段有独立 Git 提交，最终证据以 `FINAL_REPORT.md`、回归日志和哈希绑定交付回执为准。

## 模块边界

- template：真实 PPTX 分析、页面分类、字体/色彩/固定对象与容量档案；缓存按模板内容和分析器代码版本失效。
- content：格式加载、规范化、精确来源事实和保守冲突检测。
- planner/layout：类型、目录、时长、事实权重、逐页拆分和版式评分。
- generator：克隆主题/母版/关系；写入原生文本、表格、图表、图片、节点和连接线。
- validator/renderer/repair：文件、内容、对象、字体与渲染证据检查，有限自动修复后再次渲染。
- pipeline/delivery：独立构建目录、错误回执、逐页复核门禁与最终报告。

## 常用检查

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/run_regression.py
.venv/bin/python scripts/run_real_template_cases.py
.venv/bin/python scripts/run_native_case.py
.venv/bin/python scripts/audit_acceptance.py
```

回归命令包含全部 pytest 分类、JUnit、三类真实模板生成与实际 Office 全页渲染；报告位于 `output/regression/`。单项修改先执行相关测试，有新修改、失败或未解疑点时再扩大检查。需要渲染的测试使用 render marker；最终验收不能跳过。

`record_phase.py` 仅记录已经通过的阶段；它不会代替测试或审查证据。故障输出保存在独立 build 供定位，临时转换文件由 TemporaryDirectory 自动清理。原始模板、用户输出、环境与缓存不提交 Git。

## 原生兼容性经验

TextFrame.clear() 仍可能保留第一段的段落属性；写入复制样式前必须移除旧 pPr，避免重复节点引发 PowerPoint 修复。克隆 slide 时需要同时重映射 shapes 和背景的关系，保留主题及固定对象。已在真实 PowerPoint 打开修复后的 Phase14 文件及最终四套文件，未出现修复提示。

Office 渲染在独立临时 profile 内运行，先生成全新 PDF 再复制，避免旧 PDF 被误认为成功结果。缓存核对所有产物 SHA256。macOS headless 字体发现显式配置系统字体目录，PPTX 字体声明保持原样，渲染替代另记。

固定目录检查使用连续章节序列，而不是去重后的章节集合；原生对象插入其所属章节末尾。模板全宽半页背景需受到固定对象保护，独立照片应进入已有正文区域。规则通过后仍需逐页看图，不能以文件存在替代验收。
