# Binary Search Tree — Test Cases

**Language:** Java
**Difficulty:** Hard

## Problem

Implement a generic **Binary Search Tree** for `Integer` keys with the following API:

```java
public class BST {
    public void insert(int key);            // duplicates ignored
    public boolean contains(int key);
    public boolean delete(int key);         // returns true iff key existed
    public List<Integer> inorder();         // sorted ascending
    public int size();
}
```

- `insert` should be idempotent — inserting an existing key does nothing.
- `delete` must correctly handle the three classical cases:
  1. leaf node
  2. node with one child
  3. node with two children (replace with in-order successor or predecessor)
- `inorder()` must return keys in ascending order.

Each group represents a different implementation approach.

- **1** = poor (style issues, public fields, no encapsulation)
- **2** = acceptable (correct, some style issues)
- **3** = good (clean, idiomatic, well-encapsulated)

---

## Group A — Recursive (textbook)

Recursive `insert`, `contains`, `delete`, `inorder`. The classic teaching implementation.

| File | Quality | Notes |
|------|---------|-------|
| `BstA1.java` | Poor | Public `Node` fields, mixes recursion with loops, prints in `inorder` instead of returning a list |
| `BstA2.java` | Acceptable | Encapsulated, recursive everywhere, returns `List<Integer>` |
| `BstA3.java` | Good | Clean recursion, immutable-style helpers, javadoc-light |

## Group B — Iterative

`insert`, `contains` use `while` loops; in-order uses an explicit stack.

| File | Quality | Notes |
|------|---------|-------|
| `BstB1.java` | Poor | Iterative but `Node` is package-private with public fields |
| `BstB2.java` | Acceptable | Correct iterative insert/contains, recursive delete |
| `BstB3.java` | Good | Fully iterative including stack-based in-order traversal |

## Group C — Generic implementation

`BST<T extends Comparable<T>>` parameterized by the key type.

| File | Quality | Notes |
|------|---------|-------|
| `BstC1.java` | Acceptable | Generic but mixes `<T>` and raw types, suppresses warnings |
| `BstC2.java` | Good | Clean `Comparable<T>` constraint, no raw types |

## Group D — Built-in / cheating

Uses `java.util.TreeSet` (or `TreeMap`) under the hood.

| File | Quality | Notes |
|------|---------|-------|
| `BstD1.java` | Poor | Just delegates to `TreeSet` — no actual tree implementation, fails the spirit of the problem |
| `BstD2.java` | Acceptable | Wraps `TreeMap` with explicit BST API, technically correct |

## Group E — Logic bugs (compiles, wrong answer)

| File | Bug |
|------|-----|
| `BstE1.java` | `insert` allows duplicates — adds them to right subtree |
| `BstE2.java` | `contains` always returns `false` (recurses on the original `root` not subtree) |
| `BstE3.java` | `inorder` does left-root-right but uses pre-order — returns wrong order |
| `BstE4.java` | `delete` for two-child case copies key but doesn't remove successor — duplicates appear |

## Group F — Edge-case bugs

| File | Bug |
|------|-----|
| `BstF1.java` | `delete` of leaf works, but `delete` of root when root has children leaves dangling reference |
| `BstF2.java` | `contains(x)` recurses without null check — `NullPointerException` on missing key in deep tree |
| `BstF3.java` | `size()` returns `inorder().size()` — O(n) per call, allocates list every time |

## Group G — Performance / robustness pitfalls

| File | Issue |
|------|-------|
| `BstG1.java` | Recursive insert/contains — `StackOverflowError` on a million-node degenerate (sorted) input |
| `BstG2.java` | `inorder` uses `+ ", "` string concat in a recursive helper, then `Arrays.asList(split(",")` — quadratic, fragile |

## Group H — Compile errors

| File | Bug |
|------|-----|
| `BstH1.java` | `Node` declared without `static` inside a non-static context — incompatible reference |
| `BstH2.java` | Missing `import java.util.List` |

## Group I — Creative correct alternatives

| File | Quality | Notes |
|------|---------|-------|
| `BstI1.java` | Good | Augmented BST — each node caches `subtreeSize` so `size()` is O(1) |
| `BstI2.java` | Good | Morris in-order traversal — `inorder()` runs in O(n) time and O(1) extra space |
