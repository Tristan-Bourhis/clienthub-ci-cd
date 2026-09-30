def average(values: list[float]) -> float:
    if not values:
        raise ValueError("La liste ne doit pas être vide")
    return sum(values) / len(values)


def add(n1: int, n2: int) -> int:
    return n1 + n2


if __name__ == "__main__":
    add("2", 2)
