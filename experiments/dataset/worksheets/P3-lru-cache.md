# P3 — LRU Cache
_medium · typescript · 25 submissions_

## Description

Design an in-memory Least Recently Used (LRU) cache as a class `LRUCache<K, V>` with constructor `(capacity: number)`, `get(key: K): V | undefined`, `put(key: K, value: V): void` (overwriting if present), and `size(): number`. Both `get` and `put` count as 'use'. When `size > capacity` after a `put`, evict the least-recently-used entry. Both operations should be O(1) amortized.

## Rubric

- **Correctness (40)** — `get` returns the value or `undefined` for missing keys; `put` overwrites and refreshes recency; both `get` and `put` count as use; eviction removes the LEAST-recently-used entry when `size > capacity`. Returns `undefined` (not `null`) for misses. Handles `capacity = 0` without infinite loops. Does not silently mis-evict the most-recently-used entry. The code compiles.
- **Data Structures (25)** — The structure used can deliver the recency semantics — `Map` (which preserves insertion order in TypeScript), or hash + doubly-linked list, or equivalent. No duplicate recency entries that corrupt eviction order. No abuse of plain object as ordered map.
- **Efficiency (20)** — `get` and `put` are O(1) amortized in the canonical solution. No O(n) scans on every access (e.g., array `indexOf` to find the LRU). No accidental re-allocation on every `put`.
- **Code Quality (15)** — Uses generics `<K, V>` rather than `any`. Picks a clean approach and implements it idiomatically without redundant fields or awkward APIs.

## Score sheet

| Submission | Correctness (40) | Data Structures (25) | Efficiency (20) | Code Quality (15) | **Total** | Notes |
|---|---|---|---|---|---|---|
| lru_a1 |      |      |      |      |        |       |
| lru_a2 |      |      |      |      |        |       |
| lru_a3 |      |      |      |      |        |       |
| lru_b1 |      |      |      |      |        |       |
| lru_b2 |      |      |      |      |        |       |
| lru_b3 |      |      |      |      |        |       |
| lru_c1 |      |      |      |      |        |       |
| lru_c2 |      |      |      |      |        |       |
| lru_d1 |      |      |      |      |        |       |
| lru_d2 |      |      |      |      |        |       |
| lru_e1 |      |      |      |      |        |       |
| lru_e2 |      |      |      |      |        |       |
| lru_f1 |      |      |      |      |        |       |
| lru_f2 |      |      |      |      |        |       |
| lru_f3 |      |      |      |      |        |       |
| lru_f4 |      |      |      |      |        |       |
| lru_f5 |      |      |      |      |        |       |
| lru_g1 |      |      |      |      |        |       |
| lru_g2 |      |      |      |      |        |       |
| lru_h1 |      |      |      |      |        |       |
| lru_h2 |      |      |      |      |        |       |
| lru_h3 |      |      |      |      |        |       |
| lru_i1 |      |      |      |      |        |       |
| lru_i2 |      |      |      |      |        |       |
| lru_i3 |      |      |      |      |        |       |

## Submissions

### 1. `lru_a1`

