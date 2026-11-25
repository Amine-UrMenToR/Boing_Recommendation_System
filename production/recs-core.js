/* THE RECOMMENDER'S CORE (19 Nov 2026): the ECSE 557 design, ported
   The owner's McGill ECSE 557 project (Group 14): "an ethical recommender for BOING's groups". This file is the JavaScript port of
   ECSE557/notebooks/boingrec.py (recommend(), group_stats(), rerank() and their helpers) with the final design's dials
   (ECSE557/results/final_config.json, notebook 11, after the two reviews of 1 November). Pure functions only: no database, no
   network, no imports, so the course's 13 test cases (ECSE557/testcases/) run against it in node (tests/recs/port.js), and recs.js
   (the routes, D1) feeds it BOING's data. Every rule is commented by its number (R1 ... R11, the handbooks' numbering).

   The method, in order (boingrec.py section 9):
     1. groupStats()  every statistic about OTHER members, made in one place, so R8, R9 and R10 act once for everything:
                      R8 suspended accounts never count; R9 only accounts at level L+ count, each once, and an account younger than
                      young_days counts burst_w (0: not until it is 30 days old) in memberships, posts, likes and as a friend;
                      R10 each member counts for at most m groups (a keyed hash picks which), then Laplace noise for epsilon on the
                      group sizes and the pair counts (co = X^T X). Everything else is computed from the noisy co (post-processing).
     2. four scores (the hybrid): "also joined" (item-item Jaccard of memberships, alpha), similar descriptions (TF-IDF cosine,
                      beta), friends (public friends who are members, gamma), hidden tastes (the AI model: the top-k eigenvectors
                      of co, i.e. a truncated SVD of the member x group table, delta). Each rescaled to 0-1 over the member's
                      candidates, then mixed.
     3. rerankUser()  greedy, one slot at a time (R4, R5): MMR (lam x relevance - (1 - lam) x similarity to the groups picked),
                      at least ceil(q x 5) slots for new or small groups, at most n per public topic cluster, no group above c of
                      all slots. A rule that can't be kept is relaxed in that order (quota, topic cap, global cap), and counted.
     4. reasonFor()   R6: one true reason per slot, from a fixed template: the part that adds the most, or "a fair chance" on a
                      quota slot. With the noise on, an "also joined" reason names the group but no count.
   R1: personalisation off (the default in BOING) skips step 2: everyone gets the same scores, recent activity and newness.
   R11: exactly K = 5 (fewer only when fewer groups can be shown), never an endless list.

   Differences from boingrec.py, all on purpose and none of them reached by the test cases:
   - the noise draws come from a secret source in BOING (opts.rand), and the clipping hash from a secret seed (opts.seed), as
     final_config.json "in BOING" asks; the test cases pass the draws (noise.csv) and seed 0;
   - BOING's default list can give a team-picked group a "curated" part (opts.curated; none in the course, so nothing changes there);
   - the eigen-solver is a Householder tridiagonalisation + implicit QL (the classic tred2/tql2), not LAPACK's: the same subspace
     (the test cases' taste gap is far above rounding), the sign of each taste fixed the same way.
   The rest is boingrec.py line for line: rounding to 10 decimals before comparing (numpy's round half to even), ties to the smaller
   group id, the same reason texts. */

/* ------------------------------------------------ the final design (results/final_config.json) */
export const FINAL = Object.freeze({
  alpha: 0.2, beta: 0.2, gamma: 0.3, delta: 0.3,   // the hybrid's weights: also joined, descriptions, friends, hidden tastes
  k: 10,                                           // the AI model's hidden tastes
  topic_weight: 0,                                 // chosen topics count for nothing (they never helped on the practice quiz)
  personal: true,                                  // R1: true for a member who switched personalisation on (BOING's default is off)
  off_new_w: 0.5,                                  // R1: personalisation off: weight of newness (the rest is recent activity)
  q: 0.2, c: 0.05, n: 2, lam: 0.8, clusters: 8,    // R4 quota and cap, R5 topic cap, MMR, public topic clusters
  L: 3, burst_w: 0, young_days: 30,                // R9
  eps: 1.5, m: 3, size_share: 0.1,                 // R10 (eps null = no noise)
  seed: 0, small_from: 'r9', r9_scope: 'all', count_under_noise: false,
});
export const K = 5, NEW_DAYS = 30, SMALL = 10, ACTIVE_DAYS = 30, WEEK = 7;
export const PARTS = ['cf', 'content', 'social', 'mf'];

/* ------------------------------------------------ numbers like numpy */
/* np.rint: round half to even */
export function rint(y) {
  const f = Math.floor(y), d = y - f;
  if (d > 0.5) return f + 1;
  if (d < 0.5) return f;
  return f % 2 === 0 ? f : f + 1;
}
/* np.round(x, 10) */
export const r10 = x => rint(x * 1e10) / 1e10;

