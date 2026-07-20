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
