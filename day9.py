import re
import unicodedata

# Precompile regex used for normalization
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


def _levenshtein_banded(a: str, b: str, max_dist: int) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) > len(b):
        a, b = b, a

    len_a, len_b = len(a), len(b)
    if abs(len_a - len_b) > max_dist:
        return max_dist + 1

    big = max_dist + 1
    prev = [i if i <= max_dist else big for i in range(len_a + 1)]
    curr = [big] * (len_a + 1)

    for j in range(1, len_b + 1):
        bj = b[j - 1]
        lo = max(1, j - max_dist)
        hi = min(len_a, j + max_dist)
        curr[0] = j if j <= max_dist else big
        for i in range(1, lo):
            curr[i] = big

        row_min = curr[0]
        for i in range(lo, hi + 1):
            cost = 0 if a[i - 1] == bj else 1
            deletion = prev[i] + 1
            insertion = curr[i - 1] + 1
            substitution = prev[i - 1] + cost
            val = min(deletion, insertion, substitution)
            curr[i] = val
            if val < row_min:
                row_min = val

        for i in range(hi + 1, len_a + 1):
            curr[i] = big
        if row_min > max_dist:
            return big
        prev, curr = curr, prev

    return prev[len_a]


def solution(names, input_name):
    """Return best fuzzy match string or '' if no match found"""
    if not names:
        return ""

    threshold = 3
    target = _normalize(input_name)
    best_name = ""
    best_dist = threshold + 1

    for name in names:
        norm = _normalize(name)
        if norm == target:
            return name
        if abs(len(norm) - len(target)) > threshold:
            continue
        dist = _levenshtein_banded(target, norm, best_dist - 1)
        if dist < best_dist:
            best_name, best_dist = name, dist
            if best_dist == 0:
                break

    return best_name if best_dist <= threshold else ""

