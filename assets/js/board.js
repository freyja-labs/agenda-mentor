/* Agenda Mentor: the typed board.

   The whiteboard's regions with text boxes on its writing lines. The board saves in this
   browser as you type, and nothing is sent anywhere. "Send to the prompt builder" writes the
   board's text into the builder's saved answers, the same browser storage the builder reads,
   so the builder opens on prompt 2 with the transcription filled in. The text follows the
   parts prompt 1 returns for a photographed board, so the draft reads both the same way. */
(function () {
  "use strict";
  var wrap = document.getElementById("tb-wrap");
  var form = document.getElementById("tb");
  var dataEl = document.getElementById("tb-data");
  if (!wrap || !form || !dataEl) return;
  var CFG = JSON.parse(dataEl.textContent);
  var out = document.getElementById("tb-out");
  var statusEl = document.getElementById("tb-status");
  var send = document.getElementById("tb-send");
  var plain = document.getElementById("tb-plain");
  var clearBtn = document.getElementById("tb-clear");
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var CHALLENGES = [1, 2, 3];
  var SEND_LABEL = send.textContent;
  var CLEAR_LABEL = clearBtn.textContent;

  wrap.hidden = false;
  // The form never submits: a submission would put the board into the page address.
  form.addEventListener("submit", function (e) { e.preventDefault(); });

  // Storage. load() returns null when the browser refuses access, {} when nothing is saved.
  function load(key) {
    try { return JSON.parse(window.localStorage.getItem(key) || "{}") || {}; } catch (e) { return null; }
  }
  function keep(key, value) {
    try { window.localStorage.setItem(key, JSON.stringify(value)); return true; } catch (e) { return false; }
  }

  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function longDate(iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || "")) iso = today();
    return MONTHS[parseInt(iso.slice(5, 7), 10) - 1] + " " + parseInt(iso.slice(8, 10), 10) + ", " + iso.slice(0, 4);
  }

  function readBoard() {
    var v = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name) return;
      if (el.type === "radio") { if (el.checked) v[el.name] = el.value; return; }
      v[el.name] = el.value;
    });
    return v;
  }
  function writeBoard(v) {
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name) return;
      if (el.type === "radio") el.checked = v[el.name] === el.value;
      else if (typeof v[el.name] === "string") el.value = v[el.name];
    });
  }

  function clean(s) { return String(s || "").replace(/\r\n?/g, "\n").trim(); }
  // A blank box says so: the draft labels anything the board left blank as a suggestion.
  function said(s, indent) {
    s = clean(s);
    return s ? s.split("\n").map(function (l) { return l.trim(); }).join("\n" + indent) : "(blank)";
  }
  function isBlank(v) {
    return Object.keys(v).every(function (k) { return k === "lead" || !clean(v[k]); });
  }

  // The parts of prompt 1's transcription: field, area, topic, objective, the numbered
  // challenges with what is written under each, then anything else on the board.
  function boardText(v, dated) {
    var lines = [
      "Typed board from the session on " + longDate(dated) + ". There is no photo; this text is the board.",
      "",
      "- Field: " + said(v.field, "  "),
      "- Area: " + said(v.area, "  "),
      "- Topic: " + said(v.topic, "  "),
      "- Objective: " + said(v.objective, "  "),
      "- Numbered challenges:"
    ];
    CHALLENGES.forEach(function (n) {
      var k = "c" + n + "_";
      var lead = v.lead === String(n) ? " (circled: lead with this one)" : "";
      if (!clean(v[k + "text"]) && !clean(v[k + "started"]) && !clean(v[k + "looking"]) && !clean(v[k + "red"])) {
        lines.push("  " + n + ". (blank)" + lead);
        return;
      }
      lines.push("  " + n + ". " + said(v[k + "text"], "     ") + lead);
      lines.push("     Who started this: " + said(v[k + "started"], "       "));
      lines.push("     Who else is looking: " + said(v[k + "looking"], "       "));
      lines.push("     Challenger's questions (red pen): " + said(v[k + "red"], "       "));
    });
    lines.push("- Arrows and anything else on the board: " + said(v.other, "  "));
    return lines.join("\n");
  }

  function say(msg, warn) {
    statusEl.textContent = msg;
    statusEl.className = "p-status" + (warn ? " has-todo" : "");
  }

  // Text areas grow with what is written in them, the way a board has room below each line.
  var areas = form.querySelectorAll("textarea");
  function grow(ta) {
    ta.style.height = "auto";
    ta.style.height = ta.scrollHeight + "px";
  }
  function growAll() { Array.prototype.forEach.call(areas, grow); }

  // On paper a text area keeps its screen height and cuts off what does not fit, so each one
  // has a plain twin that prints in its place and grows with its text.
  var twins = Array.prototype.map.call(areas, function (ta) {
    var d = document.createElement("div");
    d.className = ta.className + " tb-mirror";
    d.setAttribute("aria-hidden", "true");
    ta.insertAdjacentElement("afterend", d);
    return d;
  });
  function mirror() {
    Array.prototype.forEach.call(areas, function (ta, i) { twins[i].textContent = ta.value; });
  }

  function markLead(v) {
    CHALLENGES.forEach(function (n) {
      document.getElementById("tb-c" + n).classList.toggle("is-lead", v.lead === String(n));
    });
  }

  var board = load(CFG.storageKey);
  var canKeep = board !== null && keep(CFG.storageKey, board);
  board = board || {};
  var lead = board.lead || "";
  var overLimit = false;

  function sync(save) {
    var v = readBoard();
    markLead(v);
    if (save) {
      board = Object.assign({}, v, { plain: plain.checked, updated: today() });
      keep(CFG.storageKey, board);
    }
    var text = boardText(v, board.updated);
    out.textContent = text;
    mirror();
    if (text.length > CFG.limit) {
      overLimit = true;
      say("The board's text is " + text.length.toLocaleString() + " characters, and Facultory keeps the first " +
          CFG.limit.toLocaleString() + ". Shorten the longest answers before you import it.", true);
    } else if (overLimit) {
      overLimit = false;
      say("");
    }
    return text;
  }

  form.addEventListener("input", function (e) {
    var el = e.target;
    // A one-line box keeps one line of text, even when a paste brings line breaks.
    if (el.classList.contains("tb-line") && /\n/.test(el.value)) el.value = el.value.replace(/\s*\n\s*/g, " ");
    if (el.tagName === "TEXTAREA") grow(el);
    sync(true);
  });
  // Enter in a one-line box moves on to the next box, as Tab does.
  form.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || e.shiftKey || e.isComposing || !e.target.classList.contains("tb-line")) return;
    e.preventDefault();
    var fields = Array.prototype.filter.call(form.elements, function (el) { return el.tagName === "TEXTAREA"; });
    var next = fields[fields.indexOf(e.target) + 1];
    if (next) next.focus();
  });
  // A second click on the circled challenge takes the circle off, as an eraser would.
  form.addEventListener("click", function (e) {
    var r = e.target;
    if (r.name !== "lead") return;
    if (r.value === lead) { r.checked = false; lead = ""; } else { lead = r.value; }
    sync(true);
  });
  form.addEventListener("change", function (e) {
    if (e.target.name === "lead" && e.target.checked) lead = e.target.value;
    sync(true);
  });

  plain.addEventListener("change", function () {
    form.classList.toggle("tb-plain", plain.checked);
    growAll();
    sync(true);
  });

  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
    } else { fallbackCopy(text); done(); }
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) { /* the text below the board stays selectable */ }
    document.body.removeChild(ta);
  }

  var armed = null;
  function disarm() {
    if (armed) clearTimeout(armed);
    armed = null;
    send.textContent = SEND_LABEL;
  }
  send.addEventListener("click", function (e) {
    var v = readBoard();
    if (isBlank(v)) {
      e.preventDefault();
      say("The board is blank. Type the field and at least one challenge, then send it.");
      return;
    }
    var text = sync(false);
    var answers = load(CFG.builderKey);
    if (answers !== null) {
      var held = clean(answers.whiteboard);
      if (held && held !== clean(text) && !armed) {
        e.preventDefault();
        send.textContent = "Replace the builder's transcription";
        say("The prompt builder already holds a different whiteboard transcription. Select the button again to replace it with this board.");
        armed = setTimeout(disarm, 8000);
        return;
      }
      answers.whiteboard = text;
      if (keep(CFG.builderKey, answers)) { disarm(); return; } // the link opens the builder on prompt 2
    }
    e.preventDefault();
    disarm();
    copyText(text, function () {
      say("This browser is not keeping saved answers, so the board's text is on your clipboard. Open the prompt builder and paste it into the whiteboard field.", true);
    });
  });

  document.getElementById("tb-copy").addEventListener("click", function () {
    copyText(sync(false), function () { say("Copied the board's text."); });
  });

  document.getElementById("tb-download").addEventListener("click", function () {
    var dated = /^\d{4}-\d{2}-\d{2}$/.test(board.updated || "") ? board.updated : today();
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["# Typed board\n\n" + sync(false) + "\n"], { type: "text/markdown;charset=utf-8" }));
    a.download = "typed-board-" + dated + ".md";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    say("Downloaded " + a.download + ".");
  });

  document.getElementById("tb-print").addEventListener("click", function () { window.print(); });

  var clearArmed = null;
  clearBtn.addEventListener("click", function () {
    if (!clearArmed) {
      clearBtn.textContent = "Click again to clear the board";
      clearArmed = setTimeout(function () { clearBtn.textContent = CLEAR_LABEL; clearArmed = null; }, 4000);
      return;
    }
    clearTimeout(clearArmed);
    clearArmed = null;
    clearBtn.textContent = CLEAR_LABEL;
    form.reset();
    lead = "";
    board = { plain: plain.checked };
    keep(CFG.storageKey, board);
    growAll();
    sync(false);
    say("Board cleared, here and in this browser's storage. The prompt builder keeps anything already sent to it.");
  });

  writeBoard(board);
  plain.checked = !!board.plain;
  form.classList.toggle("tb-plain", plain.checked);
  growAll();
  sync(false);
  if (!canKeep) say("This browser is not keeping the board. Download it or copy its text before you leave this page.", true);

  // Heights depend on the hand face and the width, so measure again once the font is in
  // and whenever the window changes size.
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(growAll);
  var pending = false;
  window.addEventListener("resize", function () {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(function () { pending = false; growAll(); });
  });
})();
