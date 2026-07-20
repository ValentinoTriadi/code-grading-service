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
