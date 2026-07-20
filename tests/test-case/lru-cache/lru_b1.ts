class Node {
    key: any;
    value: any;
    prev: any = null;
    next: any = null;
    constructor(k: any, v: any) {
        this.key = k;
        this.value = v;
    }
}

class LRUCache {
    capacity: number;
    map: any = {};
    head: any;
    tail: any;
    count: number = 0;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.head = new Node(null, null);
        this.tail = new Node(null, null);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }

    _remove(n: any) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    _add(n: any) {
        n.prev = this.head;
        n.next = this.head.next;
        this.head.next.prev = n;
        this.head.next = n;
    }

    get(key: any) {
        const n = this.map[key];
        if (!n) return undefined;
        this._remove(n);
        this._add(n);
        return n.value;
    }

    put(key: any, value: any) {
        if (this.map[key]) {
            this._remove(this.map[key]);
            this.count--;
        }
        const n = new Node(key, value);
        this._add(n);
        this.map[key] = n;
        this.count++;
        if (this.count > this.capacity) {
            const lru = this.tail.prev;
            this._remove(lru);
            delete this.map[lru.key];
            this.count--;
        }
    }

    size() {
        return this.count;
    }
}
