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
    # ensure a is shorter
    if len(a) > len(b):
        a, b = b, a
    len_a = len(a)
    prev = list(range(len_a + 1))
    curr = [0] * (len_a + 1)
    for cb in b:
        curr[0] = prev[0] + 1
        for i in range(1, len_a + 1):
            cost = 0 if a[i - 1] == cb else 1
            deletion = prev[i] + 1
            insertion = curr[i - 1] + 1
            substitution = prev[i - 1] + cost
            curr[i] = deletion if deletion < insertion else insertion
            if substitution < curr[i]:
                curr[i] = substitution
        prev, curr = curr, prev
    return prev[len_a]

def solution(names, input_name):
    """Return the single closest name (no threshold)."""
    if not names:
        return ""
    target = _normalize(input_name)
    # Initialize with the first candidate
    best_name = names[0]
    best_dist = _levenshtein(target, _normalize(best_name))
    # Check the rest
    for name in names[1:]:
        d = _levenshtein(target, _normalize(name))
        if d < best_dist:
            best_dist = d
            best_name = name
            if d == 0:
                break
    return best_name

