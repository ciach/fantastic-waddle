# Optimized solution: use iterator-based single-pass accumulation to avoid indexing and repeated len() calls.
# Key optimizations:
# - Normalize input once, then iterate with an iterator (no indexing) to reduce Python-level overhead.
# - Use local variables for hot-loop values to minimize attribute lookups.
# Complexity: Time O(n), Space O(1).

from typing import Any

def solution(*prices: Any) -> int:
    """
    Compute the maximum profit from unlimited buy/sell operations.
    Accepts either:
      - a single argument that's a list/tuple of prices, or
      - multiple numeric arguments as prices.
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not prices:
        return 0

    # If a single list/tuple was passed, use it as the sequence; otherwise treat
    # the positional arguments tuple as the sequence.
    if len(prices) == 1 and isinstance(prices[0], (list, tuple)):
        seq = prices[0]
    else:
        seq = prices  # tuple of provided positional numeric args

    it = iter(seq)
    try:
        prev = next(it)
    except StopIteration:
        return 0

    # Fast loop: localize variables
    res = 0
    _res = res
    _prev = prev
    for cur in it:
        diff = cur - _prev
        if diff > 0:
            _res += diff
        _prev = cur

    return _res

if __name__ == "__main__":
    # Example cases from the problem statement
    print(solution([100, 180, 260, 310, 40, 535, 695]))  # Expected: 865
    print(solution([4, 2, 2, 2, 4]))  # Expected: 2
    # Also support being called with separate positional args:
    print(solution(100, 180, 260, 310, 40, 535, 695))  # Expected: 865

