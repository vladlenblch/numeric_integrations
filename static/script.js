function $(selector) {
  return document.querySelector(selector);
}

function printIntegralResult(target, data) {
  const prefix = "&gt; ";

  if (!data.ok) {
    const lines = [`${prefix}ошибка: <span class="error">${data.error}</span>`];
    while (lines.length < 5) lines.push(prefix);
    target.innerHTML = lines.join("\n");
    return;
  }

  const lines = [];
  lines.push(`${prefix}значение ≈ <span class="accent">${data.result}</span>`);
  if (data.n) {
    lines.push(`${prefix}разбиений n = ${data.n}`);
  }
  if (data.runge_error !== null) {
    lines.push(`${prefix}оценка погрешности по Рунге ≈ ${data.runge_error}`);
  } else {
    lines.push(`${prefix}оценка погрешности: точность не достигнута (превышено число разбиений)`);
  }
  if (data.exact_value !== null) {
    lines.push(`${prefix}точное значение = ${data.exact_value}`);
  }
  if (data.exact_error !== null) {
    lines.push(`${prefix}|погрешность| = ${data.exact_error}`);
  }
  while (lines.length < 5) lines.push(prefix);
  if (lines.length > 5) lines.length = 5;
  target.innerHTML = lines.join("\n");
}

function printImproperResult(target, data) {
  const prefix = "> ";

  if (!data.ok) {
    const lines = [`${prefix}ошибка: <span class="error">${data.error}</span>`];
    while (lines.length < 2) lines.push(prefix);
    target.innerHTML = lines.join("\n");
    return;
  }

  if (!data.exists) {
    const lines = [
      `${prefix}сходимость: <span class="error">интеграл не существует (расходится)</span>`,
      prefix,
    ];
    target.innerHTML = lines.join("\n");
    return;
  }

  const lines = [];
  lines.push(`${prefix}сходимость: интеграл существует (сходится)`);
  lines.push(`${prefix}значение ≈ <span class="accent">${data.value}</span>`);
  target.innerHTML = lines.join("\n");
}

window.addEventListener("DOMContentLoaded", () => {
  const fnSelect = $("#function_key");
  const aInput = $("#a");
  const bInput = $("#b");
  const epsInput = $("#eps");
  const integralOutput = $("#integral-output");
  const improperOutput = $("#improper-output");
  const improperAInput = $("#improper_a");
  const improperBInput = $("#improper_b");

  function applyDefaults() {
    const opt = fnSelect.options[fnSelect.selectedIndex];
    aInput.value = opt.getAttribute("data-a");
    bInput.value = opt.getAttribute("data-b");
  }

  applyDefaults();

  fnSelect.addEventListener("change", applyDefaults);

  function applyDefaultsImproper() {
    const opt = $("#improper_key").options[$("#improper_key").selectedIndex];
    if (!opt) return;
    improperAInput.value = opt.getAttribute("data-a");
    improperBInput.value = opt.getAttribute("data-b");
  }

  applyDefaultsImproper();

  $("#improper_key").addEventListener("change", applyDefaultsImproper);

  $("#integral-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      function_key: fnSelect.value,
      method_key: $("#method_key").value,
      a: aInput.value,
      b: bInput.value,
      eps: epsInput.value,
    };

    try {
      const res = await fetch("/api/integrate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      printIntegralResult(integralOutput, data);
    } catch (err) {
      printIntegralResult(integralOutput, {
        ok: false,
        error: `ошибка сети: ${err}`,
      });
    }
  });

  $("#improper-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      key: $("#improper_key").value,
      method_key: $("#improper_method_key").value,
      eps: $("#improper_eps").value,
      a: improperAInput.value,
      b: improperBInput.value,
    };

    try {
      const res = await fetch("/api/improper", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      printImproperResult(improperOutput, data);
    } catch (err) {
      printImproperResult(improperOutput, {
        ok: false,
        error: `ошибка сети: ${err}`,
      });
    }
  });
});