```ts
class LRUCache {
    capacity: number;
    map: Map<any, any>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.map = new Map();
    }

    get(key: any): any {
        if (!this.map.has(key)) return undefined;
        const v = this.map.get(key);
        this.map.delete(key);
        this.map.set(key, v);
        return v;
    }

    put(key: any, value: any): void {
        this.map.set(key, value);
        if (this.map.size > this.capacity) {
            const firstKey = this.map.keys().next().value;
            this.map.delete(firstKey);
        }
    }

    size(): number {
        return this.map.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `lru_a2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store: Map<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.store = new Map<K, V>();
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) {
            return undefined;
        }
        const value = this.store.get(key) as V;
        this.store.delete(key);
        this.store.set(key, value);
        return value;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) {
            this.store.delete(key);
        }
        this.store.set(key, value);
        while (this.store.size > this.capacity) {
            const oldest = this.store.entries().next().value;
            if (oldest === undefined) break;
            this.store.delete(oldest[0]);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `lru_a3`

```ts
export class LRUCache<K, V> {
    private readonly capacity: number;
    private readonly entries = new Map<K, V>();

    constructor(capacity: number) {
        if (capacity <= 0) {
            throw new RangeError("capacity must be positive");
        }
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        const value = this.entries.get(key);
        if (value === undefined) return undefined;
        this.entries.delete(key);
        this.entries.set(key, value);
        return value;
    }

    put(key: K, value: V): void {
        if (this.entries.has(key)) {
            this.entries.delete(key);
        } else if (this.entries.size >= this.capacity) {
            const oldest = this.entries.keys().next().value as K;
            this.entries.delete(oldest);
        }
        this.entries.set(key, value);
    }

    size(): number {
        return this.entries.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `lru_b1`

```ts
class Node {
    key: any;
    value: any;
    prev: any = null;
    next: any = null;
    constructor(k: any, v: any) {
        this.key = k;
        this.value = v;
    }
}

class LRUCache {
    capacity: number;
    map: any = {};
    head: any;
    tail: any;
    count: number = 0;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.head = new Node(null, null);
        this.tail = new Node(null, null);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    _remove(n: any) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    _add(n: any) {
        n.prev = this.head;
        n.next = this.head.next;
        this.head.next.prev = n;
        this.head.next = n;
    }

    get(key: any) {
        const n = this.map[key];
        if (!n) return undefined;
        this._remove(n);
        this._add(n);
        return n.value;
    }

    put(key: any, value: any) {
        if (this.map[key]) {
            this._remove(this.map[key]);
            this.count--;
        }
        const n = new Node(key, value);
        this._add(n);
        this.map[key] = n;
        this.count++;
        if (this.count > this.capacity) {
            const lru = this.tail.prev;
            this._remove(lru);
            delete this.map[lru.key];
            this.count--;
        }
    }

    size() {
        return this.count;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `lru_b2`

```ts
class DLLNode<K, V> {
    key: K;
    value: V;
    prev: DLLNode<K, V> | null = null;
    next: DLLNode<K, V> | null = null;
    constructor(key: K, value: V) {
        this.key = key;
        this.value = value;
    }
}

class LRUCache<K, V> {
    private capacity: number;
    private map: Map<K, DLLNode<K, V>>;
    private head: DLLNode<K, V>;
    private tail: DLLNode<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.map = new Map();
        this.head = new DLLNode<K, V>(null as unknown as K, null as unknown as V);
        this.tail = new DLLNode<K, V>(null as unknown as K, null as unknown as V);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    private removeNode(n: DLLNode<K, V>): void {
        const p = n.prev!;
        const nx = n.next!;
        p.next = nx;
        nx.prev = p;
    }

    private addToFront(n: DLLNode<K, V>): void {
        n.prev = this.head;
        n.next = this.head.next;
        this.head.next!.prev = n;
        this.head.next = n;
    }

    get(key: K): V | undefined {
        const node = this.map.get(key);
        if (!node) return undefined;
        this.removeNode(node);
        this.addToFront(node);
        return node.value;
    }

    put(key: K, value: V): void {
        const existing = this.map.get(key);
        if (existing) {
            this.removeNode(existing);
            this.map.delete(key);
        }
        const node = new DLLNode(key, value);
        this.addToFront(node);
        this.map.set(key, node);
        if (this.map.size > this.capacity) {
            const lru = this.tail.prev!;
            this.removeNode(lru);
            this.map.delete(lru.key);
        }
    }

    size(): number {
        return this.map.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `lru_b3`

```ts
class ListNode<K, V> {
    constructor(
        public key: K,
        public value: V,
        public prev: ListNode<K, V> | null = null,
        public next: ListNode<K, V> | null = null,
    ) {}
}

export class LRUCache<K, V> {
    private readonly capacity: number;
    private readonly index = new Map<K, ListNode<K, V>>();
    private readonly head: ListNode<K, V>;
    private readonly tail: ListNode<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.head = new ListNode<K, V>(null as unknown as K, null as unknown as V);
        this.tail = new ListNode<K, V>(null as unknown as K, null as unknown as V);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    private detach(node: ListNode<K, V>): void {
        node.prev!.next = node.next;
        node.next!.prev = node.prev;
    }

    private prepend(node: ListNode<K, V>): void {
        node.prev = this.head;
        node.next = this.head.next;
        this.head.next!.prev = node;
        this.head.next = node;
    }

    get(key: K): V | undefined {
        const node = this.index.get(key);
        if (!node) return undefined;
        this.detach(node);
        this.prepend(node);
        return node.value;
    }

    put(key: K, value: V): void {
        const existing = this.index.get(key);
        if (existing) {
            existing.value = value;
            this.detach(existing);
            this.prepend(existing);
            return;
        }

        if (this.index.size === this.capacity) {
            const lru = this.tail.prev!;
            this.detach(lru);
            this.index.delete(lru.key);
        }

        const node = new ListNode(key, value);
        this.prepend(node);
        this.index.set(key, node);
    }

    size(): number {
        return this.index.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `lru_c1`

```ts
class LRUCache {
    capacity: number;
    cache: { [key: string]: any } = {};
    order: string[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: any): any {
        const k = String(key);
        if (!(k in this.cache)) return undefined;
        const idx = this.order.indexOf(k);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(k);
        return this.cache[k];
    }

    put(key: any, value: any): void {
        const k = String(key);
        this.cache[k] = value;
        const idx = this.order.indexOf(k);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(k);
        while (this.order.length > this.capacity) {
            const evict = this.order.shift()!;
            delete this.cache[evict];
        }
    }

    size(): number {
        return Object.keys(this.cache).length;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `lru_c2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private values = new Map<K, V>();
    private lastUsed = new Map<K, number>();
    private clock = 0;

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.values.has(key)) return undefined;
        this.lastUsed.set(key, ++this.clock);
        return this.values.get(key);
    }

    put(key: K, value: V): void {
        this.values.set(key, value);
        this.lastUsed.set(key, ++this.clock);

        if (this.values.size > this.capacity) {
            let oldestKey: K | undefined;
            let oldestTime = Infinity;
            for (const [k, t] of this.lastUsed) {
                if (t < oldestTime) {
                    oldestTime = t;
                    oldestKey = k;
                }
            }
            if (oldestKey !== undefined) {
                this.values.delete(oldestKey);
                this.lastUsed.delete(oldestKey);
            }
        }
    }

    size(): number {
        return this.values.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `lru_d1`

```ts
class LRUCache {
    private capacity: number;
    private keys: any[] = [];
    private values: any[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: any): any {
        const idx = this.keys.indexOf(key);
        if (idx === -1) return undefined;
        const v = this.values[idx];
        this.keys.splice(idx, 1);
        this.values.splice(idx, 1);
        this.keys.push(key);
        this.values.push(v);
        return v;
    }

    put(key: any, value: any): void {
        const idx = this.keys.indexOf(key);
        if (idx !== -1) {
            this.keys.splice(idx, 1);
            this.values.splice(idx, 1);
        }
        this.keys.push(key);
        this.values.push(value);
        if (this.keys.length > this.capacity) {
            this.keys.shift();
            this.values.shift();
        }
    }

    size(): number {
        return this.keys.length;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `lru_d2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();
    private order: K[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const idx = this.order.indexOf(key);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(key);
        return this.store.get(key);
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) {
            const idx = this.order.indexOf(key);
            if (idx >= 0) this.order.splice(idx, 1);
        }
        this.store.set(key, value);
        this.order.push(key);

        while (this.order.length > this.capacity) {
            const evict = this.order.shift();
            if (evict !== undefined) this.store.delete(evict);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `lru_e1`

```ts
function makeLRUCache<K, V>(capacity: number) {
    const store = new Map<K, V>();

    function get(key: K): V | undefined {
        if (!store.has(key)) return undefined;
        const v = store.get(key) as V;
        store.delete(key);
        store.set(key, v);
        return v;
    }

    function put(key: K, value: V): void {
        if (store.has(key)) store.delete(key);
        store.set(key, value);
        if (store.size > capacity) {
            const oldest = store.keys().next().value as K;
            store.delete(oldest);
        }
    }

    function size(): number {
        return store.size;
    }

    return { get, put, size };
}

const LRUCache = makeLRUCache;
export { LRUCache };
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `lru_e2`

```ts
export class LRUCache<K, V> {
    public readonly get: (key: K) => V | undefined;
    public readonly put: (key: K, value: V) => void;
    public readonly size: () => number;

    constructor(capacity: number) {
        const store = new Map<K, V>();

        this.get = (key) => {
            const v = store.get(key);
            if (v === undefined) return undefined;
            store.delete(key);
            store.set(key, v);
            return v;
        };

        this.put = (key, value) => {
            if (store.has(key)) {
                store.delete(key);
            } else if (store.size >= capacity) {
                const oldest = store.keys().next().value as K;
                store.delete(oldest);
            }
            store.set(key, value);
        };

        this.size = () => store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `lru_f1`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store: Map<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.store = new Map();
    }

    get(key: K): V | undefined {
        return this.store.get(key);
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `lru_f2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();
    private order: K[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const idx = this.order.indexOf(key);
        if (idx !== -1) this.order.splice(idx, 1);
        this.order.push(key);
        return this.store.get(key);
    }

    put(key: K, value: V): void {
        this.store.set(key, value);
        this.order.push(key);
        while (this.order.length > this.capacity) {
            const evict = this.order.shift()!;
            if (!this.order.includes(evict)) {
                this.store.delete(evict);
            }
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `lru_f3`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();
    private order: K[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const idx = this.order.indexOf(key);
        if (idx !== -1) this.order.splice(idx, 1);
        this.order.push(key);
        return this.store.get(key);
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) {
            const idx = this.order.indexOf(key);
            if (idx !== -1) this.order.splice(idx, 1);
        }
        this.store.set(key, value);
        this.order.push(key);
        if (this.order.length > this.capacity) {
            const evict = this.order.pop()!;
            this.store.delete(evict);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `lru_f4`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity + 1) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `lru_f5`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.capacity;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `lru_g1`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        while (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.has(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `lru_g2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | null {
        if (!this.store.has(key)) return null;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `lru_h1`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 21. `lru_h2`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store = new Map<K, V>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!store.has(key)) return undefined;
        const v = store.get(key)!;
        store.delete(key);
        store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 22. `lru_h3`

```ts
class LRUCache<K, V> {
    private capacity: number;
    private store: Map<K, V, V> = new Map();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        const v = this.store.get(key)!;
        this.store.delete(key);
        this.store.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.store.has(key)) this.store.delete(key);
        this.store.set(key, value);
        if (this.store.size > this.capacity) {
            const oldest = this.store.keys().next().value as K;
            this.store.delete(oldest);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 23. `lru_i1`

```ts
class RecencyList<K> {
    private order: K[] = [];

    touch(key: K): void {
        const idx = this.order.indexOf(key);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(key);
    }

    evictOldest(): K | undefined {
        return this.order.shift();
    }

    size(): number {
        return this.order.length;
    }
}

export class LRUCache<K, V> {
    private readonly capacity: number;
    private readonly store = new Map<K, V>();
    private readonly recency = new RecencyList<K>();

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        if (!this.store.has(key)) return undefined;
        this.recency.touch(key);
        return this.store.get(key);
    }

    put(key: K, value: V): void {
        this.store.set(key, value);
        this.recency.touch(key);
        if (this.store.size > this.capacity) {
            const evict = this.recency.evictOldest();
            if (evict !== undefined) this.store.delete(evict);
        }
    }

    size(): number {
        return this.store.size;
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 24. `lru_i2`

```ts
class LRUCache<K, V> {
    private readonly capacity: number;
    private readonly entries = new Map<K, V>();
    protected hits = 0;
    protected misses = 0;

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: K): V | undefined {
        const v = this.entries.get(key);
        if (v === undefined) {
            this.misses++;
            return undefined;
        }
        this.hits++;
        this.entries.delete(key);
        this.entries.set(key, v);
        return v;
    }

    put(key: K, value: V): void {
        if (this.entries.has(key)) this.entries.delete(key);
        else if (this.entries.size >= this.capacity) {
            const oldest = this.entries.keys().next().value as K;
            this.entries.delete(oldest);
        }
        this.entries.set(key, value);
    }

    size(): number {
        return this.entries.size;
    }

    hitRate(): number {
        const total = this.hits + this.misses;
        return total === 0 ? 0 : this.hits / total;
    }
}

export class CountingLRUCache<K, V> extends LRUCache<K, V> {
    public stats(): { hits: number; misses: number } {
        return { hits: this.hits, misses: this.misses };
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 25. `lru_i3`

```ts
interface Cache<K, V> {
    get(key: K): V | undefined;
    put(key: K, value: V): void;
    size(): number;
}

abstract class AbstractEvictingCache<K, V> implements Cache<K, V> {
    protected readonly entries = new Map<K, V>();
    constructor(protected readonly capacity: number) {}

    abstract get(key: K): V | undefined;

    put(key: K, value: V): void {
        if (this.entries.has(key)) this.entries.delete(key);
        else if (this.entries.size >= this.capacity) this.evict();
        this.entries.set(key, value);
    }

    protected abstract evict(): void;

    size(): number {
        return this.entries.size;
    }
}

export class LRUCache<K, V> extends AbstractEvictingCache<K, V> {
    get(key: K): V | undefined {
        const v = this.entries.get(key);
        if (v === undefined) return undefined;
        this.entries.delete(key);
        this.entries.set(key, v);
        return v;
    }

    protected evict(): void {
        const oldest = this.entries.keys().next().value as K;
        this.entries.delete(oldest);
    }
}
```

> Correctness: ____/40  Data Structures: ____/25  Efficiency: ____/20  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:
