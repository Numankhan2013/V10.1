/* PDF.js 6 calls Map/WeakMap getOrInsert and getOrInsertComputed (the 2026 "upsert"
   methods). Older browsers and Android WebViews lack them, and without them every
   range-loaded source PDF fails. Loaded before PDF.js on the page and in its worker. */
for (const Type of [Map, WeakMap]) {
  const proto = Type.prototype;
  if (typeof proto.getOrInsert !== 'function') {
    Object.defineProperty(proto, 'getOrInsert', {configurable: true, writable: true, value(key, value) {
      if (!this.has(key)) this.set(key, value);
      return this.get(key);
    }});
  }
  if (typeof proto.getOrInsertComputed !== 'function') {
    Object.defineProperty(proto, 'getOrInsertComputed', {configurable: true, writable: true, value(key, compute) {
      if (!this.has(key)) this.set(key, compute(key));
      return this.get(key);
    }});
  }
}
