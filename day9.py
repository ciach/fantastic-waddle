import re
import unicodedata

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTI_SPACE_RE = re.compile(r"\s+")


def _strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _normalize(s: str) -> str:
    s = _strip_accents(s).lower()
    s = _NON_ALNUM_RE.sub(" ", s)
    s = _MULTI_SPACE_RE.sub(" ", s).strip()
    return s


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) > len(b):
        a, b = b, a
    la = len(a)
    prev = list(range(la + 1))
    curr = [0] * (la + 1)
    for cb in b:
        curr[0] = prev[0] + 1
        for i in range(1, la + 1):
            cost = 0 if a[i - 1] == cb else 1
            deletion = prev[i] + 1
            insertion = curr[i - 1] + 1
            substitution = prev[i - 1] + cost
            val = deletion if deletion < insertion else insertion
            if substitution < val:
                val = substitution
            curr[i] = val
        prev, curr = curr, prev
    return prev[la]


def solution(names, input_name):
    # Defensive split if a comma-separated string is passed
    if isinstance(names, str):
        names = [s.strip() for s in names.split(",") if s.strip()]
    if not names:
        return None

    tgt = _normalize(input_name)

    # Initialize with first candidate
    best_idx = 0
    best_dist = _levenshtein(tgt, _normalize(names[0]))

    # Search best match
    for i in range(1, len(names)):
        d = _levenshtein(tgt, _normalize(names[i]))
        if d < best_dist:
            best_dist = d
            best_idx = i
            if d == 0:
                break

    # --- Robust gate: recompute length from the ACTUAL best candidate ---
    best_norm_len = len(_normalize(names[best_idx]))
    max_len = max(len(tgt), best_norm_len) or 1
    similarity = 1.0 - (best_dist / max_len)

    if best_dist <= 3 or similarity >= 0.60:
        return names[best_idx]
    return None


if __name__ == "__main__":
    print(
        solution(
            ["Acme Corp", "Global Finance Ltd", "Counterparty X", "Alpha Holdings"],
            "Globl Finanec",
        )
    )

