class LRUCache {
    capacity: number;
    map: Map<any, any>;

    constructor(capacity: number) {
        this.capacity = capacity;
        this.map = new Map();
    }

    get(key: any): any {
        if (!this.map.has(key)) return undefined;
        const v = this.map.get(key);
        this.map.delete(key);
        this.map.set(key, v);
        return v;
    }

    put(key: any, value: any): void {
        this.map.set(key, value);
        if (this.map.size > this.capacity) {
            const firstKey = this.map.keys().next().value;
            this.map.delete(firstKey);
        }
    }

    size(): number {
        return this.map.size;
    }
}
