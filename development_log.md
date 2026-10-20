# Development log

## Phase 0

Status: PASS

Implemented:
- Python 工程、虚拟环境、CLI 与基础 PPTX 读写测试。

Tests:
- `python -m pytest -q`: 1 passed。
- 四个基础 CLI 的 --help 均返回 0。

Problems Found:
- 系统 Python 被 Xcode 许可状态阻挡。

Fixes:
- 使用 Codex 附带 Python 建立项目虚拟环境。

Validation:
- PPTX 创建、读取、保存及文本回读通过；依赖安装和可编辑包入口通过。

Next:
Phase 1

## Phase 1

Status: PASS

Implemented:
- 真实模板结构分析与全页预览

Tests:
- pytest: 2 passed；真实模板 21 页全部渲染，档案 JSON 和 Markdown 已输出。

Problems Found:
- 无新增阻塞。

Fixes:
- 无。

Validation:
- 模板 SHA256 未改变；字体、颜色、母版、固定元素候选、容量和分类均已提取。

Next:
Phase 2

## Phase 2

Status: PASS

Implemented:
- 请求协议和 Skill 行为规范

Tests:
- pytest: 21 passed；19 个请求模拟覆盖缺页数、缺时长、固定目录、答辩、材料过少过多和多来源。

Problems Found:
- 首次预览中文出现方框，已先修复渲染环境。

Fixes:
- 渲染子进程加载 macOS 字体目录并配置中文 fallback；不改 PPTX 字体声明。

Validation:
- 全页已重渲染；请求强约束与异常策略明确。

Next:
Phase 3

## Phase 3

Status: PASS

Implemented:
- 多格式材料读取和来源位置保留

Tests:
- pytest: 29 passed；txt md docx pdf pptx xlsx 和直接文本均验证数字日期保留；docx 段落表格顺序测试通过。

Problems Found:
- 无新增阻塞。

Fixes:
- 无。

Validation:
- 六种格式 fixture 均已创建，空材料和不可提取 PDF 不会伪装成功。

Next:
Phase 4

## Phase 4

Status: PASS

Implemented:
- 保真事实提取与跨材料数值冲突检测

Tests:
- pytest: 32 passed；35 条已知事实逐字、数值、日期、单位、实体和来源校验通过；冲突与不同时间范围测试通过。

Problems Found:
- 无新增阻塞。

Fixes:
- 无。

Validation:
- 提取保持原句，不生成不存在的事实；冲突事实标记 CONFLICT。

Next:
Phase 5
