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
