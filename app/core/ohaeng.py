from app.data.constants import (
    CHEONGAN_OHAENG,
    CHEONGAN_UMYANG,
    JIJI_OHAENG,
    JIJI_UMYANG,
    OHAENG,
)


def analyze_ohaeng(saju: dict) -> dict:
    """사주팔자의 오행 분포를 분석한다."""
    counts = {oh: 0 for oh in OHAENG}
    details = []

    pillars = [
        ("년주", saju["year_pillar"]),
        ("월주", saju["month_pillar"]),
        ("일주", saju["day_pillar"]),
        ("시주", saju["hour_pillar"]),
    ]

    for name, pillar in pillars:
        gan = pillar["cheongan"]
        ji = pillar["jiji"]

        gan_oh = CHEONGAN_OHAENG[gan]
        ji_oh = JIJI_OHAENG[ji]
        gan_uy = CHEONGAN_UMYANG[gan]
        ji_uy = JIJI_UMYANG[ji]

        counts[gan_oh] += 1
        counts[ji_oh] += 1

        details.append({
            "pillar": name,
            "cheongan": {"char": gan, "ohaeng": gan_oh, "umyang": gan_uy},
            "jiji": {"char": ji, "ohaeng": ji_oh, "umyang": ji_uy},
        })

    day_gan = saju["day_pillar"]["cheongan"]
    my_ohaeng = CHEONGAN_OHAENG[day_gan]

    strongest = max(counts, key=counts.get)
    weakest = min(counts, key=counts.get)

    return {
        "counts": counts,
        "total": sum(counts.values()),
        "my_ohaeng": my_ohaeng,
        "strongest": strongest,
        "weakest": weakest,
        "details": details,
    }
