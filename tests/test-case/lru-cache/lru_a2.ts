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
