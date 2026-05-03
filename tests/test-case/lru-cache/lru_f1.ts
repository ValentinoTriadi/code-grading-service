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
