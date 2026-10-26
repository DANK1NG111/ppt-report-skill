def estimate_count(duration, fact_count, section_count):
    by_time = round(duration * 1.0 + 3) if duration else (fact_count + 2) // 3 + 2
    return max(section_count + 2, by_time)


def speaking_times(plans, duration):
    weights = [
        0.2
        if p.slide_type in {"cover", "closing", "contents"}
        else max(p.importance, 1)
        for p in plans
    ]
    total = (duration or max(len(plans) * 0.55, 1)) * 60
    for p, w in zip(plans, weights):
        p.estimated_speaking_time = round(total * w / sum(weights), 2)