/* R10's clipping key: splitmix64 applied three times to (seed, member, group), as boingrec.membership_keys. A member's draw depends only
   on their own rows, so adding or removing one member changes nobody else's. 64-bit arithmetic with BigInt. */
const M64 = (1n << 64n) - 1n;
function mix(x) {
  x = (x + 0x9E3779B97F4A7C15n) & M64;
  x = ((x ^ (x >> 30n)) * 0xBF58476D1CE4E5B9n) & M64;
  x = ((x ^ (x >> 27n)) * 0x94D049BB133111EBn) & M64;
  return x ^ (x >> 31n);
}
export function membershipKey(seed, u, g) {
  const s0 = mix(BigInt.asUintN(64, BigInt(seed)));
  return Number(mix(mix(s0 ^ BigInt.asUintN(64, BigInt(u))) ^ BigInt.asUintN(64, BigInt(g))) >> 11n) / 2 ** 53;
}

/* ------------------------------------------------ similar descriptions: TF-IDF like scikit-learn's default TfidfVectorizer
   lower case, tokens of 2+ word characters (\b\w\w+\b), idf = ln((1 + n) / (1 + df)) + 1, each vector scaled to length 1. */
export function tokens(text) {
  return (String(text || '').toLowerCase().match(/[\p{L}\p{N}_]+/gu) || []).filter(t => [...t].length >= 2);
}
/* texts: one per group (name + ' ' + about) -> {terms: [the vocabulary, sorted like scikit-learn's], vecs: [{ids, vals}]} with ids
   ascending, so every sum runs in scikit-learn's order: the norm, then cosine_similarity's second normalisation, then the dot product
   (scipy's sparse product adds term by term in index order). Same arithmetic, same floats. */
export function tfidf(texts) {
  const n = texts.length, df = new Map();
  const counts = texts.map(t => {
    const c = new Map();
    for (const w of tokens(t)) c.set(w, (c.get(w) || 0) + 1);
    for (const w of c.keys()) df.set(w, (df.get(w) || 0) + 1);
    return c;
  });
  const terms = [...df.keys()].sort(), id = new Map(terms.map((w, i) => [w, i]));
  const norml2 = vals => { let s = 0; for (let k = 0; k < vals.length; k++) s += vals[k] * vals[k]; s = Math.sqrt(s); if (s > 0) for (let k = 0; k < vals.length; k++) vals[k] /= s; };
  const vecs = counts.map(c => {
    const ids = Int32Array.from([...c.keys()].map(w => id.get(w)).sort((a, b) => a - b));
    const vals = Float64Array.from(ids, i => c.get(terms[i]) * (Math.log((1 + n) / (1 + df.get(terms[i]))) + 1));
    norml2(vals);           // TfidfVectorizer's norm='l2'
    norml2(vals);           // cosine_similarity normalises again
    return { ids, vals };
  });
  return { terms, vecs };
}
export function dot(a, b) {
  let s = 0, i = 0, j = 0;
  while (i < a.ids.length && j < b.ids.length) {
    if (a.ids[i] === b.ids[j]) { s += a.vals[i] * b.vals[j]; i++; j++; }
    else if (a.ids[i] < b.ids[j]) i++; else j++;
  }
  return s;
}
/* the groups x groups cosine similarity, one row at a time (cached): sim(j) -> Float64Array */
export function simRows(vecs) {
  const G = vecs.length, cache = new Map();
  return j => {
    let r = cache.get(j);
    if (!r) { r = new Float64Array(G); for (let g = 0; g < G; g++) r[g] = dot(vecs[j], vecs[g]); cache.set(j, r); }
    return r;
  };
}

/* ------------------------------------------------ the AI model: the eigenvectors of co (symmetric), largest eigenvalues first
   tred2 + tql2 (Householder to tridiagonal, then implicit QL), as in EISPACK / JAMA. a: Float64Array n x n (row-major, symmetric).
   Returns {values (ascending), vectors: Array of n Float64Array rows, column j = the j-th eigenvector}. */
