function makeLRUCache<K, V>(capacity: number) {
    const store = new Map<K, V>();

    function get(key: K): V | undefined {
        if (!store.has(key)) return undefined;
        const v = store.get(key) as V;
        store.delete(key);
        store.set(key, v);
        return v;
    }

    function put(key: K, value: V): void {
        if (store.has(key)) store.delete(key);
        store.set(key, value);
        if (store.size > capacity) {
            const oldest = store.keys().next().value as K;
            store.delete(oldest);
        }
    }

    function size(): number {
        return store.size;
    }

    return { get, put, size };
}

const LRUCache = makeLRUCache;
export { LRUCache };
