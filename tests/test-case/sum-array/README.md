# Sum Array — Test Cases

Problem: Given an array of numbers, return the sum of all elements.

Each group tests a different implementation approach. Within each group, files are numbered 1–3 representing quality level:

- **1** = poor (bad naming, shadowed builtins, unnecessary variables, etc.)
- **2** = acceptable (correct logic, some style issues)
- **3** = clean / idiomatic

---

## Group A — `for` loop, element-wise iteration

Iterates directly over elements using `for num in arr`.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_a1.py` | Poor | Function named `sum`, shadows Python built-in |
| `sum_array_a2.py` | Acceptable | Better function name, unnecessary intermediate variable |
| `sum_array_a3.py` | Good | Clean naming (`current_sum`), readable accumulation |

---

## Group B — `for` loop, index-based iteration

Iterates using `for i in range(len(arr))` and accesses elements via `arr[i]`.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_b1.py` | Poor | Function named `sum`, shadows built-in |
| `sum_array_b2.py` | Acceptable | Better name, uses index correctly |
| `sum_array_b3.py` | Good | Clean naming, consistent style |

---

## Group C — NumPy `.sum()` method

Uses `arr.sum()` assuming a NumPy array input.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_c1.py` | Poor | Function named `sum`, intermediate variable shadows name |
| `sum_array_c2.py` | Acceptable | Function named `sum` (shadows built-in), but concise |
| `sum_array_c3.py` | Good | Good function name, one-liner |
| `sum_array_c4.py` | Acceptable | Good name, unnecessary intermediate variable |

---

## Group D — Python built-in `sum()`

Uses Python's built-in `sum()` function.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_d1.py` | Broken | Function named `sum` shadows built-in → infinite recursion (`RecursionError`) |
| `sum_array_d2.py` | Acceptable | Good function name, unnecessary intermediate variable |
| `sum_array_d3.py` | Good | Clean one-liner, correct name |

---

## Group E — `functools.reduce`

Uses `functools.reduce` to fold the array into a sum.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_e1.py` | Poor | Function named `sum` (shadows built-in), intermediate variable |
| `sum_array_e2.py` | Acceptable | Good name, uses `lambda`, unnecessary intermediate variable |
| `sum_array_e3.py` | Good | Uses `operator.add` instead of lambda, explicit initial value `0` |

---

## Group F — Recursion

Implements sum recursively without any built-in helpers.

| File | Quality | Notes |
|------|---------|-------|
| `sum_array_f1.py` | Poor | Function named `sum` (shadows built-in), but logic is correct |
| `sum_array_f2.py` | Acceptable | Good function name, verbose base-case check |
| `sum_array_f3.py` | Good | Uses `not arr` idiom, includes type hints |

---

## Group G — Wrong / broken implementations

Logically incorrect code that compiles and runs but returns wrong answers.

| File | Bug |
|------|-----|
| `sum_array_g1.py` | Always returns `0` — never accumulates |
| `sum_array_g2.py` | Assigns instead of adding (`total = arr[i]` instead of `+=`) — returns last element only |
| `sum_array_g3.py` | Multiplies each element by 2 before adding — returns double the correct sum |

---

## Group H — Index errors

Code with off-by-one or out-of-bounds index mistakes that cause `IndexError` at runtime.

| File | Bug |
|------|-----|
| `sum_array_h1.py` | `range(len(arr) - 1)` skips the last element — off-by-one, wrong result |
| `sum_array_h2.py` | `arr[i + 1]` inside `range(len(arr))` — raises `IndexError` on last iteration |
| `sum_array_h3.py` | `range(1, len(arr) + 1)` — skips index 0, raises `IndexError` on last iteration |

---

## Group I — Syntax errors

Code that cannot be parsed by Python — raises `SyntaxError` before execution.

| File | Bug |
|------|-----|
| `sum_array_i1.py` | Missing `:` after `def sum_array(arr)` |
| `sum_array_i2.py` | Function body not indented — all statements at module level |
| `sum_array_i3.py` | Missing `:` after `for num in arr` |