export function eigSym(a, n) {
  const V = [], d = new Float64Array(n), e = new Float64Array(n);
  for (let i = 0; i < n; i++) { V.push(new Float64Array(n)); for (let j = 0; j < n; j++) V[i][j] = (a[i * n + j] + a[j * n + i]) / 2; }
  if (n === 0) return { values: d, vectors: V };
  /* tred2 */
  for (let j = 0; j < n; j++) d[j] = V[n - 1][j];
  for (let i = n - 1; i > 0; i--) {
    let scale = 0, h = 0;
    for (let k = 0; k < i; k++) scale += Math.abs(d[k]);
    if (scale === 0) {
      e[i] = d[i - 1];
      for (let j = 0; j < i; j++) { d[j] = V[i - 1][j]; V[i][j] = 0; V[j][i] = 0; }
    } else {
      for (let k = 0; k < i; k++) { d[k] /= scale; h += d[k] * d[k]; }
      let f = d[i - 1], g = Math.sqrt(h);
      if (f > 0) g = -g;
      e[i] = scale * g;
      h -= f * g;
      d[i - 1] = f - g;
      for (let j = 0; j < i; j++) e[j] = 0;
      for (let j = 0; j < i; j++) {
        f = d[j];
        V[j][i] = f;
        g = e[j] + V[j][j] * f;
        for (let k = j + 1; k <= i - 1; k++) { g += V[k][j] * d[k]; e[k] += V[k][j] * f; }
        e[j] = g;
      }
      f = 0;
      for (let j = 0; j < i; j++) { e[j] /= h; f += e[j] * d[j]; }
      const hh = f / (h + h);
      for (let j = 0; j < i; j++) e[j] -= hh * d[j];
      for (let j = 0; j < i; j++) {
        f = d[j]; g = e[j];
        for (let k = j; k <= i - 1; k++) V[k][j] -= (f * e[k] + g * d[k]);
        d[j] = V[i - 1][j];
        V[i][j] = 0;
      }
    }
    d[i] = h;
  }
  for (let i = 0; i < n - 1; i++) {
    V[n - 1][i] = V[i][i];
    V[i][i] = 1;
    const h = d[i + 1];
    if (h !== 0) {
      for (let k = 0; k <= i; k++) d[k] = V[k][i + 1] / h;
      for (let j = 0; j <= i; j++) {
        let g = 0;
        for (let k = 0; k <= i; k++) g += V[k][i + 1] * V[k][j];
        for (let k = 0; k <= i; k++) V[k][j] -= g * d[k];
      }
    }
    for (let k = 0; k <= i; k++) V[k][i + 1] = 0;
  }
  for (let j = 0; j < n; j++) { d[j] = V[n - 1][j]; V[n - 1][j] = 0; }
  V[n - 1][n - 1] = 1;
  e[0] = 0;
  /* tql2 */
  for (let i = 1; i < n; i++) e[i - 1] = e[i];
  e[n - 1] = 0;
  let f = 0, tst1 = 0;
  const EPS = 2 ** -52;
  for (let l = 0; l < n; l++) {
    tst1 = Math.max(tst1, Math.abs(d[l]) + Math.abs(e[l]));
    let m = l;
    while (m < n) { if (Math.abs(e[m]) <= EPS * tst1) break; m++; }
    if (m === n) m = n - 1;
    if (m > l) {
      let iter = 0;
      do {
        if (++iter > 100) break;
        let g = d[l], p = (d[l + 1] - g) / (2 * e[l]), r = Math.hypot(p, 1);
        if (p < 0) r = -r;
        d[l] = e[l] / (p + r);
        d[l + 1] = e[l] * (p + r);
        const dl1 = d[l + 1];
        let h = g - d[l];
        for (let i = l + 2; i < n; i++) d[i] -= h;
        f += h;
        p = d[m];
        let c = 1, c2 = c, c3 = c, s = 0, s2 = 0;
        const el1 = e[l + 1];
        for (let i = m - 1; i >= l; i--) {
          c3 = c2; c2 = c; s2 = s;
          g = c * e[i]; h = c * p;
          r = Math.hypot(p, e[i]);
          e[i + 1] = s * r;
          s = e[i] / r; c = p / r;
          p = c * d[i] - s * g;
          d[i + 1] = h + s * (c * g + s * d[i]);
          for (let k = 0; k < n; k++) {
            const row = V[k];
            h = row[i + 1];
            row[i + 1] = s * row[i] + c * h;
            row[i] = c * row[i] - s * h;
          }
        }
        p = -s * s2 * c3 * el1 * e[l] / dl1;
        e[l] = s * p;
        d[l] = c * p;
      } while (Math.abs(e[l]) > EPS * tst1);
    }
    d[l] += f;
    e[l] = 0;
  }
  return { values: d, vectors: V };
}
/* boingrec.taste_model: the k eigenvectors with the largest eigenvalues (stable: equal values keep their order), each one's sign
   fixed so that its largest loading (the first, on ties) is positive. Returns {strength: [k], V: Float64Array G x k (row-major)}. */
export function tasteModel(co, G, k) {
  const { values, vectors } = eigSym(co, G);
  const order = [...values.keys()].sort((x, y) => values[y] - values[x] || x - y).slice(0, Math.min(k, G));
  const kk = order.length, V = new Float64Array(G * kk);
  order.forEach((col, t) => {
    let peak = 0, best = -1;
    for (let g = 0; g < G; g++) { const a = Math.abs(vectors[g][col]); if (a > best) { best = a; peak = g; } }
    const sign = vectors[peak][col] < 0 ? -1 : 1;
    for (let g = 0; g < G; g++) V[g * kk + t] = sign * vectors[g][col];
  });
  return { strength: order.map(c => values[c]), V, k: kk };
}

