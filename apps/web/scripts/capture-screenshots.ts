/**
 * Capture feature screenshots using Playwright + static HTML mockups.
 * Mockups visually match the dark-mode app UI so they render without auth.
 *
 * Usage:
 *   npx tsx scripts/capture-screenshots.ts
 *
 * Output: docs/screenshots/{name}.png (1280×800, cropped to content)
 */
import { chromium } from "playwright"
import { resolve } from "path"

const DOCS_DIR = resolve(__dirname, "../../../docs/screenshots")

async function captureScreenshots() {
  const browser = await chromium.launch()
  const page = await browser.newPage()
  await page.setViewportSize({ width: 1280, height: 800 })

  const features: Array<{ name: string; html: string }> = [
    { name: "ai-priority-toggle",  html: generateAIPriorityMockup() },
    { name: "command-palette",     html: generateCommandPaletteMockup() },
    { name: "semantic-groups",     html: generateSemanticGroupsMockup() },
    { name: "diff-viewer",         html: generateDiffViewerMockup() },
    { name: "timeline",            html: generateTimelineMockup() },
  ]

  for (const feature of features) {
    await page.setContent(feature.html, { waitUntil: "networkidle" })
    const outPath = `${DOCS_DIR}/${feature.name}.png`
    await page.screenshot({ path: outPath, fullPage: false })
    console.log(`Captured: ${outPath}`)
  }

  await browser.close()
}

function generateAIPriorityMockup(): string {
  return `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body { background: #0f172a; font-family: system-ui; }</style>
</head>
<body class="p-8 flex items-start gap-6">
  <div class="bg-slate-900 rounded-lg border border-slate-700 p-4 w-80 flex-shrink-0">
    <div class="flex items-center justify-between mb-3">
      <span class="text-slate-200 text-sm font-semibold">Files (5)</span>
      <button class="text-xs bg-blue-600 text-white px-2 py-1 rounded font-medium">AI Priority ✓</button>
    </div>
    <div class="bg-blue-950 border border-blue-800 rounded p-2 mb-3 text-xs text-blue-300">
      ⚡ Review these 2 files first: auth.ts, db.ts
    </div>
    <div class="space-y-1">
      <div class="flex items-center gap-2 p-2 rounded bg-slate-800 border-l-2 border-blue-500">
        <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
        <span class="text-slate-200 text-xs font-mono flex-1">src/auth/login.ts</span>
        <span class="text-green-400 text-[10px]">+48</span>
        <span class="text-red-400 text-[10px]">-12</span>
      </div>
      <div class="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 border-l-2 border-transparent">
        <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
        <span class="text-slate-300 text-xs font-mono flex-1">src/db/queries.ts</span>
        <span class="text-green-400 text-[10px]">+23</span>
        <span class="text-red-400 text-[10px]">-8</span>
      </div>
      <div class="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 border-l-2 border-transparent">
        <span class="bg-yellow-900 text-yellow-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Important</span>
        <span class="text-slate-300 text-xs font-mono flex-1">src/utils/format.ts</span>
        <span class="text-green-400 text-[10px]">+7</span>
        <span class="text-red-400 text-[10px]">-2</span>
      </div>
      <div class="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 border-l-2 border-transparent">
        <span class="bg-slate-700 text-slate-400 text-[10px] px-1.5 py-0.5 rounded font-semibold">Low</span>
        <span class="text-slate-400 text-xs font-mono flex-1">tests/auth.test.ts</span>
        <span class="text-green-400 text-[10px]">+15</span>
        <span class="text-red-400 text-[10px]">-0</span>
      </div>
      <div class="flex items-center gap-2 p-2 rounded hover:bg-slate-800/50 border-l-2 border-transparent">
        <span class="bg-slate-700 text-slate-400 text-[10px] px-1.5 py-0.5 rounded font-semibold">Low</span>
        <span class="text-slate-400 text-xs font-mono flex-1">README.md</span>
        <span class="text-green-400 text-[10px]">+3</span>
        <span class="text-red-400 text-[10px]">-1</span>
      </div>
    </div>
    <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500 flex gap-3">
      <span>AI ranked in 43ms</span>
      <span class="ml-auto">NDCG@5: 0.8485</span>
    </div>
  </div>
</body>
</html>`
}

function generateCommandPaletteMockup(): string {
  return `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body { background: #0f172a44; font-family: system-ui; }</style>
</head>
<body class="flex items-start justify-center pt-16 min-h-screen" style="background:#0f172a">
  <div class="w-full max-w-lg px-4">
    <div class="bg-slate-800 rounded-xl border border-slate-600 shadow-2xl overflow-hidden">
      <div class="flex items-center gap-2 px-3 py-3 border-b border-slate-700">
        <span class="text-slate-400 text-sm">⌘</span>
        <input class="flex-1 bg-transparent text-slate-200 text-sm outline-none" value="auth" readonly/>
        <kbd class="text-xs text-slate-500 border border-slate-600 rounded px-1.5 py-0.5">Esc</kbd>
      </div>
      <div class="p-2 max-h-72 overflow-y-auto">
        <div class="text-[10px] text-slate-500 uppercase tracking-wider px-2 py-1.5">Files</div>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-blue-600/15 border border-blue-500/20 mb-0.5">
          <span class="text-slate-200 text-sm flex-1">src/auth/login.ts</span>
          <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-700 mb-0.5">
          <span class="text-slate-300 text-sm flex-1">src/auth/session.ts</span>
          <span class="bg-yellow-900 text-yellow-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Important</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-700">
          <span class="text-slate-300 text-sm flex-1">src/auth/middleware.ts</span>
          <span class="bg-slate-700 text-slate-400 text-[10px] px-1.5 py-0.5 rounded font-semibold">Low</span>
        </div>
        <div class="text-[10px] text-slate-500 uppercase tracking-wider px-2 py-1.5 mt-1">Clusters</div>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-700">
          <div class="w-2 h-2 rounded-full bg-red-500 flex-shrink-0"></div>
          <span class="text-slate-300 text-sm flex-1">Authentication Changes</span>
          <span class="text-slate-500 text-xs">3 files</span>
        </div>
      </div>
    </div>
    <div class="text-center text-slate-600 text-xs mt-3">⌘K — jump to any file instantly</div>
  </div>
</body>
</html>`
}

