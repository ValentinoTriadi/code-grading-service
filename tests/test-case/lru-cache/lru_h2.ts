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
