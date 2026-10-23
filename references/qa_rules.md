# 质量检查

必须检查 ZIP/XML/relationships、活动幻灯片顺序、文本与来源、模板残留、章节覆盖、越界、字号和可编辑对象。Office 实际渲染所有页面，核对页数，检查渲染文字和对象坐标。几何重叠可能是模板设计，不可无条件删除。

自动 QA 无法证明所有视觉质量。最终还要逐页查看渲染图、核对模板，记录 Warning 的处理结论。发现无法可靠自动修复的内容冲突或未知布局时保留报告并阻止标记合格。只在 QA Error 为 0 且人工检查完成后宣布交付验收通过。

交付回执必须绑定当前 PPTX 的 SHA256，并记录逐页观察、来源事实与目录核对、PowerPoint 原生打开是否出现修复提示，以及每项 Warning 的处置。复核者只能在实际查看后填写，不得由生成器默认置为通过。记录字段见 `references/review.example.json`。使用 `ppt-report finalize --receipt output/pipeline_receipt.json --review review.json --pdf` 生成交付回执、生成报告与可选 PDF；文件或渲染改变后旧复核失效。
