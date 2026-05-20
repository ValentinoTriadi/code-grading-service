# P1 — Sum Array
_easy · python · 28 submissions_

## Description

Given an array of numbers, return the sum of all elements. The function should handle the empty array (return 0). The signature is `def sum_array(arr): ...` (or equivalent).

## Rubric

- **Correctness (60)** — The function returns the sum of all elements correctly for both populated and empty arrays. No IndexError, RecursionError, or wrong-answer logic. The code parses without SyntaxError.
- **Code Quality (25)** — Pythonic style. Function and variable names are descriptive and do not shadow built-ins like `sum`. The chosen approach (loop, built-in, `functools.reduce`, recursion) is implemented cleanly without unnecessary intermediate variables.
- **Efficiency (15)** — The chosen approach is reasonable for the input size — a single-pass O(n) accumulation. No needless duplicate work, multiplication, or per-iteration overhead.

## Score sheet

| Submission | Correctness (60) | Code Quality (25) | Efficiency (15) | **Total** | Notes |
|---|---|---|---|---|---|
| sum_array_a1 |      |      |      |        |       |
| sum_array_a2 |      |      |      |        |       |
| sum_array_a3 |      |      |      |        |       |
| sum_array_b1 |      |      |      |        |       |
| sum_array_b2 |      |      |      |        |       |
| sum_array_b3 |      |      |      |        |       |
| sum_array_c1 |      |      |      |        |       |
| sum_array_c2 |      |      |      |        |       |
| sum_array_c3 |      |      |      |        |       |
| sum_array_c4 |      |      |      |        |       |
| sum_array_d1 |      |      |      |        |       |
| sum_array_d2 |      |      |      |        |       |
| sum_array_d3 |      |      |      |        |       |
| sum_array_e1 |      |      |      |        |       |
| sum_array_e2 |      |      |      |        |       |
| sum_array_e3 |      |      |      |        |       |
| sum_array_f1 |      |      |      |        |       |
| sum_array_f2 |      |      |      |        |       |
| sum_array_f3 |      |      |      |        |       |
| sum_array_g1 |      |      |      |        |       |
| sum_array_g2 |      |      |      |        |       |
| sum_array_g3 |      |      |      |        |       |
| sum_array_h1 |      |      |      |        |       |
| sum_array_h2 |      |      |      |        |       |
| sum_array_h3 |      |      |      |        |       |
| sum_array_i1 |      |      |      |        |       |
| sum_array_i2 |      |      |      |        |       |
| sum_array_i3 |      |      |      |        |       |

## Submissions

### 1. `sum_array_a1`

```python
def sum(arr):
    sum = 0
    for a in arr:
        sum += a
    return sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `sum_array_a2`

```python
def sum_array(arr):
    sum = 0
    for a in arr:
        sum += a
    return sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `sum_array_a3`

```python
def sum_array(arr):
    current_sum = 0
    for a in arr:
        current_sum += a
    return current_sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `sum_array_b1`

```python
def sum(arr):
    sum = 0
    for i in range(len(arr)):
        sum += arr[i]
    return sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `sum_array_b2`

```python
def sum_array(arr):
    sum = 0
    for i in range(len(arr)):
        sum += arr[i]
    return sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `sum_array_b3`

```python
def sum_array(arr):
    current_sum = 0
    for i in range(len(arr)):
        current_sum += arr[i]
    return current_sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `sum_array_c1`

```python
def sum(arr):
    sum = arr.sum()
    return sum
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `sum_array_c2`

```python
def sum(arr):
    return arr.sum()
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `sum_array_c3`

```python
def sum_array(arr):
    return arr.sum()
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `sum_array_c4`

```python
def sum(arr):
    sum_array = arr.sum()
    return sum_array
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `sum_array_d1`

```python
def sum(arr):
    return sum(arr)
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `sum_array_d2`

```python
def sum_array(arr):
    result = sum(arr)
    return result
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `sum_array_d3`

```python
def sum_array(arr):
    return sum(arr)
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `sum_array_e1`

```python
from functools import reduce

def sum(arr):
    s = reduce(lambda a, b: a + b, arr)
    return s
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `sum_array_e2`

```python
from functools import reduce

def sum_array(arr):
    total = reduce(lambda a, b: a + b, arr)
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `sum_array_e3`

```python
from functools import reduce
import operator

def sum_array(arr):
    return reduce(operator.add, arr, 0)
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `sum_array_f1`

```python
def sum(arr):
    if len(arr) == 0:
        return 0
    return arr[0] + sum(arr[1:])
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `sum_array_f2`

```python
def sum_array(arr):
    if len(arr) == 0:
        return 0
    return arr[0] + sum_array(arr[1:])
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `sum_array_f3`

```python
def sum_array(arr: list) -> int | float:
    if not arr:
        return 0
    return arr[0] + sum_array(arr[1:])
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `sum_array_g1`

```python
def sum_array(arr):
    total = 0
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 21. `sum_array_g2`

```python
def sum_array(arr):
    total = 0
    for i in range(len(arr)):
        total = arr[i]
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 22. `sum_array_g3`

```python
def sum_array(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i] * 2
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 23. `sum_array_h1`

```python
def sum_array(arr):
    total = 0
    for i in range(len(arr) - 1):
        total += arr[i]
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 24. `sum_array_h2`

```python
def sum_array(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i + 1]
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 25. `sum_array_h3`

```python
def sum_array(arr):
    total = 0
    for i in range(1, len(arr) + 1):
        total += arr[i]
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 26. `sum_array_i1`

```python
def sum_array(arr)
    total = 0
    for num in arr:
        total += num
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 27. `sum_array_i2`

```python
def sum_array(arr):
total = 0
for num in arr:
    total += num
return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 28. `sum_array_i3`

```python
def sum_array(arr):
    total = 0
    for num in arr
        total += num
    return total
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:
