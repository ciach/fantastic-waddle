#!/usr/bin/env python3
# Please do not use JDK and third-party package code implementation directly or indirectly.

# Optimized fuzzy matching using Levenshtein distance.
# Key optimizations:
# - Precompile regex and normalize known names once (now with accent folding).
# - Length-based pruning before computing distances.
# - Banded (Ukkonen) Levenshtein with early cutoff: O(threshold * min(n, m)) typical.
# - Two-row DP with reused buffers (no per-row allocations).
# Big-O (worst-case if threshold >= max(n,m)): Time O(L * n * m), Space O(min(n, m)).

from typing import List, Optional, Tuple
import re
import unicodedata

# Precompile regex used for normalization
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTI_SPACE_RE = re.compile(r"\s+")


def _strip_accents(s: str) -> str:
    # stdlib-only accent folding
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _normalize(s: str) -> str:
    s = _strip_accents(s).lower()
    s = _NON_ALNUM_RE.sub(" ", s)
    s = _MULTI_SPACE_RE.sub(" ", s).strip()
    return s


def _levenshtein_banded(a: str, b: str, max_dist: Optional[int]) -> int:
    """
    Banded/Ukkonen Levenshtein with early cutoff.
    - Returns max_dist+1 if distance exceeds max_dist (when provided).
    - Uses O(min(n,m)) space, two-row DP.
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # Ensure a is the shorter string
    if len(a) > len(b):
        a, b = b, a

    len_a, len_b = len(a), len(b)

    # If a cutoff is given, prune by impossible length gap
    if max_dist is not None and (len_b - len_a) > max_dist:
        return max_dist + 1

    # Sentinel for "outside band"
    if max_dist is None:
        big = len_a + len_b + 1  # any sufficiently large number
    else:
        big = max_dist + 1

    # Initialize previous row (j=0)
    # If banded, values beyond max_dist are set to big.
    if max_dist is None:
        prev = list(range(len_a + 1))
    else:
        prev = [i if i <= max_dist else big for i in range(len_a + 1)]

    curr = [big] * (len_a + 1)

    # Local refs for speed
    a_local = a

    for j in range(1, len_b + 1):
        bj = b[j - 1]

        if max_dist is None:
            lo = 1
            hi = len_a
            curr[0] = j
        else:
            # Compute the band for this row
            lo = max(1, j - max_dist)
            hi = min(len_a, j + max_dist)
            # Set edges outside the band to big
            curr[0] = j if j <= max_dist else big
            for i in range(1, lo):
                curr[i] = big

        row_min = curr[0]

        # Inner banded loop
        # Note: using local names avoids repeated attribute lookups
        prev_loc = prev
        curr_loc = curr
        for i in range(lo, hi + 1):
            cost = 0 if a_local[i - 1] == bj else 1
            deletion = prev_loc[i] + 1
            insertion = curr_loc[i - 1] + 1
            substitution = prev_loc[i - 1] + cost
            val = deletion if deletion < insertion else insertion
            if substitution < val:
                val = substitution
            curr_loc[i] = val
            if val < row_min:
                row_min = val

        # Anything to the right of the band is "big" (keep stale values harmless)
        if max_dist is not None:
            for i in range(hi + 1, len_a + 1):
                curr[i] = big

        if max_dist is not None and row_min > max_dist:
            return max_dist + 1

        prev, curr = curr, prev

    return prev[len_a]


def solution(
    inputName: str, known_names: List[str], threshold: int = 3
) -> Optional[Tuple[str, int]]:
    """
    Find the best fuzzy match for inputName among known_names using Levenshtein distance.
    Returns a tuple (best_name, distance) if best distance <= threshold, otherwise None.

    Complexity:
    - Typical: O(L * threshold * min(n, m)) with banded DP and cutoff.
    - Worst-case (threshold >= max(n,m)): O(L * n * m).
    - Space: O(min(n, m)) for the DP rows per comparison.

    Notes:
    - Threshold < 0 is treated as 0.
    - Normalization folds accents and strips non-alphanumerics (ASCII).
    """
    if not known_names:
        return None

    if threshold < 0:
        threshold = 0

    s0 = _normalize(inputName)
    la = len(s0)

    # Normalize known names once and keep original order
    known_norms: List[Tuple[str, str, int]] = []
    norm_to_first_original: dict = {}
    for orig in known_names:
        n = _normalize(orig)
        known_norms.append((orig, n, len(n)))
        # preserve first original mapping for exact-match short-circuit
        if n not in norm_to_first_original:
            norm_to_first_original[n] = orig

    # Early exact match (normalized)
    if s0 in norm_to_first_original:
        return (norm_to_first_original[s0], 0)

    best_name: Optional[str] = None
    best_dist = threshold + 1  # current best (strictly better distances win)

    # Iterate known names and keep best match with length-based pruning
    for orig, norm, ln in known_norms:
        if abs(ln - la) > threshold:
            continue
        # Tighten cutoff to the current best - 1
        cutoff = best_dist - 1
        dist = _levenshtein_banded(s0, norm, cutoff)
        if dist < best_dist:
            best_dist = dist
            best_name = orig
            if best_dist == 0:  # can't beat exact
                break

    if best_name is None or best_dist > threshold:
        return None
    return (best_name, best_dist)


if __name__ == "__main__":
    # Example case from the problem statement
    inputName = "Globl Finanec Ltd"
    known = ["Global Finance Ltd", "Acme Corp", "Counterparty X", "Alpha Holdings"]
    print(solution(inputName, known))

