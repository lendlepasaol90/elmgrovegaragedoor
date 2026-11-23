/* ------------------------------------------------------------
   QUOTE FORM DELIVERY (same setup as epoxyflooringtempeaz.com)
   Every lead-form submission on this site is emailed to FORM_EMAIL
   through FormSubmit (https://formsubmit.co) – no server needed.
   The very first submission from this domain sends an activation
   email to FORM_EMAIL; click "Activate Form" in it once and all
   later submissions are delivered.
   This script takes over the submit of every form on the page that
   has a name + phone field, so older placeholder handlers are skipped.
------------------------------------------------------------ */
(function () {
  "use strict";

  var FORM_EMAIL = "djcartledge9@hotmail.com";
  var FORM_ENDPOINT = "https://formsubmit.co/ajax/" + FORM_EMAIL;

  var me = document.currentScript;
  var SITE = (me && me.getAttribute("data-site")) || document.title.split(/[|│–-]/)[0].trim();

  var LABELS = {
    name: "Name", fullname: "Name", phone: "Phone", email: "Email",
    service: "Service", project: "Service", projecttype: "Service", type: "Service", finish: "Finish",
    "form-location": "Form section",
    city: "City", zip: "ZIP", neighborhood: "Neighborhood",
    sqft: "Approx. square feet", size: "Approx. square feet",
    property: "Property type", property_type: "Property type", best_time: "Best time to call", time: "Best time to call",
    "contact-preference": "Contact preference",
    message: "Project details", msg: "Project details", details: "Project details", notes: "Project details",
    source: "Form"
  };
  // Netlify leftovers / honeypots that should never be emailed
  var SKIP = { "_honey": 1, "form-name": 1, "bot-field": 1, "company_website": 1, page: 1 };
  var HP_NAMES = { "_honey": 1, "_gotcha": 1, "bot-field": 1, "company_website": 1 };
  var REAL = { name: 1, fullname: 1, phone: 1, email: 1, service: 1, project: 1, projecttype: 1, type: 1,
    message: 1, msg: 1, details: 1, notes: 1, zip: 1, city: 1, size: 1, sqft: 1 };

  // A honeypot is a hidden-from-people trap field: known name, or a text input
  // tucked inside an aria-hidden / .hp wrapper, or tabindex=-1 + autocomplete=off.
  function isHoneypot(el, form) {
    if (!el || !el.name || el.type === "hidden") return false;
    if (REAL[el.name.toLowerCase()]) return false; // never treat a real lead field as a trap
    if (HP_NAMES[el.name]) return true;
    if (el.name === "company" && form.hasAttribute("netlify-honeypot")) return true;
    // only the trap's own small wrapper – NOT a collapsed panel that happens to be aria-hidden
    if (el.closest && el.closest(".hp,.form__hp,.honeypot,.hp-field")) return true;
    return el.getAttribute("tabindex") === "-1" && el.getAttribute("autocomplete") === "off";
  }

  function field(form, n) {
    return form.querySelector('[name="' + n + '"]') || form.querySelector('[name="' + n.charAt(0).toUpperCase() + n.slice(1) + '"]');
  }
  function isLeadForm(form) { return !!(field(form, "name") && field(form, "phone")); }

  function phoneText() {
    var t = document.querySelector('a[href^="tel:"]');
    return t ? (t.textContent.trim() || t.getAttribute("href").slice(4)) : "";
  }

  function statusEl(form) {
    var s = form.querySelector(".fs-status");
    if (!s) {
      s = document.createElement("p");
      s.className = "fs-status";
      s.setAttribute("role", "status");
      s.setAttribute("aria-live", "polite");
      s.style.cssText = "margin:12px 0 0;font-size:.95rem;line-height:1.4;font-weight:600;padding:10px 12px;border-radius:8px;border-left:4px solid currentColor";
      var btn = form.querySelector("button[type=submit],input[type=submit],button:not([type])");
      if (btn && btn.parentNode) btn.parentNode.insertBefore(s, btn.nextSibling); else form.appendChild(s);
    }
    return s;
  }
  function show(form, kind, text) {
    var s = statusEl(form);
    s.style.display = "block";
    s.style.background = kind === "ok" ? "rgba(34,160,90,.12)" : "rgba(210,50,50,.12)";
    s.style.color = kind === "ok" ? "#1d7a45" : "#b42323";
    s.textContent = text;
    return s;
  }

  function prepare(form) {
    if (form.__fsReady) return;
    form.__fsReady = true;
    var hp = document.createElement("input");
    hp.type = "text"; hp.name = "_honey"; hp.tabIndex = -1; hp.autocomplete = "off";
    hp.setAttribute("aria-hidden", "true");
    hp.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0";
    form.appendChild(hp);
    // hide the old placeholder notes ("not connected yet", mailto hints)
    [].forEach.call(form.querySelectorAll(".note,.form-note,.form-ok,.form-msg"), function (n) { n.hidden = true; n.style.display = "none"; });
    [].forEach.call(form.querySelectorAll("input,textarea,select"), function (i) {
      i.addEventListener("input", function () { i.classList.remove("invalid"); i.removeAttribute("aria-invalid"); });
    });
  }

  function init() { [].forEach.call(document.forms, function (f) { if (isLeadForm(f)) prepare(f); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();

  // Capture phase: runs before (and stops) any older submit handler on the form.
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form || form.tagName !== "FORM" || !isLeadForm(form)) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    prepare(form);
    if (form.__fsBusy) return;

    var name = field(form, "name"), phone = field(form, "phone"), email = field(form, "email");
    var ok = true, first = null;
    [name, phone].forEach(function (f) {
      var bad = !f.value.trim();
      f.classList.toggle("invalid", bad);
      if (bad) { f.setAttribute("aria-invalid", "true"); ok = false; first = first || f; }
    });
    if (email && email.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      email.classList.add("invalid"); email.setAttribute("aria-invalid", "true"); ok = false; first = first || email;
    }
    if (!ok) {
      show(form, "err", first === email ? "Please check your email address." : "Please add your name and phone number so we can reach you.");
      if (first) first.focus();
      return;
    }

    // Spam traps: real visitors never fill these hidden fields
    var traps = {};
    var tripped = [].some.call(form.elements, function (el) {
      if (!isHoneypot(el, form)) return false;
      traps[el.name] = 1;
      return !!String(el.value).trim();
    });
    if (tripped) return;

    var raw = new FormData(form);
    var src = form.getAttribute("name") || form.id || "Website form";
    var data = new FormData();
    var seen = {};
    raw.forEach(function (v, k) {
      if (SKIP[k] || SKIP[k.toLowerCase()] || traps[k] || k.charAt(0) === "_" || !String(v).trim()) return;
      var label = LABELS[k.toLowerCase()] || k;
      if (seen[label]) label = label + " (" + k + ")";
      seen[label] = 1;
      data.append(label, v);
    });
    if (!seen.Form) data.append("Form", src);
    data.append("Page", window.location.href);
    data.append("_subject", "New quote request from " + name.value.trim() + " – " + SITE);
    data.append("_template", "table");
    data.append("_captcha", "false");
    if (email && email.value.trim()) data.append("_replyto", email.value.trim());

    var btn = form.querySelector("button[type=submit],input[type=submit],button:not([type])");
    var btnHTML = btn ? (btn.tagName === "INPUT" ? btn.value : btn.innerHTML) : "";
    form.__fsBusy = true;
    if (btn) { btn.disabled = true; if (btn.tagName === "INPUT") btn.value = "Sending…"; else btn.textContent = "Sending…"; }

    fetch(FORM_ENDPOINT, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then(function (res) { return res.json().catch(function () { return {}; }).then(function (j) { return { ok: res.ok, j: j }; }); })
      .then(function (r) {
        if (!r.ok || String(r.j.success) === "false") throw new Error(r.j.message || "Form error");
        form.reset();
        show(form, "ok", "Thanks! We got your request and will contact you shortly.");
        if (typeof window.gtag === "function") window.gtag("event", "generate_lead", { form: src });
      })
      .catch(function (err) {
        if (window.console) console.warn("[Quote form] FormSubmit said:", err && err.message);
        var p = phoneText();
        var s = show(form, "err", "Sorry, your request didn't go through." + (p ? " Please call us at " + p + "." : " Please call us."));
        var why = document.createElement("small");
        why.style.cssText = "display:block;margin-top:6px;opacity:.75;font-weight:400";
        why.textContent = "Reason: " + ((err && err.message) || "unknown");
        s.appendChild(why);
      })
      .then(function () {
        form.__fsBusy = false;
        if (btn) { btn.disabled = false; if (btn.tagName === "INPUT") btn.value = btnHTML; else btn.innerHTML = btnHTML; }
      });
  }, true);
})();
