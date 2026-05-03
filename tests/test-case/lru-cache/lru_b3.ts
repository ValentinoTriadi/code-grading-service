class ListNode<K, V> {
    constructor(
        public key: K,
        public value: V,
        public prev: ListNode<K, V> | null = null,
        public next: ListNode<K, V> | null = null,
    ) {}
}

export class LRUCache<K, V> {
    private readonly capacity: number;
    private readonly index = new Map<K, ListNode<K, V>>();
    private readonly head: ListNode<K, V>;
    private readonly tail: ListNode<K, V>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.head = new ListNode<K, V>(null as unknown as K, null as unknown as V);
        this.tail = new ListNode<K, V>(null as unknown as K, null as unknown as V);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    private detach(node: ListNode<K, V>): void {
        node.prev!.next = node.next;
        node.next!.prev = node.prev;
    }

    private prepend(node: ListNode<K, V>): void {
        node.prev = this.head;
        node.next = this.head.next;
        this.head.next!.prev = node;
        this.head.next = node;
    }

    get(key: K): V | undefined {
        const node = this.index.get(key);
        if (!node) return undefined;
        this.detach(node);
        this.prepend(node);
        return node.value;
    }

    put(key: K, value: V): void {
        const existing = this.index.get(key);
        if (existing) {
            existing.value = value;
            this.detach(existing);
            this.prepend(existing);
            return;
        }

        if (this.index.size === this.capacity) {
            const lru = this.tail.prev!;
            this.detach(lru);
            this.index.delete(lru.key);
        }

        const node = new ListNode(key, value);
        this.prepend(node);
        this.index.set(key, node);
    }

    size(): number {
        return this.index.size;
    }
}
