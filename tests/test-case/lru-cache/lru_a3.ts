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
