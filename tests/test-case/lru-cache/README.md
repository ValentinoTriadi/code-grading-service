# LRU Cache — Test Cases

**Language:** TypeScript
**Difficulty:** Medium

## Problem

Design an in-memory **Least Recently Used (LRU)** cache as a class:

```ts
class LRUCache<K, V> {
    constructor(capacity: number);
    get(key: K): V | undefined;     // returns undefined if missing
    put(key: K, value: V): void;    // overwrites if present
    size(): number;
}
```

Both `get` and `put` count as "use". When `size > capacity` after a `put`, evict the least-recently-used entry.

Both operations should be **O(1)** amortized in the canonical solution.

Each group represents a different implementation approach.

- **1** = poor (correctness issues, bad style, mutates state oddly)
- **2** = acceptable (correct, some style/perf issues)
- **3** = good (clean, idiomatic, O(1))

---

## Group A — `Map` reinsert trick (idiomatic JS/TS)

JavaScript's `Map` preserves insertion order. Re-inserting on access moves the key to "most recent".

| File | Quality | Notes |
|------|---------|-------|
| `lru_a1.ts` | Poor | Uses `any`, no generics, doesn't reset recency on `put` of an existing key |
| `lru_a2.ts` | Acceptable | Generic, correct, but uses `Map.entries().next()` awkwardly |
| `lru_a3.ts` | Good | Clean generic LRU using `Map`, idiomatic eviction |

## Group B — Hash map + doubly-linked list (textbook)

The canonical interview answer: `Map<K, Node>` plus a hand-rolled doubly-linked list with sentinel head/tail.

| File | Quality | Notes |
|------|---------|-------|
| `lru_b1.ts` | Poor | Linked list works, but `Node` has `any` types, `_remove` mutates without null-check |
| `lru_b2.ts` | Acceptable | Generic, correct, sentinel head/tail, slight redundancy |
| `lru_b3.ts` | Good | Clean encapsulation, `private` helpers, no `any` |

## Group C — Plain object + access-time tracking

| File | Quality | Notes |
|------|---------|-------|
| `lru_c1.ts` | Poor | Uses object literal as dict — breaks on numeric keys, O(n) eviction |
| `lru_c2.ts` | Acceptable | Tracks `lastUsed` timestamps, scans O(n) on eviction |

## Group D — Array-as-recency-list (brute force)

Maintains an array of keys ordered by recency.

| File | Quality | Notes |
|------|---------|-------|
| `lru_d1.ts` | Poor | `Array.indexOf` + `splice` per access, O(n) per op |
| `lru_d2.ts` | Acceptable | Same approach but with `Map<K,V>` for value lookup |

## Group E — Functional / closure-based

| File | Quality | Notes |
|------|---------|-------|
| `lru_e1.ts` | Acceptable | Factory function returning `{get, put}` — works but escapes the OOP requirement |
| `lru_e2.ts` | Good | Class wraps a closure — gets the best of both styles |

## Group F — Wrong logic

| File | Bug |
|------|-----|
| `lru_f1.ts` | `get` returns the value but does NOT mark the entry as recently used |
| `lru_f2.ts` | `put` of existing key inserts a duplicate entry into the recency list |
| `lru_f3.ts` | Evicts the most-recently-used instead of least (calls `pop()` instead of `shift()`) |
| `lru_f4.ts` | Evicts only when `size > capacity + 1` — keeps one extra |
| `lru_f5.ts` | `size()` returns `capacity` instead of `entries.size` |

## Group G — Edge-case bugs

| File | Bug |
|------|-----|
| `lru_g1.ts` | Crashes on `capacity = 0` — `put` infinite-loops trying to evict |
| `lru_g2.ts` | `get` returns `null` instead of `undefined` for missing keys |

## Group H — Compile errors

| File | Bug |
|------|-----|
| `lru_h1.ts` | Missing closing brace on `put` method |
| `lru_h2.ts` | `private` field accessed without `this.` |
| `lru_h3.ts` | Generic `<K, V>` declared but used as `<K, V, V>` in field type |

## Group I — OOP-flavored creative correct alternatives

| File | Quality | Notes |
|------|---------|-------|
| `lru_i1.ts` | Good | Composition — `LRUCache` delegates recency tracking to a separate `RecencyList<K>` class |
| `lru_i2.ts` | Good | Inheritance — `CountingLRUCache extends LRUCache`, exposes hit/miss stats |
| `lru_i3.ts` | Good | Abstract base `AbstractEvictingCache<K,V>`; `LRUCache` overrides `get` and `evict` strategy |
