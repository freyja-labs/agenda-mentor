/* Prompt builder. Runs entirely in the browser: the form state lives in localStorage
   (when the browser allows it) and nothing is sent anywhere. */
(function () {
  "use strict";
  var dataEl = document.getElementById("portal-data");
  var root = document.getElementById("builder");
  if (!dataEl || !root) return;
  var PORTAL = JSON.parse(dataEl.textContent);
  var form = document.getElementById("intake");
  // The form never submits: a submission would put every answer into the page address,
  // where the host's request logs and the browser's history would keep it.
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  var sheet = document.getElementById("sheet");
  var statusEl = document.getElementById("p-status");
  var notesEl = document.getElementById("p-notes");
  var hintEl = document.getElementById("profile-hint");
  var clearBtn = document.getElementById("clear");
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var LABELS = {
    name: "full name", surname: "surname", title: "title", department: "department", institution: "institution",
    field: "field", wants: "what you want to be known for", funding: "current funding", people: "people",
    load: "teaching and service load", context: "institutional context", whiteboard: "whiteboard transcription",
    career_stage: "career stage", mentor: "mentor", constraints: "things to leave out", series: "landscape notes"
  };

  root.hidden = false;
  var lastText = "";
  var lastPrompt = null;

  function store(get, value) {
    try {
      if (get) return JSON.parse(window.localStorage.getItem(PORTAL.storageKey) || "{}");
      window.localStorage.setItem(PORTAL.storageKey, JSON.stringify(value));
    } catch (e) { /* storage blocked: the form still works for this visit */ }
    return {};
  }

  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function readForm() {
    var v = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name) v[el.name] = (el.value || "").trim();
    });
    return v;
  }

  function writeForm(v) {
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name && Object.prototype.hasOwnProperty.call(v, el.name)) el.value = v[el.name];
    });
  }

  function profileById(id) {
    for (var i = 0; i < PORTAL.profiles.length; i++) if (PORTAL.profiles[i].id === id) return PORTAL.profiles[i];
    return PORTAL.profiles[0];
  }

  function values(raw) {
    var v = Object.assign({}, raw);
    var p = profileById(raw.profile);
    var iso = /^\d{4}-\d{2}-\d{2}$/.test(raw.date_iso || "") ? raw.date_iso : today();
    var y = parseInt(iso.slice(0, 4), 10), m = parseInt(iso.slice(5, 7), 10) - 1, d = parseInt(iso.slice(8, 10), 10);
    v.date = MONTHS[m] + " " + d + ", " + y;
    v.month_year = MONTHS[m] + " " + y;
    v.year_plus_2 = String(y + 2);
    v.year_plus_5 = String(y + 5);
    v.year_plus_6 = String(y + 6);
    v.horizon_years = raw.horizon_years || "5";
    v.makeorbreak_months = raw.makeorbreak_months || "24";
    v.agenda_term = p.agenda_term;
    v.agenda_title_prefix = p.agenda_title_prefix;
    v.discipline_profile = p.block;
    return v;
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // {{#if x}}...{{/if}} keeps its body when x has a value; {{x}} is replaced by the value.
  // Unfilled placeholders stay in the text so the prompt never silently drops a slot.
  function render(tpl, v) {
    var ifRe = /\{\{#if (\w+)\}\}((?:(?!\{\{#if )[\s\S])*?)\{\{\/if\}\}/;
    var guard = 0;
    while (ifRe.test(tpl) && guard++ < 200) {
      tpl = tpl.replace(ifRe, function (_m, key, body) { return v[key] ? body : ""; });
    }
    var todo = [];
    var text = tpl.replace(/\{\{(\w+)\}\}/g, function (m, key) {
      if (v[key]) return v[key];
      if (todo.indexOf(key) < 0) todo.push(key);
      return m;
    });
    text = text.replace(/\n{3,}/g, "\n\n");
    var htmlOut = esc(text).replace(/\{\{(\w+)\}\}/g, function (_m, key) {
      return '<mark title="Empty field">' + esc(LABELS[key] || key) + "</mark>";
    });
    return { text: text, html: htmlOut, todo: todo };
  }

  function currentPrompt() {
    var pick = form.ownerDocument.querySelector('input[name="pick"]:checked');
    var id = pick ? pick.value : PORTAL.prompts[0].id;
    for (var i = 0; i < PORTAL.prompts.length; i++) if (PORTAL.prompts[i].id === id) return PORTAL.prompts[i];
    return PORTAL.prompts[0];
  }

  function update(save) {
    var raw = readForm();
    if (save) store(false, raw);
    var p = profileById(raw.profile);
    hintEl.innerHTML = esc(p.summary) + (p.reviewed_by ? "" : ' <span class="flag">Not yet reviewed by a senior colleague in the field.</span>');
    var pr = currentPrompt();
    var out = render(pr.body, values(raw));
    lastText = out.text;
    lastPrompt = pr;
    notesEl.innerHTML = pr.notes_html;
    sheet.innerHTML = out.html;
    if (out.todo.length) {
      statusEl.textContent = out.todo.length + (out.todo.length === 1 ? " field is" : " fields are") + " still empty and marked in red: " +
        out.todo.map(function (k) { return LABELS[k] || k; }).join(", ") + ".";
      statusEl.className = "p-status has-todo";
    } else {
      statusEl.textContent = "Every field this prompt uses is filled in.";
      statusEl.className = "p-status";
    }
  }

  function say(msg) {
    statusEl.textContent = msg;
    statusEl.className = "p-status";
  }

  document.getElementById("copy").addEventListener("click", function () {
    var done = function () { say("Copied prompt " + lastPrompt.n + ". Paste it into your AI assistant and attach the files it asks for."); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(lastText).then(done, function () { fallbackCopy(); done(); });
    } else { fallbackCopy(); done(); }
  });

  function fallbackCopy() {
    var ta = document.createElement("textarea");
    ta.value = lastText;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) { /* the sheet stays selectable */ }
    document.body.removeChild(ta);
  }

  function save(text, type, name) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: type }));
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    return name;
  }

  document.getElementById("download").addEventListener("click", function () {
    var name = "prompt-" + String(lastPrompt.n).padStart(2, "0") + "-" + lastPrompt.id.replace(/^\d+-/, "") + ".md";
    say("Downloaded " + save(lastText, "text/markdown;charset=utf-8", name) + ".");
  });

  // "Download your answers": the form as an agenda-mentor/1 file, the format Facultory's
  // Import JSON reads. It is built here and saved to this computer; nothing is sent.
  var CAREER = { "assistant professor": "assistant", "associate professor": "associate", "full professor": "full" };
  function intIn(s, lo, hi, dflt) {
    var n = parseInt(s, 10);
    return isNaN(n) ? dflt : Math.min(hi, Math.max(lo, n));
  }
  function portable(raw) {
    var p = profileById(raw.profile);
    var doc = {
      format: PORTAL.format,
      title: p.agenda_title_prefix + (raw.name ? " — " + raw.name : ""),
      owner: { name: raw.name || "", career_stage: CAREER[raw.career_stage] || "other" },
      discipline: p.id,
      dated: /^\d{4}-\d{2}-\d{2}$/.test(raw.date_iso || "") ? raw.date_iso : today(),
      horizon_years: intIn(raw.horizon_years, 1, 10, 5),
      makeorbreak_months: intIn(raw.makeorbreak_months, 6, 48, 24),
      sections: {}
    };
    ["title", "department", "institution"].forEach(function (k) { if (raw[k]) doc.owner[k] = raw[k]; });
    if (raw.field) doc.field = raw.field;
    if (raw.whiteboard) doc.whiteboard = raw.whiteboard;
    var intake = {};
    PORTAL.intakeKeys.forEach(function (k) { if (raw[k]) intake[k] = raw[k]; });
    if (Object.keys(intake).length) doc.intake = intake;
    return doc;
  }
  var exportRow = document.getElementById("export-row");
  var exportBtn = document.getElementById("export");
  var exportStatus = document.getElementById("export-status");
  if (exportRow && exportBtn) {
    exportRow.hidden = false;
    exportBtn.addEventListener("click", function () {
      var doc = portable(readForm());
      var name = save(JSON.stringify(doc, null, 2) + "\n", "application/json", "agenda-answers-" + doc.dated + ".json");
      if (exportStatus) exportStatus.textContent = "Saved " + name + ".";
    });
  }

  var armed = null;
  clearBtn.addEventListener("click", function () {
    if (!armed) {
      clearBtn.textContent = "Click again to clear everything";
      armed = setTimeout(function () { clearBtn.textContent = "Clear the form"; armed = null; }, 4000);
      return;
    }
    clearTimeout(armed);
    armed = null;
    clearBtn.textContent = "Clear the form";
    form.reset();
    document.getElementById("f-date").value = today();
    store(false, {});
    update(false);
    say("Form cleared, here and in this browser's storage.");
  });

  form.addEventListener("input", function () { update(true); });
  form.addEventListener("change", function () { update(true); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name="pick"]'), function (r) {
    r.addEventListener("change", function () { update(false); });
  });

  function pickFromHash() {
    var m = /^#p(.+)$/.exec(window.location.hash || "");
    if (!m) return;
    var r = document.querySelector('input[name="pick"][value="' + m[1].replace(/"/g, "") + '"]');
    if (r) r.checked = true;
  }
  window.addEventListener("hashchange", function () { pickFromHash(); update(false); });

  writeForm(store(true));
  if (!document.getElementById("f-date").value) document.getElementById("f-date").value = today();
  pickFromHash();
  update(false);
})();
