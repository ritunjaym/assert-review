export const EXTENSION_TO_LANGUAGE: Record<string, string> = {
  ts: "typescript", tsx: "tsx", js: "javascript", jsx: "jsx",
  py: "python", go: "go", rs: "rust", java: "java",
  cpp: "cpp", cc: "cpp", cxx: "cpp", c: "c", h: "c",
  rb: "ruby", php: "php", md: "markdown", json: "json",
  yaml: "yaml", yml: "yaml", toml: "toml", sh: "bash",
  bash: "bash", zsh: "bash", css: "css", scss: "scss",
  html: "html", xml: "xml", sql: "sql", graphql: "graphql",
  kt: "kotlin", swift: "swift", scala: "scala", r: "r",
  lua: "lua", vim: "vim", dockerfile: "dockerfile",
}

export function detectLanguage(filename: string): string {
  const basename = filename.split("/").pop() ?? filename
  const lower = basename.toLowerCase()

  // Special filenames
  if (lower === "dockerfile") return "dockerfile"
  if (lower === "makefile") return "makefile"
  if (lower === ".gitignore" || lower === ".env.example") return "bash"

  const ext = lower.split(".").pop() ?? ""
  return EXTENSION_TO_LANGUAGE[ext] ?? "text"
}
