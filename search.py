import argparse
import csv
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from sympy import factorint as sympy_factorint
    from sympy import isprime as sympy_isprime
except Exception:
    sympy_factorint = None
    sympy_isprime = None


A_VALUES = [1, 2, 3, 5, 7, 11, 13, 17, 19]
P_PRIMES = [2, 3, 5, 7, 11]
E_MIN = 2
E_MAX = 40
K_MIN = 2
K_MAX = 20
Q_MAX = 30
TOP_N = 50


@dataclass(frozen=True)
class Candidate:
    a: int
    b: int
    c: int
    p: int
    e: int
    P: int
    q: int
    k: int
    P_factor: str
    P_max_prime_factor: int
    P_is_prime: bool
    rad_abc: int
    Q: float
    Dp_b: float
    T: float
    Ec: float
    Bab: float


SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in SMALL_PRIMES:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        c = random.randrange(1, n - 1)
        x = random.randrange(2, n - 1)
        y = x
        d = 1
        while d == 1:
            x = (pow(x, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor_list(n: int) -> list[int]:
    n = abs(n)
    if n == 1:
        return []
    if miller_rabin(n):
        return [n]
    d = pollard_rho(n)
    return factor_list(d) + factor_list(n // d)


def fallback_factorint(n: int) -> dict[int, int]:
    result: dict[int, int] = {}
    for factor in factor_list(n):
        result[factor] = result.get(factor, 0) + 1
    return result


def factorint(n: int) -> dict[int, int]:
    if n in (0, 1):
        return {}
    if sympy_factorint is not None:
        return dict(sympy_factorint(abs(n)))
    return fallback_factorint(n)


def isprime(n: int) -> bool:
    if n < 2:
        return False
    if sympy_isprime is not None:
        return bool(sympy_isprime(n))
    return miller_rabin(n)


def factor_text(n: int) -> str:
    if n == 1:
        return "1"
    return "*".join(
        str(prime) if exp == 1 else f"{prime}^{exp}"
        for prime, exp in sorted(factorint(n).items())
    )


def rad(n: int) -> int:
    value = 1
    for prime in factorint(n):
        value *= prime
    return value


def max_prime_factor(n: int) -> int:
    factors = factorint(n)
    return max(factors) if factors else 1


def make_candidate(a: int, p: int, e: int, q: int, k: int) -> Candidate | None:
    c = q**k
    pe = p**e
    numerator = c - a
    if numerator <= 0 or numerator % pe != 0:
        return None
    P = numerator // pe
    if P <= 1:
        return None
    b = pe * P
    if math.gcd(a, b) != 1:
        return None
    if a + b != c:
        return None

    rad_a = rad(a)
    rad_b = rad(b)
    rad_c = rad(c)
    rad_abc = rad_a * rad_b * rad_c
    log_c = math.log(c)
    log_rad_abc = math.log(rad_abc)
    log_b = math.log(b)
    Q = log_c / log_rad_abc
    Dp_b = e * math.log(p) / log_b
    Ec = log_c - math.log(rad_c)
    Bab = math.log(rad_a) + math.log(rad_b)
    denominator = 2 * Bab + math.log(rad_c)
    T = Ec / denominator if denominator else float("inf")

    return Candidate(
        a=a,
        b=b,
        c=c,
        p=p,
        e=e,
        P=P,
        q=q,
        k=k,
        P_factor=factor_text(P),
        P_max_prime_factor=max_prime_factor(P),
        P_is_prime=isprime(P),
        rad_abc=rad_abc,
        Q=Q,
        Dp_b=Dp_b,
        T=T,
        Ec=Ec,
        Bab=Bab,
    )


def search(q_max: int = Q_MAX) -> list[Candidate]:
    candidates: list[Candidate] = []
    for a in A_VALUES:
        for p in P_PRIMES:
            for e in range(E_MIN, E_MAX + 1):
                for k in range(K_MIN, K_MAX + 1):
                    for q in range(2, q_max + 1):
                        candidate = make_candidate(a, p, e, q, k)
                        if candidate is not None:
                            candidates.append(candidate)
    return candidates


def write_csv(path: Path, candidates: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(candidate) for candidate in candidates]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def markdown_table(candidates: list[Candidate], key: str) -> str:
    rows = sorted(candidates, key=lambda item: getattr(item, key), reverse=True)[:TOP_N]
    headers = ["a", "p", "e", "P", "q", "k", "Q", "T", "Dp_b", "P_is_prime"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for item in rows:
        values = []
        for header in headers:
            value = getattr(item, header)
            if isinstance(value, float):
                value = f"{value:.6f}"
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_results(path: Path, candidates: list[Candidate], q_max: int) -> None:
    known = [
        candidate
        for candidate in candidates
        if candidate.a == 2
        and candidate.p == 3
        and candidate.e == 10
        and candidate.P == 109
        and candidate.q == 23
        and candidate.k == 5
    ]
    lines = [
        "# ABC Quality Candidate Search Results",
        "",
        "## Summary",
        "",
        f"- q_max: {q_max}",
        f"- candidates: {len(candidates)}",
        f"- known example `2 + 3^10*109 = 23^5` detected: {'yes' if known else 'no'}",
        "",
        "## Top 50 By Q",
        "",
        markdown_table(candidates, "Q"),
        "",
        "## Top 50 By T",
        "",
        markdown_table(candidates, "T"),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q-max", type=int, default=Q_MAX)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = search(q_max=args.q_max)
    out_dir = Path("outputs")
    candidates_sorted = sorted(candidates, key=lambda item: item.Q, reverse=True)
    write_csv(out_dir / "abc_quality_candidates.csv", candidates_sorted)
    write_results(Path("results.md"), candidates_sorted, args.q_max)
    print(f"candidates={len(candidates_sorted)}")
    print(
        "known_example_detected=",
        any(
            c.a == 2 and c.p == 3 and c.e == 10 and c.P == 109 and c.q == 23 and c.k == 5
            for c in candidates_sorted
        ),
    )


if __name__ == "__main__":
    main()