function generateSemanticGroupsMockup(): string {
  return `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body { background: #0f172a; font-family: system-ui; }</style>
</head>
<body class="p-8">
  <div class="flex gap-4">
    <div class="bg-slate-900 rounded-lg border border-slate-700 p-4 w-64 flex-shrink-0">
      <div class="text-slate-200 text-sm font-semibold mb-1">Semantic Groups</div>
      <div class="text-slate-500 text-xs mb-3">CodeBERT + HDBSCAN clustering</div>
      <div class="space-y-2">
        <div class="border border-red-800/60 bg-red-950/20 rounded-lg p-3 cursor-pointer ring-1 ring-red-500/30">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full bg-red-500 flex-shrink-0"></div>
            <span class="text-red-300 text-xs font-medium flex-1">Authentication Changes</span>
          </div>
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500">3 files</span>
            <span class="text-slate-400">Coherence: 94%</span>
          </div>
        </div>
        <div class="border border-blue-800/60 bg-blue-950/20 rounded-lg p-3 cursor-pointer hover:border-blue-700">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
            <span class="text-blue-300 text-xs font-medium flex-1">Database Layer</span>
          </div>
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500">2 files</span>
            <span class="text-slate-400">Coherence: 88%</span>
          </div>
        </div>
        <div class="border border-emerald-800/60 bg-emerald-950/20 rounded-lg p-3 cursor-pointer hover:border-emerald-700">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0"></div>
            <span class="text-emerald-300 text-xs font-medium flex-1">Test Coverage</span>
          </div>
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500">2 files</span>
            <span class="text-slate-400">Coherence: 91%</span>
          </div>
        </div>
        <div class="border border-slate-700 bg-slate-800/30 rounded-lg p-3 cursor-pointer hover:border-slate-600">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-2 h-2 rounded-full bg-slate-500 flex-shrink-0"></div>
            <span class="text-slate-300 text-xs font-medium flex-1">Documentation</span>
          </div>
          <div class="flex justify-between text-[10px]">
            <span class="text-slate-500">1 file</span>
            <span class="text-slate-400">Coherence: 100%</span>
          </div>
        </div>
      </div>
    </div>
    <div class="bg-slate-900 rounded-lg border border-slate-700 p-4 flex-1">
      <div class="text-slate-400 text-xs mb-2 font-medium border-l-4 border-red-500 pl-2">Showing: Authentication Changes</div>
      <div class="space-y-1">
        <div class="flex items-center gap-2 p-2 rounded bg-slate-800/60 border-l-4 border-red-500">
          <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
          <span class="text-slate-200 text-xs font-mono flex-1">src/auth/login.ts</span>
          <span class="text-green-400 text-[10px]">+48</span>
        </div>
        <div class="flex items-center gap-2 p-2 rounded border-l-4 border-red-500">
          <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
          <span class="text-slate-300 text-xs font-mono flex-1">src/auth/session.ts</span>
          <span class="text-green-400 text-[10px]">+12</span>
        </div>
        <div class="flex items-center gap-2 p-2 rounded border-l-4 border-red-500">
          <span class="bg-yellow-900 text-yellow-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Important</span>
          <span class="text-slate-300 text-xs font-mono flex-1">src/auth/middleware.ts</span>
          <span class="text-green-400 text-[10px]">+6</span>
        </div>
      </div>
    </div>
  </div>
</body>
</html>`
}

function generateDiffViewerMockup(): string {
  return `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0f172a; font-family: monospace; }
    .add { background: rgba(34,197,94,0.08); }
    .del { background: rgba(239,68,68,0.08); }
    .add td:last-child { color: #86efac; }
    .del td:last-child { color: #fca5a5; }
    td { padding: 2px 12px; font-size: 12px; white-space: pre; }
    .ln { color: #475569; width: 32px; user-select: none; text-align: right; }
  </style>
</head>
<body class="p-6">
  <div class="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden max-w-2xl">
    <div class="flex items-center gap-2 px-4 py-2.5 border-b border-slate-700 bg-slate-800">
      <span class="bg-red-900 text-red-300 text-[10px] px-1.5 py-0.5 rounded font-semibold">Critical</span>
      <span class="text-slate-200 text-sm font-mono">src/auth/login.ts</span>
      <span class="ml-auto flex gap-2 text-xs">
        <span class="text-green-400">+5</span>
        <span class="text-red-400">-2</span>
      </span>
    </div>
    <table class="w-full border-collapse">
      <tr class="text-slate-500 bg-slate-800/40">
        <td class="ln">...</td><td class="text-slate-600 px-3 py-1 text-xs">@@ -10,8 +10,11 @@ import { db } from '../db'</td>
      </tr>
      <tr><td class="ln">10</td><td>import { hash, compare } from 'bcrypt'</td></tr>
      <tr><td class="ln">11</td><td> </td></tr>
      <tr class="del"><td class="ln">12</td><td>- async function login(user, pass) {</td></tr>
      <tr class="del"><td class="ln">13</td><td>-   return db.query(\`SELECT * WHERE user=\${user}\`)</td></tr>
      <tr class="add"><td class="ln">12</td><td>+ async function login(user: string, pass: string) {</td></tr>
      <tr class="add"><td class="ln">13</td><td>+   return db.query('SELECT * WHERE user=?', [user])</td></tr>
      <tr class="add"><td class="ln">14</td><td>+   // Fixed: parameterized query prevents SQL injection</td></tr>
      <tr><td class="ln">15</td><td>  }</td></tr>
    </table>
    <div class="border-t border-slate-700 bg-slate-800/40 px-4 py-3">
      <div class="flex items-start gap-2 mb-2">
        <div class="w-5 h-5 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white text-[10px] font-bold mt-0.5">R</div>
        <div class="bg-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 border border-slate-700 flex-1">
          SQL injection fix — parameterized queries are the right call here. Should we also add rate limiting on the login endpoint?
        </div>
      </div>
      <div class="flex gap-2 ml-7">
        <input class="flex-1 bg-slate-900 text-slate-400 text-xs px-3 py-1.5 rounded border border-slate-700 outline-none" placeholder="Reply..."/>
        <button class="text-xs bg-blue-600 text-white px-3 py-1.5 rounded font-medium">Post</button>
      </div>
    </div>
  </div>
</body>
</html>`
}

