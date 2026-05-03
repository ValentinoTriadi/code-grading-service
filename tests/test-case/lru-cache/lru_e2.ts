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
