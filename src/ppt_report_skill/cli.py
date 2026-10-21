"""Command line entry points; extended by subsequent development phases."""
import argparse
from pathlib import Path
from pptx import Presentation


def main(argv=None):
    parser = argparse.ArgumentParser(description="基于真实模板制作可编辑汇报 PPT")
    parser.add_argument("command", choices=["analyze", "create", "validate", "render", "regression", "smoke"])
    parser.add_argument("--output", default="output/smoke.pptx")
    parser.add_argument("--template", default="assets/templates/base_template.pptx")
    parser.add_argument("--materials", nargs="*", default=[])
    parser.add_argument("--request", help="PresentationRequest JSON 文件")
    parser.add_argument("--text", help="直接提供的汇报材料")
    parser.add_argument("--input", default="output/presentation.pptx", help="需要校验或渲染的 PPTX")
    parser.add_argument("--build", help="包含 slide_plans.json、request.json 和 template_profile.json 的目录")
    parser.add_argument("--draft", action="store_true", help="仅生成草稿，跳过完整 QA 流程")
    args = parser.parse_args(argv)
    if args.command == "render":
        from .renderer.render import render_presentation
        result=render_presentation(args.input,args.output if args.output!='output/smoke.pptx' else 'output/rendered')
        print(f"PASS: {result['page_count']} rendered; {result['contact_sheet']}")
        return 0
    if args.command == "validate":
        import json
        from .models import SlidePlan,PresentationRequest,TemplateProfile
        from .validator import validate_presentation
        plans=request=profile=None
        if args.build:
            build=Path(args.build)
            plans=[SlidePlan(**x) for x in json.loads((build/'slide_plans.json').read_text())]
            request=PresentationRequest(**json.loads((build/'request.json').read_text())) if (build/'request.json').exists() else None
            profile=TemplateProfile.from_dict(json.loads((build/'template_profile.json').read_text())) if (build/'template_profile.json').exists() else None
        result=validate_presentation(args.input,args.output if args.output!='output/smoke.pptx' else 'output',plans,request,profile)
        print(f"{result['status']}: errors={result['errors']}, warnings={result['warnings']}")
        return int(bool(result['errors']))
    if args.command == "create":
        import json
        from .draft import create_draft
        from .pipeline import create_presentation
        from .models import ReportError
        try:
            data=json.loads(Path(args.request).read_text()) if args.request else {}
            result=create_draft(args.template,args.materials,data,args.output,args.text) if args.draft else create_presentation(args.template,args.materials,data,args.output if args.output!='output/smoke.pptx' else 'output/presentation.pptx',args.text)
        except ReportError as exc:
            print(str(exc))
            return 2
        print(f"DRAFT_UNVALIDATED: {result}" if args.draft else f"{result['status']}: {result['path']}")
        return 0
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