function generateTimelineMockup(): string {
  return `<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body { background: #0f172a; font-family: system-ui; }</style>
</head>
<body class="p-6">
  <div class="bg-slate-900 rounded-lg border border-slate-700 p-4 max-w-lg">
    <div class="text-slate-200 text-sm font-semibold mb-4">PR Timeline</div>
    <div class="relative">
      <div class="absolute left-3.5 top-0 bottom-0 w-px bg-slate-700"></div>
      <div class="space-y-4">
        <div class="flex items-start gap-3">
          <div class="w-7 h-7 rounded-full bg-green-900 border-2 border-green-600 flex-shrink-0 flex items-center justify-center text-green-400 text-xs z-10">✓</div>
          <div class="flex-1 pt-0.5">
            <div class="text-slate-200 text-xs font-medium">PR opened</div>
            <div class="text-slate-500 text-[10px] mt-0.5">ritunjaym · 2 hours ago</div>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="w-7 h-7 rounded-full bg-blue-900 border-2 border-blue-600 flex-shrink-0 flex items-center justify-center text-blue-400 text-xs z-10">⬡</div>
          <div class="flex-1 pt-0.5">
            <div class="text-slate-200 text-xs font-medium">Commit: fix SQL injection in login</div>
            <div class="text-slate-500 text-[10px] mt-0.5">abc1234 · 1 hour ago</div>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="w-7 h-7 rounded-full bg-slate-800 border-2 border-slate-600 flex-shrink-0 flex items-center justify-center text-slate-400 text-xs z-10">💬</div>
          <div class="flex-1 pt-0.5">
            <div class="text-slate-200 text-xs font-medium">Comment on src/auth/login.ts</div>
            <div class="text-slate-400 text-[10px] mt-0.5 bg-slate-800 rounded px-2 py-1">SQL injection fix — parameterized queries are correct here...</div>
            <div class="text-slate-500 text-[10px] mt-0.5">reviewer1 · 45 min ago</div>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="w-7 h-7 rounded-full bg-yellow-900 border-2 border-yellow-600 flex-shrink-0 flex items-center justify-center text-yellow-400 text-xs z-10">△</div>
          <div class="flex-1 pt-0.5">
            <div class="text-slate-200 text-xs font-medium">Review requested: changes requested</div>
            <div class="text-slate-500 text-[10px] mt-0.5">reviewer1 · 30 min ago</div>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <div class="w-7 h-7 rounded-full bg-emerald-900 border-2 border-emerald-600 flex-shrink-0 flex items-center justify-center text-emerald-400 text-xs z-10">⬡</div>
          <div class="flex-1 pt-0.5">
            <div class="text-slate-200 text-xs font-medium">Commit: add rate limiting to login</div>
            <div class="text-slate-500 text-[10px] mt-0.5">def5678 · 10 min ago</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>`
}

captureScreenshots().catch(console.error)
