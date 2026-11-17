(function () {
  "use strict";

  var page = document.body.dataset.page;
  var DOW = ["월", "화", "수", "목", "금", "토", "일"];
  var LV = { "보통": 0, "붐빔": 1, "매우 붐빔": 2 };
  var BLOCK_HOURS = { "오후": [12, 17], "저녁": [17, 23] }; // 끝 시각은 포함하지 않음
  var BLOCK_LABEL = { "오후": "오후 12~16시", "저녁": "저녁 17~22시" };
  var ICON = {
    download: '<path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19.5h14"/>',
    x: '<path d="M17 7 7 17M7 7l10 10"/>'
  };

  /* ---------- 공용 ---------- */
  function $(id) { return document.getElementById(id); }
  function get(path) {
    return fetch(path).then(function (r) { if (!r.ok) throw new Error(path); return r.json(); });
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function icon(name) {
    var s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("class", "ic"); s.setAttribute("aria-hidden", "true");
    s.innerHTML = ICON[name];
    return s;
  }
  function num(x) { return Math.round(x).toLocaleString("ko-KR"); }
  function about(x) { return num(Math.round(x / 10) * 10); }
  function pct(x) { return x === null || x === undefined ? "해당 없음" : Math.round(x * 100) + "%"; }
  function pad(n) { return String(n).padStart(2, "0"); }
  function ymd(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function parse(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function dowIdx(d) { return (d.getDay() + 6) % 7; } // 월=0
  function md(s) { var d = parse(s); return (d.getMonth() + 1) + "월 " + d.getDate() + "일"; }
  function mdw(s) { return md(s) + " (" + DOW[dowIdx(parse(s))] + ")"; }
  function longDate(s) { var d = parse(s); return d.getFullYear() + "년 " + md(s) + " " + DOW[dowIdx(d)] + "요일"; }
  function hm(s) { return String(s).slice(11, 16); }
  function lvn(level) { return LV[level] || 0; }
  function chip(level) { return el("span", "chip lv-" + lvn(level), level); }
  function shortTitle(t) { return String(t).replace(/^\s*\[[^\]]*\]\s*/, "").replace(/^(19|20)\d{2}\s+/, ""); }
  function minutes(t) { var p = t.split(":"); return +p[0] * 60 + +p[1]; }
  function fail(node, msg) { node.innerHTML = ""; node.appendChild(el("p", "err", msg)); }

  function footer() {
    get("data/sources.json").then(function (s) {
      var ul = $("src-list");
      s.data.forEach(function (d) {
        var li = el("li"), a = el("a", null, d.name);
        a.href = d.url; a.rel = "noopener"; li.appendChild(a); ul.appendChild(li);
      });
    }).catch(function () {});
    get("data/forecast.json").then(function (fc) {
      $("src-def").textContent = "붐빔은 2025년 시간대별 주차대수 상위 25% (" + num(fc.thresholds.p75) + "대 이상), 매우 붐빔은 상위 10% (" +
        num(fc.thresholds.p90) + "대 이상)입니다. 동2, 남2, 북2 주차장 기준입니다.";
      var p = $("period");
      if (p) p.textContent = "예보 기간 " + md(fc.period.start) + " ~ " + md(fc.period.end) + ", " + fc.generated_at.slice(5, 7).replace(/^0/, "") + "월 " +
        fc.generated_at.slice(8, 10).replace(/^0/, "") + "일 생성";
    }).catch(function () {});
  }

  function store(key, val) {
    try { if (val === null) localStorage.removeItem(key); else localStorage.setItem(key, val); } catch (e) { /* 저장 불가 환경 */ }
  }
  function recall(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }

  /* ---------- 수강생 캘린더 ---------- */
  function citizen() {
    Promise.all([get("data/forecast.json"), get("data/courses.json"), get("data/overlaps.json")]).then(function (res) {
      var fc = res[0], courses = res[1], overlaps = res[2];
      var byDate = {}, hol = {}, sched = {};
      fc.blocks.forEach(function (b) { (byDate[b.date] = byDate[b.date] || {})[b.block] = b; });
      (fc.holidays || []).forEach(function (h) { hol[h.date] = h.name; });
      (fc.schedule || []).forEach(function (s) { (sched[s.date] = sched[s.date] || []).push(s); });

      var start = parse(fc.period.start), end = parse(fc.period.end), today = ymd(new Date());
      var months = [];
      for (var m = new Date(start.getFullYear(), start.getMonth(), 1); m <= end; m = new Date(m.getFullYear(), m.getMonth() + 1, 1)) months.push(m);
      var flagged = fc.blocks.filter(function (b) { return b.show_congestion; })
        .sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : (a.block === "오후" ? -1 : 1); });

      var state = { month: 0, selected: null, course: null, mine: {}, lanes: [], upAll: false };

      /* 내 강좌가 걸치는 구간 */
      function lanesOf(c) {
        var s = minutes(c.start), e = minutes(c.end);
        return Object.keys(BLOCK_HOURS).filter(function (k) {
          var h = BLOCK_HOURS[k]; return s < h[1] * 60 && e > h[0] * 60;
        });
      }
      function meets(c, key) {
        if (hol[key]) return null;
        var i = dowIdx(parse(key));
        if (c.days.indexOf(i) >= 0) return "reg";
        if (c.optional_days.indexOf(i) >= 0) return "opt";
        return null;
      }
      function dayList(ds) {
        var run = ds.length >= 3 && ds.every(function (x, i) { return i === 0 || x === ds[i - 1] + 1; });
        return run ? DOW[ds[0]] + "~" + DOW[ds[ds.length - 1]] : ds.map(function (i) { return DOW[i]; }).join(", ");
      }
      function dayText(c) {
        var d = dayList(c.days);
        if (c.optional_days.length) d += ", " + dayList(c.optional_days) + "(선택)";
        return d;
      }

      /* 달 고르기 */
      var monthsBox = $("months");
      months.forEach(function (mo, i) {
        var b = el("button", null, (mo.getMonth() + 1) + "월");
        b.type = "button";
        b.setAttribute("aria-label", mo.getFullYear() + "년 " + (mo.getMonth() + 1) + "월");
        b.addEventListener("click", function () { state.month = i; drawMonth(); });
        monthsBox.appendChild(b);
      });

      function drawMonth() {
        var cur = months[state.month];
        $("month").textContent = cur.getFullYear() + "년 " + (cur.getMonth() + 1) + "월";
        Array.prototype.forEach.call(monthsBox.children, function (b, i) { b.setAttribute("aria-pressed", String(i === state.month)); });
        var cal = $("cal"); cal.innerHTML = "";
        DOW.forEach(function (d, i) {
          var h = el("div", "dow" + (i === 6 ? " sun" : ""), d); h.setAttribute("aria-hidden", "true"); cal.appendChild(h);
        });
        var first = dowIdx(cur);
        for (var i = 0; i < first; i++) cal.appendChild(el("div", "pad"));
        var days = new Date(cur.getFullYear(), cur.getMonth() + 1, 0).getDate();
        for (var d = 1; d <= days; d++) cal.appendChild(tile(new Date(cur.getFullYear(), cur.getMonth(), d)));
        var tail = (first + days) % 7;
        if (tail) for (var j = tail; j < 7; j++) cal.appendChild(el("div", "pad"));
      }

      function tile(date) {
        var key = ymd(date), bl = byDate[key];
        var b = el("button", "day");
        b.type = "button";
        if (dowIdx(date) === 6) b.classList.add("sun");
        if (hol[key]) b.classList.add("hol");
        if (key === today) b.classList.add("today");
        var n = el("span", "n"); var nb = el("b", null, String(date.getDate())); n.appendChild(nb); b.appendChild(n);
        if (!bl) {
          b.classList.add("off"); b.disabled = true;
          b.setAttribute("aria-label", longDate(key) + ", 예보 기간 밖");
          return b;
        }
        var lanes = el("span", "lanes"), said = [], meet = state.course ? meets(state.course, key) : null;
        ["오후", "저녁"].forEach(function (k) {
          var x = bl[k], lane = el("span", "lane");
          if (x && x.show_congestion) { lane.classList.add("lv-" + lvn(x.level)); said.push(k + " 공연으로 " + x.level); }
          if (meet && state.lanes.indexOf(k) >= 0) { lane.classList.add("my"); if (meet === "opt") lane.classList.add("opt"); }
          lanes.appendChild(lane);
        });
        b.appendChild(lanes);
        var mine = state.mine[key];
        var title = ["오후", "저녁"].map(function (k) { return bl[k] && bl[k].show_congestion ? bl[k].titles[0] : null; }).filter(Boolean)[0];
        if (mine) b.appendChild(el("span", "t me", "내 수업 " + hm(mine.start_dt)));
        else if (title) { var tt = el("span", "t", shortTitle(title)); tt.title = title; b.appendChild(tt); }
        else if (hol[key]) b.appendChild(el("span", "t hn", hol[key]));
        if (state.selected === key) { b.classList.add("sel"); b.setAttribute("aria-pressed", "true"); } else b.setAttribute("aria-pressed", "false");
        b.setAttribute("aria-label", longDate(key) + (hol[key] ? " " + hol[key] : "") + ", " + (said.length ? said.join(", ") : "공연 혼잡 없음") +
          (mine ? ", 내 수업 " + hm(mine.start_dt) + " 겹침" : meet ? ", 내 수업 있음" : ""));
        b.addEventListener("click", function () { select(key, "tile"); });
        return b;
      }

      /* how: "tile" 달력 칸을 누름, "jump" 목록에서 고름, "init" 처음 열림 */
      function select(key, how) {
        state.selected = key;
        var d = parse(key);
        months.forEach(function (mo, i) { if (mo.getFullYear() === d.getFullYear() && mo.getMonth() === d.getMonth()) state.month = i; });
        drawMonth(); showDay(key);
        var narrow = window.matchMedia("(max-width: 1023px)").matches;
        if (how === "tile") {
          var t0 = document.querySelector(".day.sel"); if (t0) t0.focus({ preventScroll: true });
          if (narrow) $("detail").scrollIntoView({ block: "nearest", behavior: "smooth" });
        } else if (how === "jump") {
          var t1 = document.querySelector(".day.sel"); if (t1) t1.focus({ preventScroll: true });
          if (narrow) $("cal").scrollIntoView({ block: "nearest", behavior: "smooth" });
        }
      }

      function showDay(key) {
        var box = $("detail"), bl = byDate[key] || {};
        box.innerHTML = "";
        box.appendChild(el("h2", null, longDate(key)));
        var sub = [];
        if (hol[key]) sub.push(hol[key] + ", 수영장 강좌 쉬는 날");
        var any = ["오후", "저녁"].some(function (k) { return bl[k] && bl[k].show_congestion; });
        sub.push(any ? "공연 때문에 평소보다 붐빌 것으로 보입니다." : "공연으로 인한 혼잡은 예상되지 않습니다.");
        box.appendChild(el("p", "sub", sub.join(" ")));
        var slots = el("div", "slots");
        ["오후", "저녁"].forEach(function (k) {
          var b = bl[k]; if (!b) return;
          var s = el("div", "slot"), ln = el("span", "ln" + (b.show_congestion ? " lv-" + lvn(b.level) : ""));
          ln.setAttribute("aria-hidden", "true"); s.appendChild(ln);
          var hd = el("div", "hd");
          hd.appendChild(el("strong", null, k)); hd.appendChild(el("span", "hr", k === "오후" ? "12~16시" : "17~22시")); hd.appendChild(chip(b.level));
          if (b.show_congestion) hd.appendChild(el("span", "tag", "공연 영향"));
          s.appendChild(hd);
          var diff = b.pred_max - b.base_max;
          s.appendChild(el("p", "fig", "가장 붐빌 때 약 " + about(b.pred_max) + "대" + (diff >= 50 ? ", 평소보다 약 " + about(diff) + "대 많음" : ", 평소 수준")));
          if (b.show_congestion && b.titles.length) {
            var ul = el("ul", "shows");
            b.titles.forEach(function (t) {
              var li = el("li", null, t), info = (sched[key] || []).filter(function (x) { return x.title === t; })[0];
              if (info) li.appendChild(el("span", null, " (" + info.venue + ", " + (info.start_time_assumed ? "시작 시각 미정" : info.start_time + " 시작") + ")"));
              ul.appendChild(li);
            });
            s.appendChild(ul);
          } else if (b.titles.length) {
            s.appendChild(el("p", "quiet", "이 시간에 영향을 줄 수 있는 공연이 있지만, 평소와 큰 차이는 없을 것으로 보입니다."));
          } else if (b.level !== "보통") {
            s.appendChild(el("p", "quiet", "공연과 관계없이 이 시간대는 평소에도 붐비는 편입니다."));
          }
          slots.appendChild(s);
        });
        box.appendChild(slots);
        if (state.course) {
          var c = state.course, mine = state.mine[key], meet = meets(c, key);
          var msg = mine ? c.name + " " + hm(mine.start_dt) + "~" + hm(mine.end_dt) + " 수업이 " + mine.block + " 혼잡과 겹칩니다. 평소보다 일찍 출발하거나 대중교통을 이용하세요."
            : meet ? c.name + " 수업이 있지만 공연 혼잡과는 겹치지 않습니다." : c.name + " 수업이 없는 날입니다.";
          box.appendChild(el("p", "me", msg));
        }
        var notes = [];
        var fb = ["오후", "저녁"].map(function (k) { return bl[k] && bl[k].baseline_month_fallback; }).filter(Boolean)[0];
        if (fb) notes.push("이 달은 2025년 자료가 없어 " + Math.round(fb) + "월의 평소 패턴을 썼습니다.");
        if (["오후", "저녁"].some(function (k) { return bl[k] && bl[k].assumed_start; })) notes.push("시작 시각이 정해지지 않은 공연은 19시 시작으로 보고 계산했습니다.");
        if (notes.length) box.appendChild(el("p", "fine", notes.join(" ")));
      }

      /* 다가오는 공연 혼잡: 날짜별 한 줄 */
      var upDays = [];
      flagged.forEach(function (b) {
        var last = upDays[upDays.length - 1];
        if (!last || last.date !== b.date) upDays.push(last = { date: b.date, blocks: [] });
        last.blocks.push(b);
      });
      function drawUpcoming() {
        var ul = $("uplist"); ul.innerHTML = "";
        var list = state.upAll ? upDays : upDays.slice(0, 8);
        $("up-count").textContent = upDays.length + "일";
        if (!upDays.length) { ul.appendChild(el("li", "hint", "예보 기간에 공연으로 붐빌 시간이 없습니다.")); return; }
        list.forEach(function (g) {
          var li = el("li"), bt = el("button"), titles = [];
          bt.type = "button";
          var d = el("span", "d", md(g.date)); d.appendChild(el("span", null, DOW[dowIdx(parse(g.date))])); bt.appendChild(d);
          var lv = el("span", "lv"), said = [];
          g.blocks.forEach(function (b) {
            lv.appendChild(el("span", "chip lv-" + lvn(b.level), b.block + " " + b.level));
            said.push(b.block + " " + b.level);
            b.titles.forEach(function (x) { if (titles.indexOf(x) < 0) titles.push(x); });
          });
          var mine = state.mine[g.date];
          if (mine) lv.appendChild(el("span", "tag pool", "내 수업 " + hm(mine.start_dt)));
          bt.appendChild(lv);
          bt.appendChild(el("span", "ti", titles.join(", ")));
          bt.setAttribute("aria-label", mdw(g.date) + ", " + said.join(", ") + (mine ? ", 내 수업 겹침" : "") + ", " + titles.join(", "));
          bt.addEventListener("click", function () { select(g.date, "jump"); });
          li.appendChild(bt); ul.appendChild(li);
        });
        var more = $("upmore");
        more.hidden = upDays.length <= 8;
        more.textContent = state.upAll ? "처음 8일만 보기" : "모두 보기 (" + upDays.length + "일)";
      }
      $("upmore").addEventListener("click", function () { state.upAll = !state.upAll; drawUpcoming(); });

      /* 강좌 검색 (콤보박스) */
      var q = $("q"), results = $("results"), clear = $("clear"), active = -1, shown = [];
      function closeList() { results.hidden = true; q.setAttribute("aria-expanded", "false"); q.removeAttribute("aria-activedescendant"); active = -1; }
      function setActive(i) {
        var items = results.querySelectorAll("[role=option]");
        if (!items.length) return;
        active = (i + items.length) % items.length;
        Array.prototype.forEach.call(items, function (it, j) { it.setAttribute("aria-selected", String(j === active)); });
        q.setAttribute("aria-activedescendant", items[active].id);
        items[active].scrollIntoView({ block: "nearest" });
      }
      function highlight(name, term) {
        var frag = document.createDocumentFragment(), i = name.indexOf(term);
        if (i < 0 || !term) { frag.appendChild(document.createTextNode(name)); return frag; }
        frag.appendChild(document.createTextNode(name.slice(0, i)));
        frag.appendChild(el("mark", null, name.slice(i, i + term.length)));
        frag.appendChild(document.createTextNode(name.slice(i + term.length)));
        return frag;
      }
      function search() {
        var term = q.value.trim();
        clear.hidden = !q.value;
        results.innerHTML = ""; active = -1;
        if (!term) { closeList(); return; }
        var words = term.split(/\s+/);
        shown = courses.filter(function (c) { return words.every(function (w) { return c.name.indexOf(w) >= 0; }); })
          .sort(function (a, b) { return a.start < b.start ? -1 : a.start > b.start ? 1 : a.name < b.name ? -1 : 1; }).slice(0, 40);
        if (!shown.length) {
          var none = el("li", "none", "'" + term + "'이(가) 들어간 강좌가 없습니다. 강좌명 일부만 입력해 보세요.");
          none.setAttribute("role", "option"); none.setAttribute("aria-disabled", "true"); none.id = "opt-none";
          results.appendChild(none);
        }
        shown.forEach(function (c, i) {
          var li = el("li"); li.id = "opt-" + i; li.setAttribute("role", "option"); li.setAttribute("aria-selected", "false");
          var nm = el("span", "nm"); nm.appendChild(highlight(c.name, words[0])); li.appendChild(nm);
          li.appendChild(el("span", "mt", dayText(c) + ", " + c.start + "~" + c.end + ", " + c.group + ", 강좌번호 " + c.course_no));
          li.addEventListener("mousedown", function (e) { e.preventDefault(); });
          li.addEventListener("click", function () { pick(c, "user"); });
          results.appendChild(li);
        });
        results.hidden = false; q.setAttribute("aria-expanded", "true");
      }
      q.addEventListener("input", search);
      q.addEventListener("focus", function () { if (q.value.trim() && !state.course) search(); });
      q.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown") { e.preventDefault(); if (results.hidden) search(); setActive(active + 1); }
        else if (e.key === "ArrowUp") { e.preventDefault(); setActive(active - 1); }
        else if (e.key === "Enter") { if (active >= 0 && shown[active]) { e.preventDefault(); pick(shown[active], "user"); } }
        else if (e.key === "Escape") { closeList(); }
      });
      q.addEventListener("blur", function () { setTimeout(closeList, 120); });
      clear.addEventListener("click", function () { unpick(); q.value = ""; clear.hidden = true; closeList(); q.focus(); });

      function pick(c, how) {
        state.course = c; state.lanes = lanesOf(c); state.mine = {};
        overlaps.forEach(function (o) { if (o.course_no === c.course_no && !state.mine[o.date]) state.mine[o.date] = o; });
        q.value = c.name; clear.hidden = false; closeList();
        store("olpark.course", c.course_no);
        try { var u = new URL(location.href); u.searchParams.set("course", c.course_no); history.replaceState(null, "", u); } catch (e) { /* 무시 */ }
        drawMine();
        var keys = Object.keys(state.mine).sort();
        if (keys.length) select(keys[0], how === "init" ? "init" : "none"); else { drawMonth(); if (state.selected) showDay(state.selected); }
        drawUpcoming();
      }
      function unpick() {
        state.course = null; state.lanes = []; state.mine = {};
        store("olpark.course", null);
        try { var u = new URL(location.href); u.searchParams.delete("course"); history.replaceState(null, "", u); } catch (e) { /* 무시 */ }
        $("mine").hidden = true; $("mine-hint").hidden = false;
        drawMonth(); if (state.selected) showDay(state.selected); drawUpcoming();
      }

      function drawMine() {
        var c = state.course, box = $("mine"); box.innerHTML = ""; box.hidden = false; $("mine-hint").hidden = true;
        box.appendChild(el("h3", null, c.name));
        box.appendChild(el("p", "sched", dayText(c) + ", " + c.start + "~" + c.end + ", " + c.group + ", 정원 " + c.capacity + "명, 강좌번호 " + c.course_no));
        var keys = Object.keys(state.mine).sort(), opt = keys.filter(function (k) { return state.mine[k].optional; }).length;
        var v = el("p", "verdict");
        if (!state.lanes.length) {
          v.textContent = "이 강좌는 예보 구간(12~22시) 밖의 수업이라 공연 혼잡과 겹치지 않습니다.";
        } else if (!keys.length) {
          v.textContent = "예보 기간에는 공연 혼잡과 겹치는 수업이 없습니다.";
        } else {
          v.appendChild(document.createTextNode("예보 기간에 공연 혼잡과 겹치는 수업 "));
          v.appendChild(el("b", "tnum", keys.length + "회"));
          if (opt) v.appendChild(document.createTextNode(" (토요일 선택 수업 " + opt + "회 포함)"));
        }
        box.appendChild(v);
        if (state.lanes.length) {
          var lk = el("span", "lanekey"); var sw = el("i"); sw.setAttribute("aria-hidden", "true"); lk.appendChild(sw);
          lk.appendChild(document.createTextNode("달력에서 " + state.lanes.join(", ") + " 줄에 파란 테두리로 표시"));
          box.appendChild(lk);
        }
        if (keys.length) {
          var ul = el("ul", "hits"); ul.setAttribute("aria-label", "겹치는 날");
          keys.forEach(function (k) {
            var o = state.mine[k], li = el("li"), bt = el("button");
            bt.type = "button";
            var bar = el("i", "lv-" + lvn(o.level)); bar.setAttribute("aria-hidden", "true"); bt.appendChild(bar);
            bt.appendChild(document.createTextNode(mdw(k)));
            bt.setAttribute("aria-label", mdw(k) + " " + o.block + " " + o.level + ", 날짜 상세 보기");
            bt.addEventListener("click", function () { select(k, "jump"); });
            li.appendChild(bt); ul.appendChild(li);
          });
          box.appendChild(ul);
        }
        var act = el("div", "actions");
        if (keys.length) {
          var a = el("a", "btn primary");
          a.href = "data/ics/" + c.course_no + ".ics"; a.setAttribute("download", c.course_no + ".ics");
          a.appendChild(icon("download")); a.appendChild(document.createTextNode("겹치는 날을 휴대폰 캘린더에 추가"));
          act.appendChild(a);
        }
        var other = el("button", "btn quiet", "다른 강좌 고르기"); other.type = "button";
        other.addEventListener("click", function () { unpick(); q.value = ""; clear.hidden = true; q.focus(); });
        act.appendChild(other);
        box.appendChild(act);
      }

      /* 시작 */
      drawUpcoming();
      var wanted = null;
      try { wanted = new URL(location.href).searchParams.get("course"); } catch (e) { /* 무시 */ }
      wanted = wanted || recall("olpark.course");
      var found = courses.filter(function (c) { return c.course_no === wanted; })[0];
      if (found) pick(found, "init");
      else if (flagged.length) select(flagged[0].date, "init");
      else { drawMonth(); showDay(fc.period.start); }
    }).catch(function () {
      fail($("cal"), "예보 데이터를 불러오지 못했습니다. 잠시 뒤 새로고침해 주세요.");
      $("detail").innerHTML = "";
    });
  }

  /* ---------- 기관 겹침 목록 ---------- */
  function agency() {
    Promise.all([get("data/overlaps.json"), get("data/forecast.json")]).then(function (res) {
      var ov = res[0].slice().sort(function (a, b) { return a.start_dt < b.start_dt ? -1 : a.start_dt > b.start_dt ? 1 : (a.name < b.name ? -1 : 1); });
      var fc = res[1], from = $("from"), to = $("to"), reg = $("regular"), more = $("more"), limit = 50;
      from.value = fc.period.start; to.value = fc.period.end;
      from.min = to.min = fc.period.start; from.max = to.max = fc.period.end;

      function rows() {
        var a = from.value || fc.period.start, b = to.value || fc.period.end;
        if (a > b) { var t = a; a = b; b = t; }
        return ov.filter(function (o) { return o.date >= a && o.date <= b && !(reg.checked && o.optional); });
      }
      function draw(reset) {
        if (reset) limit = 50;
        var rs = rows(), table = $("tbl");
        Array.prototype.slice.call(table.tBodies).forEach(function (b) { b.remove(); });
        if (!rs.length) {
          var tb0 = el("tbody"), tr0 = el("tr"), td0 = el("td", "empty", "선택한 기간에 공연 혼잡과 겹치는 수업이 없습니다. 기간을 넓혀 보세요.");
          td0.colSpan = 4; tr0.appendChild(td0); tb0.appendChild(tr0); table.appendChild(tb0);
        }
        var key = null, tb = null;
        rs.slice(0, limit).forEach(function (o) {
          if (o.date + o.block !== key) {
            key = o.date + o.block; tb = el("tbody");
            var gr = el("tr", "grp"), th = el("th");
            th.colSpan = 4; th.scope = "colgroup";
            var top = el("div", "g1");
            top.appendChild(el("strong", null, mdw(o.date)));
            top.appendChild(el("span", "blk", BLOCK_LABEL[o.block] || o.block));
            top.appendChild(chip(o.level));
            top.appendChild(el("span", "ex", "평소보다 약 " + about(o.excess) + "대 많음"));
            th.appendChild(top);
            th.appendChild(el("div", "g2", o.titles.join(", ")));
            gr.appendChild(th); tb.appendChild(gr); table.appendChild(tb);
          }
          var tr = el("tr");
          tr.appendChild(el("td", "time", hm(o.start_dt) + "~" + hm(o.end_dt)));
          var nm = el("td", null, o.name);
          if (o.optional) { nm.appendChild(document.createTextNode(" ")); nm.appendChild(el("span", "tag m-only", "토요일 선택")); }
          tr.appendChild(nm);
          tr.appendChild(el("td", "num", num(o.capacity) + "명"));
          var nt = el("td"); if (o.optional) nt.appendChild(el("span", "tag", "토요일 선택")); tr.appendChild(nt);
          tb.appendChild(tr);
        });
        var cap = rs.reduce(function (s, o) { return s + o.capacity; }, 0), cs = {};
        rs.forEach(function (o) { cs[o.course_no] = 1; });
        var sm = $("summary"); sm.innerHTML = "";
        [["선택한 기간에 겹치는 수업 ", num(rs.length) + "회"], [", 해당 강좌 ", num(Object.keys(cs).length) + "개"], [", 정원 합계 ", num(cap) + "명"]].forEach(function (x) {
          sm.appendChild(document.createTextNode(x[0])); sm.appendChild(el("b", null, x[1]));
        });
        sm.appendChild(document.createTextNode(". 정원 합계는 회차별 정원을 더한 값으로 실제 출석 인원과 다릅니다."));
        $("shown").textContent = rs.length ? num(Math.min(limit, rs.length)) + " / " + num(rs.length) + "회 표시 중" : "";
        more.hidden = rs.length <= limit;
        more.textContent = Math.min(50, rs.length - limit) + "회 더 보기";
      }
      more.addEventListener("click", function () { limit += 50; draw(false); });
      [from, to, reg].forEach(function (x) { x.addEventListener("change", function () { draw(true); }); });
      draw(true);
    }).catch(function () {
      var tb = document.querySelector("#tbl tbody"); tb.innerHTML = "";
      var tr = el("tr"), td = el("td", null, ""); td.colSpan = 4; td.appendChild(el("p", "err", "목록을 불러오지 못했습니다. 잠시 뒤 새로고침해 주세요."));
      tr.appendChild(td); tb.appendChild(tr);
    });
  }

  /* ---------- 근거와 검증 ---------- */
  function tooltip(host) {
    var tip = el("div", "tip"); tip.hidden = true; tip.setAttribute("role", "presentation"); host.appendChild(tip);
    return {
      show: function (node, value, label) {
        tip.innerHTML = ""; tip.appendChild(el("b", null, value)); tip.appendChild(el("span", null, label)); tip.hidden = false;
        var h = host.getBoundingClientRect(), r = node.getBoundingClientRect();
        var x = Math.min(Math.max(8, r.right - h.left + 8), h.width - tip.offsetWidth - 8);
        tip.style.left = x + "px"; tip.style.top = (r.top - h.top + r.height / 2 - tip.offsetHeight / 2) + "px";
      },
      hide: function () { tip.hidden = true; }
    };
  }

  function evidence() {
    Promise.all([get("data/evidence_2025.json"), get("data/metrics.json"), get("data/sources.json")]).then(function (res) {
      var ev = res[0], m = res[1], src = res[2];
      var share = ev.n_sessions_total ? ev.n_sessions_overlapped / ev.n_sessions_total : 0;
      var lead = $("ev-lead"); lead.innerHTML = "";
      [["2025년 정상 기간(" + ev.months.join(", ") + "월) 올림픽수영장 수업 ", null], [num(ev.n_sessions_total) + "회", 1], [" 가운데 ", null],
       [num(ev.n_sessions_overlapped) + "회(" + (share * 100).toFixed(1) + "%)", 1], ["가 실제 주차 기록상 공연 때문에 붐빈 오후나 저녁과 겹쳤습니다. 그중 ", null],
       [num(ev.n_sessions_overlapped_optional) + "회", 1], ["는 토요일 선택 수업입니다. 겹친 회차의 정원을 모두 더하면 ", null], [num(ev.capacity_sum) + "명", 1],
       ["으로, 실제 출석 인원과는 다릅니다.", null]].forEach(function (x) {
        lead.appendChild(x[1] ? el("b", null, x[0]) : document.createTextNode(x[0]));
      });

      /* 달별 막대: 한 계열, 값은 막대 끝에 */
      var host = $("ev-month"), tip = tooltip(host), bars = el("div", "bars"), mx = 0, total = 0;
      Object.keys(ev.by_month).forEach(function (k) { mx = Math.max(mx, ev.by_month[k]); total += ev.by_month[k]; });
      Object.keys(ev.by_month).sort(function (a, b) { return a - b; }).forEach(function (k) {
        var v = ev.by_month[k], row = el("div", "row");
        row.tabIndex = 0; row.setAttribute("role", "img");
        row.setAttribute("aria-label", k + "월 " + num(v) + "회, 전체의 " + Math.round(v / total * 100) + "%");
        row.appendChild(el("span", "k", k + "월"));
        var tr = el("span", "track"), bar = el("span", "bar");
        bar.style.width = "calc((100% - 56px) * " + (v / mx).toFixed(4) + ")";
        tr.appendChild(bar); tr.appendChild(el("span", "v", num(v) + "회")); row.appendChild(tr);
        function on() { tip.show(bar, num(v) + "회", k + "월, 겹친 수업 전체의 " + Math.round(v / total * 100) + "%"); }
        row.addEventListener("pointerenter", on); row.addEventListener("focus", on);
        row.addEventListener("pointerleave", tip.hide); row.addEventListener("blur", tip.hide);
        bars.appendChild(row);
      });
      host.appendChild(bars);

      var tb = document.querySelector("#ev-top tbody");
      ev.top_events.forEach(function (t) {
        var tr = el("tr"); tr.appendChild(el("td", null, t.title)); tr.appendChild(el("td", "time", mdw(t.date)));
        tr.appendChild(el("td", "num", num(t.sessions) + "회")); tb.appendChild(tr);
      });

      /* 검증: 평소 패턴에서 이 서비스 방식으로의 변화 (덤벨) */
      if (m.blocks) {
        var chart = $("loo-chart"), tip2 = tooltip(chart), dumb = el("div", "dumb");
        var METRICS = [["acc", "맞힌 비율"], ["recall", "붐빈 날 잡아낸 비율"], ["show_days_recall", "공연일 붐빔 잡아낸 비율"]];
        Object.keys(m.blocks).forEach(function (blk) {
          dumb.appendChild(el("p", "grp", BLOCK_LABEL[blk] || blk));
          METRICS.forEach(function (mt) {
            var a = m.blocks[blk].analog[mt[0]] || 0, b = m.blocks[blk].baseline[mt[0]] || 0;
            var row = el("div", "row"); row.tabIndex = 0; row.setAttribute("role", "img");
            row.setAttribute("aria-label", blk + " " + mt[1] + ": 평소 패턴만 " + pct(b) + ", 이 서비스 " + pct(a));
            row.appendChild(el("span", "k", mt[1]));
            var plot = el("span", "plot"), lo = Math.min(a, b), hi = Math.max(a, b);
            var seg = el("span", "seg"); seg.style.left = (lo * 100) + "%"; seg.style.width = ((hi - lo) * 100) + "%"; plot.appendChild(seg);
            var d1 = el("span", "dot base"); d1.style.left = (b * 100) + "%"; plot.appendChild(d1);
            var d2 = el("span", "dot ours"); d2.style.left = (a * 100) + "%"; plot.appendChild(d2);
            row.appendChild(plot);
            var v = el("span", "v"); v.appendChild(el("b", null, pct(a))); v.appendChild(document.createTextNode(" (평소 " + pct(b) + ")")); row.appendChild(v);
            function on() { tip2.show(d2, pct(a), "이 서비스, 평소 패턴만 " + pct(b)); }
            row.addEventListener("pointerenter", on); row.addEventListener("focus", on);
            row.addEventListener("pointerleave", tip2.hide); row.addEventListener("blur", tip2.hide);
            dumb.appendChild(row);
          });
        });
        var sc = el("div", "scale"); sc.setAttribute("aria-hidden", "true"); sc.appendChild(el("span"));
        var ticks = el("div"); ["0%", "50%", "100%"].forEach(function (t) { ticks.appendChild(el("span", null, t)); }); sc.appendChild(ticks); sc.appendChild(el("span"));
        dumb.appendChild(sc);
        chart.insertBefore(dumb, chart.firstChild);

        var lt = document.querySelector("#loo tbody");
        Object.keys(m.blocks).forEach(function (blk) {
          [["analog", "과거 비슷한 공연일 참고"], ["baseline", "평소 패턴만"]].forEach(function (x) {
            var s = m.blocks[blk][x[0]], tr = el("tr");
            [blk, x[1], pct(s.acc), pct(s.recall), pct(s.show_days_recall), pct(s.precision), num(s.mae) + "대"].forEach(function (val, i) {
              tr.appendChild(el("td", i > 1 ? "num" : null, val));
            });
            lt.appendChild(tr);
          });
        });
      }
      if (m.flag) $("flag").textContent = "달력의 공연 영향 표시(붐빔 이상이면서 평소보다 200대 또는 25% 이상 많음)는 실제 해당 구간 " + m.flag.n_actual +
        "개 가운데 " + pct(m.flag.hit_rate) + "를 미리 표시했고, 표시한 " + m.flag.n_pred + "개 가운데 " + pct(m.flag.false_alarm_rate) + "는 실제로는 해당하지 않았습니다." +
        (m.weather ? " 비 오는 시간의 주차대수는 평소의 " + pct(m.weather.rain_ratio) + " 수준으로 차이가 작아 예보에 날씨는 넣지 않았습니다." : "");
      var ul = $("limits"); src.limits.forEach(function (l) { ul.appendChild(el("li", null, l)); });
    }).catch(function () { fail($("ev-lead"), "근거 데이터를 불러오지 못했습니다. 잠시 뒤 새로고침해 주세요."); });
  }

  footer();
  if (page === "citizen") citizen();
  if (page === "agency") agency();
  if (page === "evidence") evidence();
})();
