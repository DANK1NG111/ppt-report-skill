import pytest
from ppt_report_skill.models import PresentationRequest
from ppt_report_skill.content.report_type import detect_report_type


@pytest.mark.parametrize(
    "topic,expected",
    [
        ("季度工作汇报", "work_report"),
        ("部门年度工作总结", "work_report"),
        ("项目进展与里程碑", "project_progress"),
        ("项目目标和当前进度", "project_progress"),
        ("研究背景、方法与实验", "academic_report"),
        ("课程汇报与文献讨论", "academic_report"),
        ("发展对象答辩个人情况", "defense"),
        ("毕业论文答辩", "defense"),
        ("随想", "custom"),
    ],
)
def test_classification(topic, expected):
    assert detect_report_type(PresentationRequest(topic=topic), []) == expected


def test_explicit_type_wins():
    assert (
        detect_report_type(
            PresentationRequest(topic="学术实验", presentation_type="work_report"), []
        )
        == "work_report"
    )
