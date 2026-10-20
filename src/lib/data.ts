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
