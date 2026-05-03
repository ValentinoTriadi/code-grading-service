class DLLNode<K, V> {
    key: K;
    value: V;
    prev: DLLNode<K, V> | null = null;
    next: DLLNode<K, V> | null = null;
    constructor(key: K, value: V) {
        this.key = key;
        this.value = value;
    }
}

class LRUCache<K, V> {
    private capacity: number;
    private map: Map<K, DLLNode<K, V>>;
    private head: DLLNode<K, V>;
    private tail: DLLNode<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.map = new Map();
        this.head = new DLLNode<K, V>(null as unknown as K, null as unknown as V);
        this.tail = new DLLNode<K, V>(null as unknown as K, null as unknown as V);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    private removeNode(n: DLLNode<K, V>): void {
        const p = n.prev!;
        const nx = n.next!;
        p.next = nx;
        nx.prev = p;
    }

    private addToFront(n: DLLNode<K, V>): void {
        n.prev = this.head;
        n.next = this.head.next;
        this.head.next!.prev = n;
        this.head.next = n;
    }

    get(key: K): V | undefined {
        const node = this.map.get(key);
        if (!node) return undefined;
        this.removeNode(node);
        this.addToFront(node);
        return node.value;
    }

    put(key: K, value: V): void {
        const existing = this.map.get(key);
        if (existing) {
            this.removeNode(existing);
            this.map.delete(key);
        }
        const node = new DLLNode(key, value);
        this.addToFront(node);
        this.map.set(key, node);
        if (this.map.size > this.capacity) {
            const lru = this.tail.prev!;
            this.removeNode(lru);
            this.map.delete(lru.key);
        }
    }

    size(): number {
        return this.map.size;
    }
}
