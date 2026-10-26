# V1 验收矩阵

判据来自用户 pasted-text-1.txt。PASS 表示下面列出的当前实现和实际证据共同成立，不表示任意未来材料都无需复核。

| Phase / 要求 | 当前实现与证据 | 结果 |
|---|---|---|
| 0 工程、Git、依赖、CLI、读写 PPTX、pytest | pyproject.toml、scripts 四个入口、smoke 实际生成重读、完整 Git 阶段历史 | PASS |
| 1 真实模板结构、字体/主题/色彩/固定元素、21页分类、档案和全页预览 | template/analyzer.py、classifier.py；assets/template_profiles/base_template.json/.md；assets/previews/21张PNG与PDF；原模板和副本SHA一致 | PASS |
| 2 行为规范、默认推断、强约束、两种模式、至少15请求 | SKILL.md；references/report_rules.md；19项 request_cases.json 与 test_requests.py | PASS |
| 3 txt/md/docx/pdf/pptx/xlsx/直接文本、顺序、数字日期、表格 | content/loader.py、normalizer.py；六格式fixture与8项loader检查 | PASS |
| 4 至少30事实、数字日期单位实体保真、来源、冲突阻断 | 35条known_facts.json；test_facts.py、test_draft.py；中文紧邻数值及同/跨来源冲突 | PASS |
| 5 工作/项目/学术/答辩/custom分类、显式类型优先 | content/report_type.py、test_type.py | PASS |
| 6 Outline、时长总页数、权重、固定目录、四种场景 | planner/outline.py、timing.py、test_outline.py；规划默认推断保存在回执 | PASS |
| 7 逐页信息、来源、口述时间、拆页、去重、至少3完整计划 | slide_planner.py、test_slide_planner.py；三类真实模板build里的slide_plans.json | PASS |
| 8 真实版式与容量评分、至少30匹配案例 | layout/matcher.py、capacity.py；6类×5容量test_matcher.py | PASS |
| 9 中文/英文/混排/数字/bullet/长标题、段落字体继承和强调、有限缩字 | generator/text.py、test_text.py；无容量则报TEXT_OVERFLOW；修复重复pPr并经原生打开验证 | PASS |
| 10 横/竖/方/超大/小图片、contain/裁切/替换、保持比例 | generator/images.py、test_images.py；原生对象案例第8页真实原图与逐页复核 | PASS |
| 11 3×3/5×5/10×5/长文本/数值表、行高列宽、拆表、可编辑与重点标记 | generator/tables.py、test_tables.py、test_pipeline.py；native_case原生table与单元格值核对 | PASS |
| 12 column/bar/line/pie、单位时间series、legend、可修改数据 | generator/charts.py、test_charts.py；原生chart及嵌入XLSX精确数据检查 | PASS |
| 13 流程/时间轴/阶段/组织/架构、原生节点和连接线 | generator/shapes.py；5类test_shapes.py，native_case三节点两连接线 | PASS |
| 14 完整PPTX、顺序、主题、Logo、可编辑、页数、无修复提示、中间结果 | generator/presentation.py；Phase14修正版用户确认无修复提示；最终5套CUA实际打开；每次独立build | PASS |
| 15 文件/内容/对象/字体结构QA、JSON/MD | validator/各模块；test_validator.py、structural坏关系注入；各输出qa_report.json/.md | PASS |
| 16 Office实际PDF→PNG，全页数一致，contact sheet | renderer/render.py；test_render.py；所有验收案例render_receipt及完整页图 | PASS |
| 17 重叠/边界/对齐/密度/字体/比例/标题/对比度/表图可读/模板与渲染文字 | validator/visual.py、tests/visual/test_visual.py；46页实际逐页观察记录 | PASS |
| 18 定位、自动修复、重生成、重渲染、重检、不损事实 | repair.py、test_repair.py；故意越界/文字溢出/图片变形输入实际修复，原文字完全一致 | PASS |
| 19 完整Pipeline及Skill流程 | pipeline.py、delivery.py；test_pipeline.py、test_delivery.py；输入到DELIVERED回执全链路 | PASS |
| 20 工作/长项目/固定目录答辩三套TEST FIXTURE | tests/fixtures/work_report、project_report、defense，request+material+独立expected | PASS |
| 21 同一真实模板三类完整测试 | output/real_template_cases/；8+13+10页，37条来源事实逐字保留 | PASS |
| 22 一键各类回归、明确PASS/FAIL、详细报告 | regression.py、scripts/run_regression.py；output/regression/pytest.xml、pytest.log、regression_report.json | PASS |
| 23 大模板、重复解析/渲染、缓存损坏与变更 | template/profile.py、render.py；test_cache.py、test_render.py；30.8MB模板缓存实测 | PASS |
| 24 简明错误、技术日志、字体兼容说明 | request.py、cli.py、fonts.py；test_errors.py；error.log与font_report.json | PASS |
| 25 默认final_presentation、可选PDF、生成报告8项说明 | cli.py、delivery.py；generation_report.md、delivery_receipt.json；test_delivery.py拒绝过期/未完整复核 | PASS |
| 26 文件/事实/模板/排版/可编辑/全页渲染/零Error/已审Warning/回归 | object_audit.json；五套visual_review与delivery_receipt；PPTX/渲染哈希重新核对通过 | PASS |
| 27 Skill 14项内容、README、开发说明 | SKILL.md、README.md、DEVELOPMENT.md与references；quick_validate通过，文档链接检查 | PASS |
| 28 临时代码清理、无用导入、格式、必要注释类型、全回归 | Ruff F与format、compileall；142项清理后回归通过；CLI默认/显式输出实际运行 | PASS |
| 29 第二模板、不靠当前模板分支 | scripts/run_second_template.py、test_second_template.py；4:3蓝色6页原生打开、来源/目录/页脚保留，生产引擎无需修改 | PASS |
| 30 最终报告13项与完整状态 | FINAL_REPORT.md；release audit和全部阶段日志 | PASS |

核心模型 TemplateProfile、LayoutProfile、SourceFact、PresentationRequest、PresentationOutline、SlidePlan 的所需字段均在 models.py 中，日期/值/单位保留列表，重点内容采用 focus_points 英文字段。可扩展的 payload 携带表格、图表、图片和流程数据。

固定约束另查来源原句、原始模板SHA、母版/主题/版式XML、固定对象几何/图片哈希、嵌入图表工作簿及最终delivery哈希。自动检查无法证明任意语义与所有视觉质量，因此实际逐页查看和原生打开仍是交付门槛。已知限制见FINAL_REPORT，均未冒充已实现能力。
