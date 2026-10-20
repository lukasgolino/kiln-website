// Small controls shared by the viewers: animation chips, play/pause, chip groups.
import type { Viewer } from "./viewer";

/** Fill `box` with one chip per animation of whatever the viewer shows. */
export function animChips(viewer: Viewer, box: HTMLElement) {
  viewer.onClips = (names) => {
    box.replaceChildren(
      ...names.map((name, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = name;
        b.setAttribute("aria-pressed", String(i === 0));
        b.addEventListener("click", () => {
          viewer.play(name);
          box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
        });
        return b;
      }),
    );
    box.hidden = names.length === 0;
  };
  const show = viewer.show.bind(viewer);
  viewer.show = async (url, look, anim) => {
    await show(url, look, anim);
    box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x.textContent === anim || (!anim && x === box.firstChild))));
  };
}

export function playButton(viewer: Viewer, button: HTMLButtonElement) {
  const sync = () => {
    button.textContent = viewer.playing ? "❚❚" : "▶";
    button.setAttribute("aria-label", viewer.playing ? "Pause" : "Play");
  };
  sync();
  button.addEventListener("click", () => {
    viewer.setPlaying(!viewer.playing);
    sync();
  });
}

/** A group of chips where one is pressed; calls `pick` with the chip's data-value. */
export function chipGroup(box: HTMLElement, pick: (value: string) => void) {
  const buttons = [...box.querySelectorAll<HTMLButtonElement>("button")];
  for (const b of buttons)
    b.addEventListener("click", () => {
      buttons.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      pick(b.dataset.value!);
    });
}
