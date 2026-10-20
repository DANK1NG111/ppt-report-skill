"""Versioned JSON-serializable contracts shared by all pipeline stages."""
from dataclasses import asdict, dataclass, field
from pathlib import Path
import json


def save_json(value, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(value) if hasattr(value, "__dataclass_fields__") else value,
                               ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class LayoutProfile:
    layout_id: str
    layout_name: str
    layout_type: str
    source_slide: int
    title_box: dict | None = None
    subtitle_box: dict | None = None
    body_boxes: list[dict] = field(default_factory=list)
    image_boxes: list[dict] = field(default_factory=list)
    chart_boxes: list[dict] = field(default_factory=list)
    table_boxes: list[dict] = field(default_factory=list)
    fixed_shapes: list[dict] = field(default_factory=list)
    recommended_content_size: int = 0
    max_content_size: int = 0
    visual_density: float = 0.0
    secondary_tags: list[str] = field(default_factory=list)
    content_shapes: list[dict] = field(default_factory=list)


@dataclass
class TemplateProfile:
    template_path: str
    sha256: str
    slide_width: int
    slide_height: int
    aspect_ratio: float
    masters: list[dict]
    layouts: list[LayoutProfile]
    fonts: list[str]
    theme_fonts: list[str]
    colors: list[str]
    theme_colors: dict
    backgrounds: list[dict]
    fixed_elements: list[dict]
    logos: list[dict]
    headers: list[dict]
    footers: list[dict]
    page_number_style: list[dict]
    placeholders: list[dict]
    example_slides: list[dict]
    layout_capacities: dict
    editable_elements: dict
    font_fallbacks: dict = field(default_factory=dict)
    schema_version: int = 1

    @classmethod
    def from_dict(cls, data):
        return cls(**{**data, "layouts": [LayoutProfile(**x) for x in data["layouts"]]})


@dataclass
class MaterialBlock:
    source: str
    location: str
    kind: str
    text: str
    section: str = ""
    rows: list[list[str]] = field(default_factory=list)
    image_path: str | None = None


@dataclass
class SourceFact:
    id: str
    content: str
    source: str
    location: str
    category: str
    original_text: str
    date: list[str] = field(default_factory=list)
    value: list[str] = field(default_factory=list)
    unit: list[str] = field(default_factory=list)
    importance: float = 1.0
    confidence: float = 1.0
    section: str = ""
    status: str = "VERIFIED_SOURCE"


@dataclass
class PresentationRequest:
    topic: str = "汇报"
    presentation_type: str | None = None
    audience: str | None = None
    duration: float | None = None
    target_slide_count: int | None = None
    required_sections: list[str] = field(default_factory=list)
    required_order: bool = True
    focus_points: list[str] = field(default_factory=list)
    must_include: list[str] = field(default_factory=list)
    template_mode: str = "STRICT_TEMPLATE"
    speaker_notes: bool = True


@dataclass
class PresentationOutline:
    title: str
    presentation_type: str
    estimated_duration: float
    target_slide_count: int
    sections: list[str]
    section_weights: dict
    assumptions: list[str] = field(default_factory=list)


@dataclass
class SlidePlan:
    slide_number: int
    section: str
    slide_type: str
    title: str
    core_message: str
    supporting_facts: list[str]
    source_refs: list[dict]
    visual_type: str = "text"
    layout_requirement: str = "title_content"
    importance: float = 1.0
    estimated_speaking_time: float = 30.0
    layout_id: str | None = None
    payload: dict = field(default_factory=dict)


@dataclass
class Issue:
    code: str
    severity: str
    message: str
    slide: int | None = None
    shape_id: int | None = None
    repaired: bool = False


class ReportError(Exception):
    """Stable machine code plus concise user-facing explanation."""
    def __init__(self, code, message, detail=""):
        self.code, self.message, self.detail = code, message, detail
        super().__init__(f"{code}: {message}")
