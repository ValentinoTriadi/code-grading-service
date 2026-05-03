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
