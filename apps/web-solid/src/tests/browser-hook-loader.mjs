// Loaded via --import in vmForks execArgv.
// Registers the ESM resolve hook that forces 'browser' export conditions
// for solid-js/* packages so they resolve to the DOM build (web.js) instead
// of the SSR build (server.js) that Node.js picks via the 'node' condition.
import { register } from 'node:module'
register(new URL('./browser-conditions.mjs', import.meta.url), import.meta.url)
