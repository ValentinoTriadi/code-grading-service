class LRUCache {
    private capacity: number;
    private keys: any[] = [];
    private values: any[] = [];

    constructor(capacity: number) {
        this.capacity = capacity;
    }

    get(key: any): any {
        const idx = this.keys.indexOf(key);
        if (idx === -1) return undefined;
        const v = this.values[idx];
        this.keys.splice(idx, 1);
        this.values.splice(idx, 1);
        this.keys.push(key);
        this.values.push(v);
        return v;
    }

    put(key: any, value: any): void {
        const idx = this.keys.indexOf(key);
        if (idx !== -1) {
            this.keys.splice(idx, 1);
            this.values.splice(idx, 1);
        }
        this.keys.push(key);
        this.values.push(value);
        if (this.keys.length > this.capacity) {
            this.keys.shift();
            this.values.shift();
        }
    }

    size(): number {
        return this.keys.length;
    }
}
