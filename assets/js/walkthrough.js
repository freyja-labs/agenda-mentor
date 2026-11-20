/* Agenda Mentor: the home page walkthrough.

   One whiteboard, one step per stage. It plays once through when it comes into view, pauses
   while it is out of view or the tab is hidden, and stops for good when someone picks a step.
   With reduced motion it never plays on its own and nothing draws; the steps still work.
   The steps follow the tabs pattern: arrow keys, Home, and End move between them, and moving
   into them from the keyboard stops the autoplay.

   The page's content security policy allows no inline style, so the timing lives in
   site.css: this file switches classes and sets one custom property through the CSSOM. */
(() => {
  "use strict";

  const walk = document.querySelector("[data-walk]");
  if (!walk) return;
  const board = walk.querySelector(".walk-board");
  const toggle = walk.querySelector(".walk-toggle");
  const list = walk.querySelector(".walk-steps");
  const tabs = Array.from(walk.querySelectorAll('[role="tab"]'));
  const panels = tabs.map((t) => document.getElementById(t.getAttribute("aria-controls")));
  if (!board || !toggle || !list || !tabs.length || panels.some((p) => !p)) return;

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const last = tabs.length;
  let step = 1;
  let mode = "pending"; // pending, playing, paused, stopped, or done
  let userPaused = false;
  let inView = !("IntersectionObserver" in window);
  let fontsIn = false;

  panels.forEach((p, i) => {
    p.setAttribute("role", "tabpanel");
    p.setAttribute("aria-labelledby", tabs[i].id);
    // The tab already names the step; the caption's own title is for the eye.
    p.querySelectorAll(".say-t").forEach((t) => t.setAttribute("aria-hidden", "true"));
  });

  // Long enough to read the caption after the drawing finishes.
  function dwell(n) {
    const words = panels[n - 1].textContent.trim().split(/\s+/).length;
    return Math.min(9500, Math.max(6000, 2600 + words * 200));
  }

  function label() {
    toggle.textContent = mode === "playing" ? "Pause" : mode === "done" ? "Replay" : "Play";
  }

  function show(n, draw) {
    step = n;
    walk.dataset.step = String(n);
    tabs.forEach((t, i) => {
      const on = i === n - 1;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      t.classList.toggle("is-past", i < n - 1);
      t.classList.remove("is-timing");
    });
    panels.forEach((p, i) => p.classList.toggle("is-on", i === n - 1));
    board.querySelectorAll(".go").forEach((el) => el.classList.remove("go"));
    if (draw) {
      void board.getBoundingClientRect(); // so a repeated step draws again from the start
      board.querySelectorAll(".a" + n).forEach((el) => el.classList.add("go"));
    }
  }

  function time() {
    const tab = tabs[step - 1];
    walk.style.setProperty("--walk-dwell", dwell(step) + "ms");
    tab.classList.remove("is-timing");
    void tab.offsetWidth;
    tab.classList.add("is-timing");
  }

  function play(from) {
    walk.classList.remove("is-pending", "is-paused");
    mode = "playing";
    userPaused = false;
    show(from, true);
    time();
    label();
  }

  function pause(byUser) {
    if (mode !== "playing") return;
    mode = "paused";
    userPaused = byUser;
    walk.classList.add("is-paused");
    label();
  }

  function resume() {
    if (mode !== "paused") return;
    mode = "playing";
    userPaused = false;
    walk.classList.remove("is-paused");
    label();
  }

  function stop() {
    if (mode === "stopped") return;
    mode = "stopped";
    walk.classList.remove("is-pending", "is-paused");
    tabs.forEach((t) => t.classList.remove("is-timing"));
    label();
  }

  function choose(n, focus) {
    stop();
    show(n, true);
    if (focus) tabs[n - 1].focus();
  }

  // The bar under the current step is the clock: when it fills, the next step starts.
  list.addEventListener("animationend", (e) => {
    if (e.animationName !== "wt-progress" || mode !== "playing") return;
    if (step < last) {
      show(step + 1, true);
      time();
    } else {
      mode = "done";
      tabs.forEach((t) => t.classList.remove("is-timing"));
      label();
    }
  });

  toggle.addEventListener("click", () => {
    if (mode === "playing") pause(true);
    else if (mode === "paused") resume();
    else if (mode === "pending" || mode === "done") play(1);
    else play(step);
  });

  tabs.forEach((t, i) => {
    t.addEventListener("click", () => choose(i + 1, false));
    t.addEventListener("keydown", (e) => {
      const next = (i + 1) % last + 1;
      const prev = (i + last - 1) % last + 1;
      const keys = { ArrowRight: next, ArrowDown: next, ArrowLeft: prev, ArrowUp: prev, Home: 1, End: last };
      if (!(e.key in keys)) return;
      e.preventDefault();
      choose(keys[e.key], true);
    });
  });
  list.addEventListener("focusin", () => {
    if (mode === "playing" || mode === "paused") stop();
  });

  function maybeStart() {
    if (mode === "pending" && fontsIn && inView && !reduce.matches) play(1);
  }

  if ("IntersectionObserver" in window) {
    new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        inView = entry.isIntersecting;
        if (!inView) pause(false);
        else if (mode === "paused" && !userPaused && !document.hidden) resume();
        maybeStart();
      });
    }, { threshold: 0.4 }).observe(board);
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause(false);
    else if (mode === "paused" && !userPaused && inView) resume();
  });

  if (reduce.addEventListener) {
    reduce.addEventListener("change", () => {
      if (!reduce.matches) return;
      if (mode === "pending") show(step, false);
      stop();
    });
  }

  // Start on a blank board and draw once the hand face is in, so the first words do not jump.
  walk.classList.add("is-ready");
  if (reduce.matches) mode = "stopped";
  else walk.classList.add("is-pending");
  show(1, false);
  label();

  const fonts = document.fonts;
  const loaded = fonts && fonts.load
    ? Promise.all([fonts.load('700 40px "Kalam"'), fonts.load('400 27px "Kalam"')]).catch(() => {})
    : Promise.resolve();
  Promise.race([loaded, new Promise((r) => setTimeout(r, 1500))]).then(() => {
    fontsIn = true;
    maybeStart();
  });
})();
