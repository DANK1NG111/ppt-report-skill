"""Command line entry points; extended by subsequent development phases."""
import argparse
from pathlib import Path
from pptx import Presentation


def main(argv=None):
    parser = argparse.ArgumentParser(description="基于真实模板制作可编辑汇报 PPT")
    parser.add_argument("command", choices=["analyze", "create", "validate", "render", "regression", "smoke"])
    parser.add_argument("--output", default="output/smoke.pptx")
    parser.add_argument("--template", default="assets/templates/base_template.pptx")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        from .template.analyzer import analyze_template
        from .renderer.render import render_presentation
        profile = analyze_template(args.template, "assets/template_profiles/base_template.json")
        result = render_presentation(args.template, "assets/previews")
        print(f"PASS: {len(profile.layouts)} pages; {result['page_count']} rendered")
        return 0
    if args.command == "smoke":
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = "TEST FIXTURE"
        prs.save(path)
        assert len(Presentation(path).slides) == 1
        print(path)
        return 0
    parser.error("此命令将在对应开发阶段实现")


if __name__ == "__main__":
    raise SystemExit(main())
