// Build-time access to the assets written by tools/build_site_assets.py and to the art sources.
import { readFileSync } from "node:fs";

// astro build/dev run from the site root; module URLs move when the build bundles this file
const root = process.cwd().replace(/\/?$/, "/");

export function readJson<T = any>(path: string): T {
  return JSON.parse(readFileSync(root + path, "utf-8")) as T;
}

export function readText(path: string): string {
  return readFileSync(root + path, "utf-8");
}

export const site = () => readJson("public/data/site.json");
export const source = (model: string) => readText(`art/demo/models/${model}.kiln.yaml`).trimEnd();
export const asset = (url: string) => import.meta.env.BASE_URL.replace(/\/?$/, "/") + url.replace(/^\//, "");
/** The three styles' looks, for the in-browser viewer. */
export const looks = () => Object.fromEntries(Object.entries(site().styles).map(([k, v]: [string, any]) => [k, v.look]));

/** A showpiece's source for the page: its first parts (the head of the file is rig and animation numbers), long
 * lines cut short, and the whole file's line count. */
export function heroSource(project: string, model: string, show = 48, wide = 150): { excerpt: string; from: number; lines: number } {
  const all = readText(`art/heroes/${project}/models/${model}.kiln.yaml`).trimEnd().split("\n");
  const from = Math.max(0, all.indexOf("parts:"));
  const cut = (line: string) => (line.length > wide ? line.slice(0, wide) + " …" : line);
  return { excerpt: all.slice(from, from + show).map(cut).join("\n"), from: from + 1, lines: all.length };
}
