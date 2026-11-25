// The recommender's port against the course's answers (19 Nov 2026): runs boing-backend/recs-core.js on each of ECSE557/testcases/
// (13 cases made by notebook 11 with the final design) and compares every row with expected.csv, as testcases/README.md says a port
// passes: the same groups in the same order, the same reason code, every score within 1e-6, the same reason text character for
// character. No server, no database: node tests/recs/port.js   (CASES=<folder> to point elsewhere, ONLY=01 to run one case)
const fs = require('fs'), path = require('path'), os = require('os');
const ROOT = path.join(__dirname, '..');
const CASES = process.env.CASES || path.join(ROOT, 'testcases');

/* recs-core.js is an ES module with no imports: a copy as .mjs loads in node */
async function core() {
  const tmp = path.join(os.tmpdir(), 'recs-core-' + process.pid + '.mjs');
  fs.copyFileSync(path.join(__dirname, 'recs-core.js'), tmp);
  const m = await import('file://' + tmp.replace(/\\/g, '/'));
  fs.unlinkSync(tmp);
  return m;
}
function csv(file) {
  if (!fs.existsSync(file)) return [];
  const text = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n'), rows = [];
  let row = [], f = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(f); f = ''; }
    else if (ch === '\n') { row.push(f); rows.push(row); row = []; f = ''; }
    else f += ch;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  const [head, ...body] = rows.filter(r => r.length > 1 || r[0] !== '');
  return body.map(r => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

async function runCase(C, dir) {
  const cfgFile = JSON.parse(fs.readFileSync(path.join(dir, 'config.json'), 'utf8'));
  const cfg = cfgFile.config, today = cfgFile.constants.TODAY;
  const users = new Map(csv(path.join(dir, 'users.csv')).map(r => [+r.user_id, { created: +r.created_day, level: +r.level, public: r.privacy === 'public', suspended: r.suspended === '1' }]));
  const groups = csv(path.join(dir, 'groups.csv')).map(r => ({ id: +r.group_id, name: r.name, about: r.about, discover: r.open === '1' && r.hidden_by_mods === '0', created: +r.created_day }))
    .sort((a, b) => a.id - b.id);
  const members = csv(path.join(dir, 'train_memberships.csv')).map(r => [+r.user_id, +r.group_id]);
  const posts = csv(path.join(dir, 'train_posts.csv')).map(r => ({ id: +r.post_id, user: +r.user_id, group: +r.group_id, day: +r.day, hidden: r.hidden_by_mods === '1' }));
  const likes = csv(path.join(dir, 'train_likes.csv')).map(r => [+r.post_id, +r.user_id]);
  const friends = csv(path.join(dir, 'friendships.csv')).map(r => [+r.user_a, +r.user_b]);
  const blocks = csv(path.join(dir, 'blocks.csv')).map(r => [+r.user_id, +r.blocked_id]);
  const notInt = new Set(csv(path.join(dir, 'not_interested.csv')).map(r => r.user_id + '|' + r.group_id));
  const clusters = new Map(csv(path.join(dir, 'clusters.csv')).map(r => [+r.group_id, +r.cluster]));
  let noise = null;
  if (fs.existsSync(path.join(dir, 'noise.csv'))) {
    noise = { size: new Map(), pair: new Map() };
    for (const r of csv(path.join(dir, 'noise.csv'))) {
      if (r.kind === 'size') noise.size.set(+r.group_a, +r.value);
      else if (r.kind === 'pair') noise.pair.set(+r.group_a + '|' + +r.group_b, +r.value);
    }
  }
  const world = { today, users, groups, members, posts, likes };
  const stats = C.groupStats(world, cfg, { noise, seed: cfg.noise_seed == null ? cfg.seed : cfg.noise_seed });
  const { vecs } = C.tfidf(groups.map(g => g.name + ' ' + g.about));
  const sim = C.simRows(vecs);
  const created = groups.map(g => g.created), discover = Uint8Array.from(groups, g => g.discover ? 1 : 0);
  const off = C.offParts(stats, created, today, discover, cfg);
  const cluster = groups.map(g => clusters.get(g.id));
  const served = [...new Set(cfgFile.users)].sort((a, b) => a - b);
  const order = cfgFile.serve_order;
  const cap = cfg.c == null ? Infinity : Math.max(1, Math.floor(cfg.c * C.K * served.length + 1e-9));
  const shared = { used: new Float64Array(stats.G), cap };
  const coTrue = cfg.burst_w !== 1 && cfg.m == null && !stats.noisy ? C.trueShared(world, stats) : null;
  /* who is in which group, friends, blocks */
  const myGroups = new Map();
  for (const [u, g] of members) { let s = myGroups.get(u); if (!s) myGroups.set(u, s = new Set()); s.add(g); }
  const blocked = new Set(blocks.flatMap(([a, b]) => [a + '|' + b, b + '|' + a]));
  const friendOf = new Map();
  for (const [a, b] of friends) for (const [x, y] of [[a, b], [b, a]]) { let s = friendOf.get(x); if (!s) friendOf.set(x, s = new Set()); s.add(y); }
  const got = new Map(), relaxed = { quota: 0, topic: 0, global: 0 };
  for (const u of order) {
    const mineSet = myGroups.get(u) || new Set();
    const mine = groups.map((g, i) => mineSet.has(g.id) ? i : -1).filter(i => i >= 0);
    const allowed = Uint8Array.from(groups, g => g.discover && !mineSet.has(g.id) && !notInt.has(u + '|' + g.id) ? 1 : 0);
    /* R6, R8, R9: public friends who count, not blocked either way; each with every group they're in */
    const friendsIn = new Map();
    for (const f of [...(friendOf.get(u) || [])].sort((a, b) => a - b)) {
      const x = users.get(f);
      if (!x || !x.public || !C.friendOk(stats, f) || blocked.has(u + '|' + f)) continue;
      for (const g of myGroups.get(f) || []) { const i = stats.gi.get(g); let a = friendsIn.get(i); if (!a) friendsIn.set(i, a = []); a.push(f); }
    }
    const res = C.recommendOne({ stats, cfg, ui: { mine, allowed, friendsIn, friendW: stats.accountW }, off, sim, cluster, created, today, shared, coTrue });
    for (const k in relaxed) relaxed[k] += res.relaxed[k];
    got.set(u, res.items.map((it, r) => ({ rank: r + 1, group: groups[it.g].id, g: it.g, score: it.score, code: it.reason.code, reason: it.reason, mine,
      text: C.reasonText(it.reason, i => groups[i].name, f => 'user ' + f) })));
  }
  /* compare */
  const exp = csv(path.join(dir, 'expected.csv'));
  const byUser = new Map();
  for (const r of exp) { let a = byUser.get(+r.user_id); if (!a) byUser.set(+r.user_id, a = []); a.push(r); }
  let rows = 0, bad = 0, ties = 0;
  const problems = [];
  /* A numerical tie: an "AI model" reason ("Because you're in X") where the expected X and ours are linked to the suggested group by the
     same value up to 1e-9 (typically a group with no members who count: every link to it is 0, and numpy picks X by LAPACK's rounding
     noise, about 1e-17). Both answers are equally true; such rows are counted apart, never hidden. */
  const tie = (h, w) => {
    if (h.code !== 'similar_group' || h.reason.via !== 'mf' || !w.reason_text.startsWith("Because you're in ")) return false;
    const name = w.reason_text.slice("Because you're in ".length), src = h.mine.find(i => groups[i].name === name);
    return src !== undefined && Math.abs(C.link(stats, src, h.g) - C.link(stats, h.reason.ref, h.g)) < 1e-9;
  };
  for (const [u, want] of byUser) {
    const have = got.get(u) || [];
    if (have.length !== want.length) { bad++; problems.push(`user ${u}: ${have.length} rows, expected ${want.length}`); continue; }
    want.forEach((w, i) => {
      rows++;
      const h = have[i], why = [];
      if (h.group !== +w.group_id) why.push(`group ${h.group} != ${w.group_id}`);
      if (h.code !== w.reason_code) why.push(`code ${h.code} != ${w.reason_code}`);
      if (Math.abs(h.score - +w.score) > 1e-6) why.push(`score ${h.score.toFixed(6)} != ${w.score}`);
      if (h.text !== w.reason_text) { if (!why.length && tie(h, w)) { ties++; return; } why.push(`text "${h.text}" != "${w.reason_text}"`); }
      if (why.length) { bad++; if (problems.length < 8) problems.push(`user ${u} rank ${i + 1}: ${why.join('; ')}`); }
    });
  }
  for (const u of got.keys()) if (!byUser.has(u) && got.get(u).length) { bad++; problems.push(`user ${u}: unexpected rows`); }
  return { rows, bad, problems, relaxed, ties };
}

(async () => {
  const C = await core();
  const index = csv(path.join(CASES, 'index.csv'));
  let pass = 0, fail = 0;
  const totals = { rows: 0, ties: 0 };
  for (const c of index) {
    if (process.env.ONLY && !c.case.startsWith(process.env.ONLY)) continue;
    const t0 = Date.now();
    const r = await runCase(C, path.join(CASES, c.case));
    const rel = `${r.relaxed.quota} / ${r.relaxed.topic} / ${r.relaxed.global}`;
    const relOk = rel === c.relaxed || c.relaxed === undefined || +c.relaxed === r.relaxed.quota + r.relaxed.topic + r.relaxed.global;
    const good = r.bad === 0 && r.rows === +c.rows;
    if (good) pass++; else fail++;
    console.log(`${good ? 'PASS' : 'FAIL'} ${c.case}: ${r.rows - r.bad - r.ties}/${c.rows} rows match exactly${r.ties ? ', ' + r.ties + ' numerical ties' : ''}, relaxed ${rel}${relOk ? '' : ' (expected ' + c.relaxed + ')'} (${Date.now() - t0} ms)`);
    totals.rows += r.rows; totals.ties += r.ties;
    for (const p of r.problems) console.log('   ' + p);
  }
  console.log(`\n${pass} passed, ${fail} failed; ${totals.rows} rows, ${totals.ties} of them numerical ties (the group an AI-model reason names)`);
  process.exit(fail ? 1 : 0);
})();
