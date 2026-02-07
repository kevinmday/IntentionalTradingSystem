def compute_fils(c_pub: int, c_brand: int) -> float:
    return max(
        0.0,
        min(
            1.0,
            0.55 * (c_pub > 0)
            + 0.15 * min(3, c_pub)
            - 0.20 * min(3, c_brand),
        ),
    )