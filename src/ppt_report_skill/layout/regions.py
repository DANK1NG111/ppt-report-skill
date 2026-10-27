"""Shared template geometry for both design planning and native object placement."""


def body_regions(bodies, profile):
    eligible = [
        b
        for b in bodies
        if b["height"] > profile.slide_height * 0.10
        and b["width"] > profile.slide_width * 0.15
    ]
    return (
        sorted(eligible, key=lambda b: (b["y"], b["x"]))
        if eligible
        else sorted(bodies, key=lambda b: b["width"] * b["height"], reverse=True)
    )


def union_box(areas):
    if not areas:
        return None
    x = min(b["x"] for b in areas)
    y = min(b["y"] for b in areas)
    return {
        "x": x,
        "y": y,
        "width": max(b["x"] + b["width"] for b in areas) - x,
        "height": max(b["y"] + b["height"] for b in areas) - y,
    }
