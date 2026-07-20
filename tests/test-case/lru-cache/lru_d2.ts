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
