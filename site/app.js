(function () {
  "use strict";
  var page = document.body.dataset.page;
  var DOW = ["월", "화", "수", "목", "금", "토", "일"];
  var LV = { "보통": 0, "붐빔": 1, "매우 붐빔": 2 };

  function get(path) {
    return fetch(path).then(function (r) { if (!r.ok) throw new Error(path); return r.json(); });
  }
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function pct(x) { return x === null || x === undefined ? "-" : Math.round(x * 100) + "%"; }
  function num(x) { return Math.round(x).toLocaleString("ko-KR"); }
  function lvClass(l) { return l === "매우 붐빔" ? "lv-매우" : "lv-" + l; }
  function ymd(d) {
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function hm(s) { return String(s).slice(11, 16); }

  function renderSources() {
    get("data/sources.json").then(function (s) {
      var f = document.getElementById("sources");
      f.appendChild(el("p", null, "데이터 출처"));
      var ul = el("ul");
      s.data.forEach(function (d) {
        var li = el("li"); var a = el("a", { href: d.url, rel: "noopener" }, d.name); li.appendChild(a); ul.appendChild(li);
      });
      f.appendChild(ul);
      f.appendChild(el("p", null, "이 서비스는 공공데이터 활용 경진대회 출품용 시제품이며, 예보는 실제와 다를 수 있습니다."));
    }).catch(function () {});
  }

  /* ---------- 수강생용 캘린더 ---------- */
  function citizen() {
    Promise.all([get("data/forecast.json"), get("data/courses.json"), get("data/overlaps.json")]).then(function (res) {
      var fc = res[0], courses = res[1], overlaps = res[2];
      var byDate = {};
      fc.blocks.forEach(function (b) { (byDate[b.date] = byDate[b.date] || []).push(b); });
      var start = new Date(fc.period.start + "T00:00:00"), end = new Date(fc.period.end + "T00:00:00");
      var cur = new Date(start.getFullYear(), start.getMonth(), 1);
      var mineDates = {}, selected = null;

      function drawMonth() {
        document.getElementById("month").textContent = cur.getFullYear() + "년 " + (cur.getMonth() + 1) + "월";
        document.getElementById("prev").disabled = cur <= new Date(start.getFullYear(), start.getMonth(), 1);
        document.getElementById("next").disabled = cur >= new Date(end.getFullYear(), end.getMonth(), 1);
        var cal = document.getElementById("cal"); cal.innerHTML = "";
        DOW.forEach(function (d) { cal.appendChild(el("div", { "class": "dow" }, d)); });
        var first = (cur.getDay() + 6) % 7;
        for (var i = 0; i < first; i++) cal.appendChild(el("div"));
        var days = new Date(cur.getFullYear(), cur.getMonth() + 1, 0).getDate();
        for (var d = 1; d <= days; d++) {
          var date = new Date(cur.getFullYear(), cur.getMonth(), d), key = ymd(date);
          var bl = byDate[key] || [];
          var btn = el("button", { type: "button", "class": "day" });
          if (!bl.length) { btn.disabled = true; btn.appendChild(el("span", { "class": "n" }, String(d))); cal.appendChild(btn); continue; }
          var top = bl.reduce(function (a, b) { return LV[b.level] > LV[a.level] ? b : a; });
          var fb = bl.filter(function (b) { return b.show_congestion; });
          var flagged = fb.length > 0;
          // 색은 공연 때문에 붐빌 때만 칠한다 (평일 낮처럼 원래 붐비는 시간은 상세 화면에서만 표시)
          if (flagged) btn.classList.add(lvClass(fb.reduce(function (a, b) { return LV[b.level] > LV[a.level] ? b : a; }).level));
          if (mineDates[key]) btn.classList.add("mine");
          if (selected === key) btn.classList.add("sel");
          btn.appendChild(el("span", { "class": "n" }, String(d)));
          if (flagged) btn.appendChild(el("span", { "class": "flag" }, "공연"));
          var t = fb.map(function (b) { return b.titles[0]; }).filter(Boolean)[0];
          if (t) btn.appendChild(el("span", { "class": "t" }, t));
          btn.setAttribute("aria-label", key + " " + top.level + (flagged ? ", 공연 혼잡 예상" : "") + (mineDates[key] ? ", 내 강좌와 겹침" : ""));
          btn.addEventListener("click", (function (k) { return function () { selected = k; drawMonth(); showDay(k); }; })(key));
          cal.appendChild(btn);
        }
      }

      function showDay(key) {
        var box = document.getElementById("detail"); box.innerHTML = "";
        box.appendChild(el("h2", null, key + " 예보"));
        var wrap = el("div", { "class": "blocks" });
        (byDate[key] || []).forEach(function (b) {
          var c = el("div", { "class": "block " + lvClass(b.level) });
          c.appendChild(el("h3", null, b.block + (b.block === "오후" ? " (12~16시)" : " (17~22시)")));
          c.appendChild(el("div", { "class": "lv" }, b.level + (b.show_congestion ? " · 공연 영향" : "")));
          var diff = b.pred_max - b.base_max;
          c.appendChild(el("div", null, "예상 최고 약 " + num(b.pred_max) + "대" + (diff > 0 ? " (평소보다 약 " + num(diff) + "대 많음)" : " (평소 수준)")));
          if (b.titles.length) c.appendChild(el("div", { "class": "note" }, "공연: " + b.titles.join(", ")));
          if (b.assumed_start) c.appendChild(el("div", { "class": "note" }, "시작 시각 미정(19시 가정)"));
          if (b.baseline_month_fallback) c.appendChild(el("div", { "class": "note" }, "이 달은 2025년 자료가 없어 가까운 달(" + b.baseline_month_fallback + "월)의 평소 패턴을 사용"));
          wrap.appendChild(c);
        });
        box.appendChild(wrap);
        var mine = overlaps.filter(function (o) { return o.date === key && o.course_no === myCourse; });
        if (mine.length) box.appendChild(el("p", null, "내 강좌(" + mine[0].name + ") " + hm(mine[0].start_dt) + " 수업이 이 시간대와 겹칩니다."));
      }

      var myCourse = null;
      var q = document.getElementById("q"), results = document.getElementById("results");
      q.addEventListener("input", function () {
        results.innerHTML = "";
        var term = q.value.trim(); if (term.length < 1) return;
        courses.filter(function (c) { return c.name.indexOf(term) >= 0; }).slice(0, 30).forEach(function (c) {
          var days = c.days.map(function (i) { return DOW[i]; }).join(",") + (c.optional_days.length ? ",(" + c.optional_days.map(function (i) { return DOW[i]; }).join(",") + ")" : "");
          var b = el("button", { type: "button" }, c.name + " · " + days + " " + c.start + "~" + c.end);
          b.addEventListener("click", function () { pick(c); });
          var li = el("li"); li.appendChild(b); results.appendChild(li);
        });
      });

      function pick(c) {
        myCourse = c.course_no; mineDates = {};
        var mine = overlaps.filter(function (o) { return o.course_no === c.course_no; });
        mine.forEach(function (o) { mineDates[o.date] = true; });
        results.innerHTML = ""; q.value = c.name;
        var box = document.getElementById("mine"); box.innerHTML = "";
        box.appendChild(el("p", null, mine.length ? "예보 기간 중 공연 혼잡과 겹치는 수업이 " + mine.length + "회 있습니다. 캘린더에 테두리로 표시했습니다." : "예보 기간 중 공연 혼잡과 겹치는 수업이 없습니다."));
        if (mine.some(function (o) { return o.optional; })) box.appendChild(el("p", null, "이 중 토요일(선택) 수업이 " + mine.filter(function (o) { return o.optional; }).length + "회입니다."));
        var a = el("a", { href: "data/ics/" + c.course_no + ".ics", download: c.course_no + ".ics" }, "휴대폰 캘린더에 추가 (.ics)");
        box.appendChild(a);
        drawMonth();
      }

      document.getElementById("prev").addEventListener("click", function () { cur = new Date(cur.getFullYear(), cur.getMonth() - 1, 1); drawMonth(); });
      document.getElementById("next").addEventListener("click", function () { cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1); drawMonth(); });
      drawMonth();
      var about = document.getElementById("about");
      about.textContent = "예보 기간 " + fc.period.start + " ~ " + fc.period.end + " · 생성 " + fc.generated_at.slice(0, 16).replace("T", " ") +
        " · '붐빔'은 2025년 시간대별 주차대수 상위 25%(" + num(fc.thresholds.p75) + "대 이상), '매우 붐빔'은 상위 10%(" + num(fc.thresholds.p90) + "대 이상)입니다. 동2·남2·북2 주차장 기준.";
    }).catch(function (e) { document.getElementById("cal").textContent = "데이터를 불러오지 못했습니다."; });
  }

  /* ---------- 기관용 ---------- */
  function agency() {
    Promise.all([get("data/overlaps.json"), get("data/forecast.json")]).then(function (res) {
      var ov = res[0].slice().sort(function (a, b) { return (a.start_dt < b.start_dt ? -1 : a.start_dt > b.start_dt ? 1 : (a.name < b.name ? -1 : 1)); }), fc = res[1];
      var from = document.getElementById("from"), to = document.getElementById("to"), reg = document.getElementById("regular");
      from.value = fc.period.start; to.value = fc.period.end; from.min = to.min = fc.period.start; from.max = to.max = fc.period.end;
      var shown = 50;
      var more = el("button", { type: "button", "class": "btn" }, "더 보기");
      document.getElementById("tbl").parentNode.after(more);
      more.addEventListener("click", function () { shown += 100; draw(true); });
      function draw(keep) {
        if (!keep) shown = 50;
        var rows = ov.filter(function (o) { return o.date >= from.value && o.date <= to.value && !(reg.checked && o.optional); });
        var tb = document.querySelector("#tbl tbody"); tb.innerHTML = "";
        more.hidden = rows.length <= shown;
        more.textContent = "더 보기 (" + Math.min(shown, rows.length) + " / " + rows.length + "회 표시 중)";
        rows.slice(0, shown).forEach(function (o) {
          var tr = el("tr");
          [o.date, hm(o.start_dt) + "~" + hm(o.end_dt), o.name + (o.optional ? " (토요일 선택)" : ""), num(o.capacity), o.block, o.level, "+" + num(o.excess) + "대", o.titles.join(", ")]
            .forEach(function (v, i) { tr.appendChild(el("td", (i === 3 || i === 6) ? { "class": "num" } : null, v)); });
          tb.appendChild(tr);
        });
        var cap = rows.reduce(function (s, o) { return s + o.capacity; }, 0);
        var courses = {}; rows.forEach(function (o) { courses[o.course_no] = 1; });
        var k = document.getElementById("kpis"); k.innerHTML = "";
        [["겹치는 회차", num(rows.length) + "회"], ["해당 강좌 수", num(Object.keys(courses).length) + "개"], ["정원 합계", num(cap) + "명"]].forEach(function (x) {
          var d = el("div", { "class": "kpi" }); d.appendChild(el("b", null, x[1])); d.appendChild(el("span", null, x[0])); k.appendChild(d);
        });
      }
      [from, to, reg].forEach(function (x) { x.addEventListener("change", function () { draw(false); }); });
      draw();
    });
  }

  /* ---------- 근거 ---------- */
  function evidence() {
    Promise.all([get("data/evidence_2025.json"), get("data/metrics.json"), get("data/sources.json")]).then(function (res) {
      var ev = res[0], m = res[1], src = res[2];
      var k = document.getElementById("ev-kpis");
      [["겹친 수업 회차", num(ev.n_sessions_overlapped) + "회"], ["그중 토요일 선택 수업", num(ev.n_sessions_overlapped_optional) + "회"],
       ["겹친 회차 정원 합계", num(ev.capacity_sum) + "명"], ["공연 혼잡 구간", num(ev.n_show_congestion_blocks) + " / " + num(ev.n_blocks)]].forEach(function (x) {
        var d = el("div", { "class": "kpi" }); d.appendChild(el("b", null, x[1])); d.appendChild(el("span", null, x[0])); k.appendChild(d);
      });
      document.getElementById("ev-note").textContent = "2025년 정상 기간(" + ev.months.join(", ") + "월) 올림픽수영장 강좌 " + num(ev.n_sessions_total) +
        "회 중, 실제 주차 기록상 공연 때문에 붐빈 오후·저녁 구간과 겹친 회차입니다. 정원 합계는 회차별 정원을 더한 값으로 실제 출석 인원과 다릅니다.";
      var mx = Math.max.apply(null, Object.values(ev.by_month));
      var box = document.getElementById("ev-month");
      Object.keys(ev.by_month).forEach(function (mo) {
        var row = el("div", { "class": "bar" }); row.appendChild(el("span", { style: "width:34px" }, mo + "월"));
        var bar = el("i"); bar.style.width = Math.max(2, 240 * ev.by_month[mo] / mx) + "px"; row.appendChild(bar);
        row.appendChild(el("span", null, num(ev.by_month[mo]) + "회")); box.appendChild(row);
      });
      var tb = document.querySelector("#ev-top tbody");
      ev.top_events.forEach(function (t) { var tr = el("tr"); tr.appendChild(el("td", null, t.title)); tr.appendChild(el("td", null, t.date)); tr.appendChild(el("td", { "class": "num" }, num(t.sessions))); tb.appendChild(tr); });
      var lt = document.querySelector("#loo tbody");
      if (m.blocks) Object.keys(m.blocks).forEach(function (blk) {
        [["analog", "과거 비슷한 공연일 참고"], ["baseline", "평소 패턴만"]].forEach(function (x) {
          var s = m.blocks[blk][x[0]], tr = el("tr");
          [blk, x[1], pct(s.acc), pct(s.recall), pct(s.show_days_recall), pct(s.precision), num(s.mae) + "대"].forEach(function (v, i) { tr.appendChild(el("td", i > 1 ? { "class": "num" } : null, v)); });
          lt.appendChild(tr);
        });
      });
      if (m.flag) document.getElementById("flag").textContent = "'공연 영향' 표시(붐빔 이상이면서 평소보다 200대 또는 25% 이상 많음)는 실제 해당 구간 " + m.flag.n_actual +
        "개 중 " + pct(m.flag.hit_rate) + "를 미리 표시했고, 표시한 " + m.flag.n_pred + "개 중 " + pct(m.flag.false_alarm_rate) + "는 실제로는 해당하지 않았습니다." +
        (m.weather ? " 비 오는 시간의 주차대수는 평소의 " + pct(m.weather.rain_ratio) + " 수준으로 차이가 작아 예보에는 날씨를 넣지 않았습니다." : "");
      var ul = document.getElementById("limits"); src.limits.forEach(function (l) { ul.appendChild(el("li", null, l)); });
    });
  }

  renderSources();
  if (page === "citizen") citizen();
  if (page === "agency") agency();
  if (page === "evidence") evidence();
})();
