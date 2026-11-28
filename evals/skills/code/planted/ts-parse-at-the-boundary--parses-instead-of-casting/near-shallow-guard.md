Replace the cast with a guard: `const isOrder = (x: unknown): x is Order => typeof x === 'object' && x !== null && 'id' in x;`, then `if (!isOrder(body)) throw …`.
