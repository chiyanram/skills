`body as Order` checks nothing; parse it instead: `const body: unknown = await res.json(); return OrderSchema.parse(body);` with `Order = z.infer<typeof OrderSchema>`.
