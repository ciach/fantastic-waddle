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
    if a == b: return 0
    if not a:  return len(b)
    if not b:  return len(a)
    if len(a) > len(b): a, b = b, a
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
            val = deletion if deletion < insertion else insertion
            if substitution < val: val = substitution
            curr[i] = val
        prev, curr = curr, prev
    return prev[len_a]

def solution(names, input_name):
    # If the judge passes names as a single comma-separated string, split it.
    if isinstance(names, str):
        names = [s.strip() for s in names.split(",") if s.strip()]

    if not names:
        return ""

    target_norm = _normalize(input_name)

    best_idx = 0
    best_dist = _levenshtein(target_norm, _normalize(names[0]))

    for i in range(1, len(names)):
        d = _levenshtein(target_norm, _normalize(names[i]))
        if d < best_dist:
            best_dist = d
            best_idx = i
            if d == 0:
                break

    # Return the original candidate — spaces intact.
    return names[best_idx]

