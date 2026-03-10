// ESM resolve hook: strips the 'node' condition for solid-js/* imports
// so the 'browser' (or default) export maps to the DOM build (web.js)
// rather than the SSR build (server.js).
export async function resolve(specifier, context, nextResolve) {
  if (/^(solid-js|@solidjs\/)/.test(specifier)) {
    const filtered = (context.conditions ?? []).filter(
      (c) => c !== 'node' && c !== 'worker',
    )
    const conditions = filtered.includes('browser')
      ? filtered
      : ['browser', ...filtered]
    return nextResolve(specifier, { ...context, conditions })
  }
  return nextResolve(specifier, context)
}