/* ------------------------------------------------ public topic clusters (R5): KMeans on the TF-IDF vectors (the course: scikit-learn
   KMeans, 8 clusters, seed 0, 10 starts). Group texts are public, so this needs no privacy. k-means++ starts from a seeded generator;
   BOING computes them once a day. The test cases give the course's own clusters as data (clusters.csv), so this isn't compared. */
export function mulberry(seed) {
  let h = seed >>> 0;
  return () => {
    h = (h + 0x6D2B79F5) >>> 0;
    let x = h;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
export function kmeans(vecs, kWanted, seed = 0, starts = 10, iters = 50) {
  const G = vecs.length, k = Math.min(kWanted, G);
  if (k <= 0) return { labels: [], centroids: [] };
  if (k === G) return { labels: vecs.map((_, i) => i), centroids: vecs.map(v => new Map(Array.from(v.ids, (t, x) => [t, v.vals[x]]))) };
  const T = vecs.reduce((m, v) => Math.max(m, v.ids.length ? v.ids[v.ids.length - 1] + 1 : 0), 0);
  const idx = vecs.map(v => Array.from(v.ids, (t, k) => [t, v.vals[k]]));
  const norm2 = idx.map(p => p.reduce((s, [, x]) => s + x * x, 0));
  let best = null;
  for (let run = 0; run < starts; run++) {
    const rand = mulberry(seed * 1000003 + run + 1), C = [];
    const dense = i => { const c = new Float64Array(T); for (const [t, x] of idx[i]) c[t] = x; return c; };
    /* k-means++ */
    C.push(dense(Math.floor(rand() * G)));
    const dist = new Float64Array(G).fill(Infinity);
    while (C.length < k) {
      const c = C[C.length - 1];
      let cn = 0; for (let t = 0; t < T; t++) cn += c[t] * c[t];
      let sum = 0;
      for (let i = 0; i < G; i++) {
        let dp = 0; for (const [t, x] of idx[i]) dp += x * c[t];
        dist[i] = Math.min(dist[i], Math.max(0, norm2[i] - 2 * dp + cn));
        sum += dist[i];
      }
      let r = rand() * sum, pick = G - 1;
      for (let i = 0; i < G; i++) { r -= dist[i]; if (r < 0) { pick = i; break; } }
      C.push(dense(pick));
    }
    const labels = new Int32Array(G).fill(-1);
    let inertia = 0;
    for (let it = 0; it < iters; it++) {
      const cn = C.map(c => { let s = 0; for (let t = 0; t < T; t++) s += c[t] * c[t]; return s; });
      let moved = false;
      inertia = 0;
      for (let i = 0; i < G; i++) {
        let bj = 0, bd = Infinity;
        for (let j = 0; j < k; j++) {
          let dp = 0; for (const [t, x] of idx[i]) dp += x * C[j][t];
          const dd = norm2[i] - 2 * dp + cn[j];
          if (dd < bd - 1e-12) { bd = dd; bj = j; }
        }
        if (labels[i] !== bj) { labels[i] = bj; moved = true; }
        inertia += Math.max(0, bd);
      }
      if (!moved && it) break;
      const cnt = new Array(k).fill(0);
      for (let j = 0; j < k; j++) C[j] = new Float64Array(T);
      for (let i = 0; i < G; i++) { cnt[labels[i]]++; for (const [t, x] of idx[i]) C[labels[i]][t] += x; }
      for (let j = 0; j < k; j++) {
        if (!cnt[j]) { C[j] = dense(Math.floor(rand() * G)); continue; }
        for (let t = 0; t < T; t++) C[j][t] /= cnt[j];
      }
    }
    if (!best || inertia < best.inertia - 1e-12) best = { inertia, labels: [...labels], C };
  }
  /* centroids: Map term id -> weight */
  return { labels: best.labels, centroids: best.C.map(c => { const m = new Map(); c.forEach((x, t) => { if (x > 0) m.set(t, x); }); return m; }) };
}

/* ------------------------------------------------ 1. the statistics about other members (boingrec.group_stats)
   world: {today, users: Map uid -> {created, level, suspended}, groups: [{id, created, ...}] (id order), members: [[uid, gid]],
           posts: [{id, user, group, day, hidden}], likes: [[pid, uid]]}
   opts:  {noise: {size: Map gid -> draw, pair: Map 'a|b' -> draw} (the test cases), rand: () => (0, 1) (BOING: a secret source),
           seed: the clipping hash's seed (BigInt or number; BOING: secret)} */
export function laplace(rand, b) {
  let u = rand() - 0.5;
  while (u === -0.5) u = rand() - 0.5;
  return -b * Math.sign(u) * Math.log(1 - 2 * Math.abs(u));
}
export function groupStats(world, cfg, opts = {}) {
  const today = world.today, gids = world.groups.map(g => g.id), G = gids.length, gi = new Map(gids.map((g, i) => [g, i]));
  /* R8, R9: the accounts that count: not suspended, level L or more */
  const counted = new Set();
  for (const [u, x] of world.users) if (!x.suspended && x.level >= cfg.L) counted.add(u);
  /* R9 (r9_scope 'all'): each counted account's weight in the activity and as a friend: 1, or burst_w while young */
  const young = u => world.users.get(u).created > today - cfg.young_days;
  const accountW = new Map();
  for (const u of counted) accountW.set(u, young(u) ? cfg.burst_w : 1);
  /* the memberships that count, once each; a young member's entry in X is sqrt(burst_w), so it adds burst_w to sizes and pairs */
  const seen = new Set(), mem = [];
  for (const [u, g] of world.members) {
    if (!counted.has(u) || !gi.has(g)) continue;
    const key = u + '|' + g;
    if (seen.has(key)) continue;
    seen.add(key);
    mem.push({ u, g, w: cfg.burst_w !== 1 && young(u) ? Math.sqrt(cfg.burst_w) : 1 });
  }
  /* R10: each member counts for at most m groups: their m memberships with the smallest keyed hash (boingrec.clip_contributions) */
  const seed = opts.seed === undefined ? cfg.seed : opts.seed;
  let kept = mem;
  if (cfg.m != null) {
    const by = new Map();
    for (const r of mem) { let a = by.get(r.u); if (!a) by.set(r.u, a = []); a.push(r); }
    kept = [];
    for (const rows of by.values()) {
      if (rows.length <= cfg.m) { kept.push(...rows); continue; }
      rows.map(r => ({ r, key: membershipKey(seed, r.u, r.g) })).sort((x, y) => x.key - y.key).slice(0, cfg.m).forEach(x => kept.push(x.r));
    }
  }
  /* co = X^T X: the members two groups share (the diagonal: the sizes). The one table "also joined" and the AI model learn from. */
  const co = new Float64Array(G * G), rows = new Map();
  for (const r of kept) { let a = rows.get(r.u); if (!a) rows.set(r.u, a = []); a.push(r); }
  for (const a of rows.values())
    for (const x of a) for (const y of a) co[gi.get(x.g) * G + gi.get(y.g)] += x.w * y.w;
  /* R10: Laplace noise for epsilon: sizes get size_share of it (sensitivity m), pairs the rest (sensitivity m(m-1)/2); then only
     post-processing (a size below 0 is 0, a pair stays between 0 and its smaller group's size, the table stays symmetric) */
  const noisy = cfg.eps != null && Number.isFinite(cfg.eps);
  let drawn = null;
  if (noisy) {
    if (cfg.m == null || !(cfg.eps > 0)) throw new Error('eps needs m, and a positive eps');
    const bSize = cfg.m / (cfg.size_share * cfg.eps), bPair = (cfg.m * (cfg.m - 1) / 2) / ((1 - cfg.size_share) * cfg.eps);
    const draw = opts.noise ? null : opts.rand;
    if (!opts.noise && typeof draw !== 'function') throw new Error('the noise needs a random source');
    const sizes = new Float64Array(G);
    drawn = { size: new Float64Array(G), pair: new Float64Array(G * (G - 1) / 2) };
    for (let i = 0; i < G; i++) {
      const d = opts.noise ? (opts.noise.size.get(gids[i]) || 0) : laplace(draw, bSize);
      drawn.size[i] = d;
      sizes[i] = Math.max(co[i * G + i] + d, 0);
    }
    let p = 0;
    for (let i = 0; i < G; i++) for (let j = i + 1; j < G; j++, p++) {
      const d = opts.noise ? (opts.noise.pair.get(gids[i] + '|' + gids[j]) || 0) : laplace(draw, bPair);
      drawn.pair[p] = d;
      const v = Math.min(Math.max(co[i * G + j] + d, 0), Math.min(sizes[i], sizes[j]));
      co[i * G + j] = v; co[j * G + i] = v;
    }
    for (let i = 0; i < G; i++) co[i * G + i] = sizes[i];
  }
  const sizes = new Float64Array(G);
  for (let i = 0; i < G; i++) sizes[i] = co[i * G + i];
  const model = opts.skipTastes ? { strength: [], V: new Float64Array(0), k: 0 } : tasteModel(co, G, cfg.k);
  /* recent activity (personalisation off): posts in groups (not hidden by moderators) and the likes on them, counted accounts only,
     each with its author's weight (R9 'all': a young account's posts and likes count burst_w); "this week" = posts of the last 7 days */
  const activity = new Float64Array(G), postsWeek = new Float64Array(G);
  if (world.posts) {
    const recent = new Map();
    for (const p of world.posts) {
      if (!(p.group > 0) || p.hidden || !counted.has(p.user) || !(p.day > today - ACTIVE_DAYS) || !gi.has(p.group)) continue;
      recent.set(p.id, p);
      const i = gi.get(p.group), w = accountW.get(p.user);
      activity[i] += w;
      if (p.day > today - WEEK) postsWeek[i] += w;
    }
    for (const [pid, u] of world.likes || []) {
      const p = recent.get(pid);
      if (p && counted.has(u)) activity[gi.get(p.group)] += accountW.get(u);
    }
  }
  /* R4: new (created in the last 30 days) or small: fewer than 10 members WHO COUNT (R9: not suspended, level L+, a young account
     counting burst_w; no clipping, no noise), so the accounts R9 ignores can't push a rival over the line */
  const count = new Float64Array(G), seen2 = new Set();
  for (const [u, g] of world.members) {
    if (!counted.has(u) || !gi.has(g) || seen2.has(u + '|' + g)) continue;
    seen2.add(u + '|' + g);
    count[gi.get(g)] += young(u) ? cfg.burst_w : 1;
  }
  const newcomer = new Uint8Array(G);
  world.groups.forEach((g, i) => { if (g.created > today - NEW_DAYS || count[i] < SMALL) newcomer[i] = 1; });
  return { gids, gi, G, co, sizes, V: model.V, k: model.k, strength: model.strength, activity, postsWeek, newcomer, counted, accountW,
           memberCount: count, drawn, noisy };
}
/* boingrec.friend_accounts: the accounts that may count and be named as friends: counted, with a weight above 0 */
export const friendOk = (stats, u) => (stats.accountW.get(u) || 0) > 0;

/* "also joined": Jaccard from co (diagonal 0) */
export function jac(stats, i, j) {
  if (i === j) return 0;
  const G = stats.G, both = stats.co[i * G + j], either = stats.sizes[i] + stats.sizes[j] - both;
  return either > 0 ? both / either : 0;
}
/* the AI model's link from group i to group j: (V V^T)[i, j] */
export function link(stats, i, j) {
  const k = stats.k, V = stats.V;
  let s = 0;
  for (let t = 0; t < k; t++) s += V[i * k + t] * V[j * k + t];
  return s;
}

/* ------------------------------------------------ personalisation off (R1): the same two parts for everyone, already weighted
   active = log(1 + recent activity), scaled so the most active group on Discover gets 1; new = 1 for a group made today, 0 at 30 days.
   created: day of each group (stats order); discover: Uint8Array, 1 = on Discover (for the scale only); curated (BOING): Uint8Array. */
export function offParts(stats, created, today, discover, cfg, curated, curatedW = 0.25) {
  const G = stats.G, act = new Float64Array(G), active = new Float64Array(G), fresh = new Float64Array(G), cur = new Float64Array(G);
  let top = -Infinity;
  for (let g = 0; g < G; g++) { act[g] = Math.log1p(stats.activity[g]); if (discover[g] && act[g] > top) top = act[g]; }
  for (let g = 0; g < G; g++) {
    active[g] = (1 - cfg.off_new_w) * (top > 0 ? act[g] / top : 0);
    fresh[g] = cfg.off_new_w * Math.min(1, Math.max(0, 1 - (today - created[g]) / NEW_DAYS));
    if (curated && curated[g]) cur[g] = curatedW;
  }
  return { active, new: fresh, curated: cur };
}

/* rescale to 0-1 over the member's candidates (rounded to 10 decimals first; the same value everywhere says nothing: 0) */
export function rescale(s, allowed) {
  const G = s.length, out = new Float64Array(G);
  let lo = Infinity, hi = -Infinity;
  for (let g = 0; g < G; g++) if (allowed[g]) { const v = r10(s[g]); if (v < lo) lo = v; if (v > hi) hi = v; }
  const span = hi - lo;
  if (!(span > 0)) return out;
  for (let g = 0; g < G; g++) if (allowed[g]) out[g] = (r10(s[g]) - lo) / span;
  return out;
}

/* ------------------------------------------------ 2. one member's scores
   ui: {mine: [group indices, ascending] (every group they're in), allowed: Uint8Array (R7, R8: on Discover for them, not theirs, not
        dismissed...), friendsIn: Map group index -> [friend ids, ascending] (R6, R8, R9: public, counted, not blocked either way),
        friendW: Map friend -> weight}
   sim: simRows(...). Returns {parts: {cf, content, social, mf, active, new, curated} weighted, score, personal}. */
export function scoreUser(stats, cfg, ui, off, sim) {
  const G = stats.G, z = () => new Float64Array(G);
  const parts = { cf: z(), content: z(), social: z(), mf: z(), active: Float64Array.from(off.active), new: Float64Array.from(off.new),
                  curated: Float64Array.from(off.curated || z()) };
  let personal = false;
  if (cfg.personal) {
    const raw = { cf: z(), content: z(), social: z(), mf: z() }, mine = ui.mine;
    for (const j of mine) {
      const sr = sim(j);
      for (let g = 0; g < G; g++) {
        raw.cf[g] += jac(stats, j, g);
        raw.content[g] += sr[g];
        raw.mf[g] += link(stats, j, g);
      }
    }
    if (mine.length) for (let g = 0; g < G; g++) raw.content[g] /= mine.length;
    for (const [g, fr] of ui.friendsIn) for (const f of fr) raw.social[g] += ui.friendW ? ui.friendW.get(f) : 1;
    const w = { cf: cfg.alpha, content: cfg.beta, social: cfg.gamma, mf: cfg.delta };
    for (const p of PARTS) { const r = rescale(raw[p], ui.allowed); for (let g = 0; g < G; g++) parts[p][g] = w[p] * r[g]; }
    for (let g = 0; g < G && !personal; g++) if (ui.allowed[g] && PARTS.reduce((s, p) => s + parts[p][g], 0) > 0) personal = true;
  }
  /* nothing to go on (or personalisation off): the default list */
  if (!personal) for (const p of PARTS) parts[p].fill(0);
  else { parts.active.fill(0); parts.new.fill(0); parts.curated.fill(0); }
  const score = z();
  for (let g = 0; g < G; g++)
    score[g] = parts.cf[g] + parts.content[g] + parts.social[g] + parts.mf[g] + parts.active[g] + parts.new[g] + parts.curated[g];
  return { parts, score, personal };
}

/* ------------------------------------------------ 3. the fair re-ranking of one member's list (boingrec.rerank, one row)
   shared: {used: Float64Array (slots each group got so far, across members: R4's cap), cap}. Changes shared.used.
   Returns {picks: [group index], forced: [bool], relaxed: {quota, topic, global}}. */
export function rerankUser(rel, allowed, sim, newcomer, cluster, cfg, shared, k = K) {
  const G = rel.length, r = Float64Array.from(rel, r10);
  const avail = Uint8Array.from(allowed), closest = new Float64Array(G), perCluster = new Map();
  const need = Math.ceil(cfg.q * k - 1e-9), perTopic = cfg.n == null ? k : cfg.n;
  const picks = [], forced = [], relaxed = { quota: 0, topic: 0, global: 0 };
  let newcomersPicked = 0;
  for (let pos = 0; pos < k; pos++) {
    if (!avail.some(x => x)) break;
    const owed = need - newcomersPicked, force = owed > 0 && owed >= k - pos;
    const ok = (g, lvl) => avail[g] && (lvl >= 3 || shared.used[g] < shared.cap) && (lvl >= 2 || (perCluster.get(cluster[g]) || 0) < perTopic)
      && (lvl >= 1 || !force || newcomer[g]);
    let level = 0;
    while (level < 3 && !Array.from({ length: G }, (_, g) => g).some(g => ok(g, level))) level++;
    if (force && level >= 1) relaxed.quota++;
    if (level >= 2) relaxed.topic++;
    if (level >= 3) relaxed.global++;
    const mmr = g => r10(cfg.lam * r[g] - (1 - cfg.lam) * closest[g]);
    const best = lvl => { let bj = -1, bv = -Infinity; for (let g = 0; g < G; g++) if (ok(g, lvl)) { const v = mmr(g); if (v > bv) { bv = v; bj = g; } } return bj; };
    const j = best(level);
    forced.push(force && level === 0 ? j !== best(1) : false);
    picks.push(j);
    avail[j] = 0;
    shared.used[j] += 1;
    perCluster.set(cluster[j], (perCluster.get(cluster[j]) || 0) + 1);
    newcomersPicked += newcomer[j] ? 1 : 0;
    const sj = sim(j);
    for (let g = 0; g < G; g++) if (sj[g] > closest[g]) closest[g] = sj[g];
  }
  return { picks, forced, relaxed };
}

/* ------------------------------------------------ 4. the reason (R6): {code, ref, n?, about?, more?, sub?}
   codes: shared_members (ref = the member's group; n = the count stated, or none), similar_group (ref = their group; via 'mf' = the AI
   model "Because you're in X", via 'content' = "Similar to X, which you joined"), friend (ref = the first friend; more = the others),
   new_group (sub 'new' | 'small': "a fair chance"), active (sub 'week' | 'month'), curated (BOING's team picks), discover (none left).
   o: {created (days, stats order), today, coTrue (Float64Array, the true shared counts when there's no clipping and no noise)} */
export function fairChance(created, today, j) {
  return { code: 'new_group', sub: created[j] > today - NEW_DAYS ? 'new' : 'small', ref: 0 };
}
export function defaultReason(stats, parts, j, o) {
  const act = stats.activity[j], wk = stats.postsWeek[j] > 0 ? 'week' : 'month';
  if (parts.curated && parts.curated[j] > 0 && parts.curated[j] >= parts.active[j] && parts.curated[j] >= parts.new[j]) return { code: 'curated', ref: 0 };
  if (parts.active[j] >= parts.new[j] && act > 0) return { code: 'active', sub: wk, ref: 0 };
  if (stats.newcomer[j]) return fairChance(o.created, o.today, j);
  if (act > 0) return { code: 'active', sub: wk, ref: 0 };
  return { code: 'discover', ref: 0 };
}
export function personalReason(stats, cfg, parts, ui, j, sim, o) {
  let top = PARTS[0];
  for (const p of PARTS) if (parts[p][j] > parts[top][j]) top = p;
  if (parts[top][j] <= 0) return defaultReason(stats, parts, j, o);
  const mine = ui.mine, argmax = f => { let b = mine[0], bv = -Infinity; for (const g of mine) { const v = f(g); if (v > bv) { bv = v; b = g; } } return b; };
  if (top === 'cf') {
    const src = argmax(g => jac(stats, g, j));
    const co = o.coTrue || stats.co, n = rint(co[src * stats.G + j]);
    if (n < 1 || (stats.noisy && !cfg.count_under_noise)) return { code: 'shared_members', ref: src };
    return { code: 'shared_members', ref: src, n, about: cfg.m != null || stats.noisy };
  }
  if (top === 'mf') return { code: 'similar_group', via: 'mf', ref: argmax(g => link(stats, g, j)) };
  if (top === 'social') { const fr = ui.friendsIn.get(j); return { code: 'friend', ref: fr[0], more: fr.length - 1 }; }
  return { code: 'similar_group', via: 'content', ref: argmax(g => sim(g)[j]) };
}
/* the fixed templates (boingrec.recommend's texts). groupName(i), friendName(id) give the names. */
export function reasonText(r, groupName, friendName) {
  switch (r.code) {
    case 'shared_members':
      if (!r.n) return `Members of ${groupName(r.ref)} also joined it`;
      return `${r.about ? 'About ' : ''}${r.n} member${r.n > 1 ? 's' : ''} of ${groupName(r.ref)} ${r.n > 1 ? 'are' : 'is'} in it`;
    case 'similar_group': return r.via === 'mf' ? `Because you're in ${groupName(r.ref)}` : `Similar to ${groupName(r.ref)}, which you joined`;
    case 'friend': return r.more ? `Your friend ${friendName(r.ref)} and ${r.more} other friend${r.more > 1 ? 's' : ''} are members`
      : `Your friend ${friendName(r.ref)} is a member`;
    case 'new_group': return r.sub === 'new' ? 'A new group: we show new groups so they get a fair chance'
      : 'A small group: we show small groups so they get a fair chance';
    case 'active': return r.sub === 'week' ? 'Active this week' : 'Active this month';
    case 'curated': return 'Picked by the BOING team';
    default: return 'Open to everyone on Discover';
  }
}

/* ------------------------------------------------ one member, end to end: scores, the re-ranking, the reasons
   o: {stats, cfg, ui, off, sim, cluster, created, today, shared, coTrue}. Returns [{g (index), score, reason, forced, personal}]. */
export function recommendOne(o) {
  const { stats, cfg, ui, off, sim } = o;
  const sc = scoreUser(stats, cfg, ui, off, sim);
  const rel = rescale(sc.score, ui.allowed);
  const rr = rerankUser(rel, ui.allowed, sim, stats.newcomer, o.cluster, cfg, o.shared);
  const ro = { created: o.created, today: o.today, coTrue: o.coTrue };
  const items = rr.picks.map((j, r) => ({
    g: j, score: sc.score[j], forced: rr.forced[r], personal: sc.personal,
    reason: rr.forced[r] ? fairChance(o.created, o.today, j) : sc.personal ? personalReason(stats, cfg, sc.parts, ui, j, sim, ro)
      : defaultReason(stats, sc.parts, j, ro),
    parts: Object.fromEntries(Object.keys(sc.parts).map(p => [p, sc.parts[p][j]])),
  }));
  return { items, relaxed: rr.relaxed, personal: sc.personal };
}

/* the true number of members two groups share, among the accounts that count (each once): what a reason states when there is neither
   clipping nor noise but young accounts are weighted (boingrec.recommend, the case m = None, burst_w < 1, no eps) */
export function trueShared(world, stats) {
  const G = stats.G, out = new Float64Array(G * G), by = new Map(), seen = new Set();
  for (const [u, g] of world.members) {
    if (!stats.counted.has(u) || !stats.gi.has(g) || seen.has(u + '|' + g)) continue;
    seen.add(u + '|' + g);
    let a = by.get(u); if (!a) by.set(u, a = []); a.push(stats.gi.get(g));
  }
  for (const a of by.values()) for (const x of a) for (const y of a) out[x * G + y] += 1;
  return out;
}
