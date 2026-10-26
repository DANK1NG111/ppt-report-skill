# 请求与原生对象格式

请求字段以 `PresentationRequest` 为准，未知字段报错。`duration` 单位为分钟；`target_slide_count` 为总页数；`required_sections` 不得重复；`required_order` 默认 true（有固定目录时始终保持顺序）；`focus_points` 提高对应事实权重；`must_include` 必须能在材料事实中找到。类型为 work_report/project_progress/academic_report/defense/custom。

`visuals` 是对象列表，每项有 `type`、可选 `section`、`title`。section 必须是最终目录中的原始名称，省略时使用第一章。以下数据本身属于用户提供的输入，原样记录为来源，不自动推断数值。

```json
{
  "topic": "TEST FIXTURE",
  "presentation_type": "custom",
  "required_sections": ["数据", "流程", "图片"],
  "visuals": [
    {"type":"table","section":"数据","title":"测试结果","data":{"rows":[["项目","数量"],["通过","16"],["待处理","2"]]}},
    {"type":"chart","section":"数据","title":"分类数量","data":{"kind":"column","title":"分类数量","unit":"个","time":"2026年9月","categories":["甲","乙","丙"],"series":[{"name":"数量","values":[12,18,9]}]}},
    {"type":"diagram","section":"流程","title":"执行流程","data":{"kind":"process","nodes":[{"id":"a","label":"收集材料"},{"id":"b","label":"核对事实"},{"id":"c","label":"交付成果"}],"edges":[["a","b"],["b","c"]]}},
    {"type":"image","section":"图片","title":"现场图","path":"/absolute/path/photo.jpg","fit":"contain"}
  ]
}
```

图表 kind 支持 column、bar、line、pie；类别与每个 series.values 等长，数值必须有限，series 名称不能重复；必须给单位和时间。饼图只接受单系列、少量非负类别。

流程 kind 支持 process、timeline、stages、organization、architecture。节点 id 唯一，edge 引用已存在节点；层次图不能有循环。省略 edges 时按输入节点顺序连接。

图片 fit 支持 contain、crop、center_crop、fill。后三种保持比例并裁切，均不拉伸。图片路径按当前运行目录解析，建议绝对路径。

材料表格自动拆行、拆列并重复表头/首列。显式 visuals 表格超出容量会报告 TABLE_OVERFLOW；先按真实证据分成多个 visual，不能丢弃行列。大量图形、长标签或固定页数过少时，先拆成可容纳的证据页，保留原始数据。
