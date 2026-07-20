class LRUCache {
    capacity: number;
    cache: { [key: string]: any } = {};
    order: string[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: any): any {
        const k = String(key);
        if (!(k in this.cache)) return undefined;
        const idx = this.order.indexOf(k);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(k);
        return this.cache[k];
    }

    put(key: any, value: any): void {
        const k = String(key);
        this.cache[k] = value;
        const idx = this.order.indexOf(k);
        if (idx >= 0) this.order.splice(idx, 1);
        this.order.push(k);
        while (this.order.length > this.capacity) {
            const evict = this.order.shift()!;
            delete this.cache[evict];
        }
    }

    size(): number {
        return Object.keys(this.cache).length;
    }
}
