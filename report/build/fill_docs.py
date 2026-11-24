"""Rebuild results/final_choices.md and report/model-card.md from their templates (templates/ in this folder), with every number read
from results/ (written by notebook 11). No number in the two documents is typed by hand. Also checks that README.md quotes the headline
numbers of the same run.

Notebook 11 runs it at the end of section 13. By hand, from the ECSE557 folder:
    .venv\\Scripts\\python report\\build\\fill_docs.py           rebuild both documents
    .venv\\Scripts\\python report\\build\\fill_docs.py --check   only compare: exit code 1 if a document or README.md is out of date
"""
import json
import math
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'notebooks'))
import boingrec as br  # noqa: E402

R = ROOT / 'results'
F = br.FINAL_CONFIG
UP = 1e-9   # the results files keep 4 decimals: round half up, as the notebook does with its unrounded numbers
f2, f3, f4 = (lambda v: f'{v + UP:.2f}'), (lambda v: f'{v + UP:.3f}'), (lambda v: f'{v + UP:.4f}')
p0, p1 = (lambda v: f'{100 * v + UP:.0f}%'), (lambda v: f'{100 * v + UP:.1f}%')
js = lambda f: json.loads((R / f).read_text(encoding='utf-8'))


def values():
    """Every number the two documents quote, as text, read from the results files."""
    table = pd.read_csv(R / 'final_table.csv', index_col=0)
    row = {'popularity': 'Popularity (BOING today)', 'hybrid': 'Hybrid, no re-ranking (component)', 'exact': 'Final design without privacy',
           'clip': 'Final design, clipping only (test cases)', 'final': f'Final design (ε = {F.eps:g}, m = {F.m})',
           'eps05': 'Final design with ε = 0.5', 'eps2': 'Final design with ε = 2', 'eps5': 'Final design with ε = 5',
           'before': 'Final design before the review (ε = 5)', 'off': 'Personalisation off (default list)'}
    # final_table.csv keeps 4 decimals; final_config.json keeps the headline rows with 6, so read those first (a 4-decimal
    # 0.2205 would round up to 0.221, while the run's 0.220484 is 0.220)
    test6 = js('final_config.json')['test (1,406 members)']
    T = lambda k, c: (test6[row[k]][c] if row[k] in test6 and test6[row[k]].get(c) is not None else table.loc[row[k], c])
    costs = pd.read_csv(R / 'final_costs.csv', index_col=0)
    C = lambda start, col='cost': costs.loc[[i for i in costs.index if i.startswith(start)][0], col]
    clusters = pd.read_csv(R / 'final_topic_clusters.csv', index_col=0)
    clusters.index = clusters.index.astype(str)
    fine = pd.read_csv(R / 'final_eps_fine.csv', index_col=0)
    rounds = pd.read_csv(R / 'final_rounds.csv', index_col=0)
    below = max(e for e in fine.index if e < F.eps)
    act = pd.read_csv(R / 'final_activity_privacy.csv', index_col=0)
    reasons = pd.read_csv(R / 'final_reasons.csv', index_col=0)
    RS = lambda k, c: reasons.loc[row[k], c]
    newc = pd.read_csv(R / 'final_newcomers.csv', index_col=0)
    N = lambda k, c: newc.loc[row[k], c]
    sybil = pd.read_csv(R / 'final_sybil.csv')
    posting = pd.read_csv(R / 'final_sybil_posting.csv')
    promo = pd.read_csv(R / 'final_promotion.csv')
    promo = promo[promo['rule'].str.startswith('final')]
    promo_sizes = promo.groupby('rivals')['fake accounts'].first().sort_index()
    words = lambda xs, last: ', '.join(str(int(x)) for x in xs[:-1]) + f' {last} ' + str(int(xs[-1])) if len(xs) > 1 else str(int(xs[0]))
    weights = pd.read_csv(R / 'final_weights.csv')
    off_quiz = pd.read_csv(R / 'off_validation.csv', index_col=0)
    scope, sab, reach, rules = js('final_privacy_scope.json'), js('final_sabotage.json'), js('final_reachable.json'), js('final_rules.json')
    e4, e6, config = js('e4_recommendation.json'), js('e6_rules.json'), js('final_config.json')
    chosen = weights[(weights.alpha == F.alpha) & (weights.beta == F.beta) & (weights.gamma == F.gamma) & (weights.delta == F.delta)]
    total = lambda part, key: sum(s[part][key] for s in rules.values())
    faithful = sum(sum(v['true'] for v in s['faithful to the computed score (fidelity)'].values()) for s in rules.values())
    checked = sum(sum(v['shown'] for v in s['faithful to the computed score (fidelity)'].values()) for s in rules.values())
    each = config['checks on the practice quiz']['topic clusters']['the rule on each quiz alone']
    n_tested = 1406
    return {
        'clusters': F.clusters, 'eps': f'{F.eps:g}', 'share_pct': p0(F.size_share), 'odds': f'{math.exp(F.eps):.1f}',
        'w_a': f'{F.alpha:g}', 'w_b': f'{F.beta:g}', 'w_g': f'{F.gamma:g}', 'w_d': f'{F.delta:g}', 'w_rank': int(chosen['rank'].iloc[0]),
        'hybrid_ndcg': f3(T('hybrid', 'ndcg@5')), 'exact_ndcg': f3(T('exact', 'ndcg@5')), 'final_ndcg': f3(T('final', 'ndcg@5')),
        'final_newc': p1(T('final', 'newcomer_share')), 'before_newc': p1(T('before', 'newcomer_share')),
        'final_newc_r9': p1(T('final', 'newcomer_share (members who count)')),
        'final_below': int(round(T('final', 'lists below the quota (members who count)'))),
        'final_below_shown': f"{T('final', 'lists below the quota (count Discover shows)') + UP:.0f}",
        'before_below': int(round(T('before', 'lists below the quota (count Discover shows)'))),
        'cost_rerank': f3(C('Fair exposure')), 'cost_public': f4(C('"Small"')), 'cost_r9': f4(C('Fake-account')),
        'cost_r9_low': f4(C('Fake-account', 'cost low')), 'cost_r9_high': f4(C('Fake-account', 'cost high')), 'cost_r10': f3(C('Privacy')),
        'cost_eps05': f3(C('Stronger privacy')), 'gain_eps2': f3(-C('Weaker privacy instead: epsilon = 2')),
        'gain_eps5': f3(-C('Weaker privacy instead: epsilon = 5')), 'cost_weights': f4(C('The weights')),
        'cost_all': f3(C('Every rule')),
        'r1_eps': f"{rounds.loc[1, 'eps']:g}", 'r1_clusters': int(rounds.loc[1, 'clusters']),
        'w_best': rounds.loc[1, 'best mix'].strip('()').replace('.0,', ',').replace('.0)', ')'),
        'w_gap': f4(rounds.loc[1, 'best minus the mix']), 'w_gap_lo': f4(rounds.loc[1, 'best minus the mix, low']),
        'w_gap_hi': f4(rounds.loc[1, 'best minus the mix, high']),
        'eps_below': f'{below:g}', 'eps_below_acc': p1(fine.loc[below, 'accuracy kept']), 'eps_below_lo': p1(fine.loc[below, 'accuracy kept low']),
        'eps_below_hi': p1(fine.loc[below, 'accuracy kept high']), 'eps_below_alone': int(fine.loc[below, 'quizzes passing alone']),
        'eps_below_single': p0(fine.loc[below, 'single releases below 90%']),
        'epsc_acc': p1(fine.loc[F.eps, 'accuracy kept']), 'epsc_lo': p1(fine.loc[F.eps, 'accuracy kept low']),
        'epsc_hi': p1(fine.loc[F.eps, 'accuracy kept high']), 'epsc_new': p0(fine.loc[F.eps, 'newcomer slots kept']),
        'epsc_single': p0(fine.loc[F.eps, 'single releases below 90%']),
        'off_cov': f"{T('off', 'coverage'):.0f}", 'off_ndcg': f3(T('off', 'ndcg@5')), 'pop_ndcg': f3(T('popularity', 'ndcg@5')),
        'off_quiz_ndcg': f3(off_quiz.loc['newness weight 0.5', 'ndcg@5']), 'off_quiz_ndcg0': f3(off_quiz.loc['newness weight 0', 'ndcg@5']),
        'off_quiz_newc': p0(off_quiz.loc['newness weight 0.5', 'newcomer_share']), 'off_quiz_newc0': p0(off_quiz.loc['newness weight 0', 'newcomer_share']),
        'pile_chosen': p0(clusters.loc[str(F.clusters), 'lists with 3+ of one chosen topic']),
        'pile_15': p0(clusters.loc['15', 'lists with 3+ of one chosen topic']),
        'budget_15': p1(clusters.loc['15', "share of the hybrid's NDCG@5"]),
        'clusters_each': ', '.join(str(each[str(q)] or 'none') for q in range(5)),
        'pile_tastes': p0(clusters.loc["10 from the AI model's tastes", 'lists with 3+ of one chosen topic']),
        'tastes_budget': p1(clusters.loc["10 from the AI model's tastes", "share of the hybrid's NDCG@5"]),
        'hidden_pile_final': p0(T('final', 'lists with 3+ of one hidden topic')), 'hidden_pile_hybrid': p0(T('hybrid', 'lists with 3+ of one hidden topic')),
        'hidden_pile_exact': p0(T('exact', 'lists with 3+ of one hidden topic')),
        'honest_wait': p1(e4['cost_no_attack']['honest_memberships_turned_down'] / e4['cost_no_attack']['honest_memberships']),
        'd100': int(sybil[(sybil.attacker.str.startswith('D')) & (sybil.k == 100)]['target exposure'].iloc[0]),
        'd100_post_default': int(posting[(posting.attacker.str.startswith('D')) & (posting.k == 100)]['default lists showing the target'].iloc[0]),
        'post_default_before': int(posting[(posting.attacker.str.startswith('D')) & (posting.k == 100)]['default lists showing it, no attack'].iloc[0]),
        'sybil_ks': words(sorted(set(sybil.k) | set(posting.k)), 'and'),
        'promo_fakes': words(list(promo_sizes.to_numpy()), 'or'), 'promo_rivals': words(list(promo_sizes.index), 'or'),
        'hidden_nc': f"{N('final', 'hidden in new or small groups'):.0f}",
        'cap_slots': max(1, math.floor(F.c * br.K * n_tested + 1e-9)), 'all_slots': f'{br.K * n_tested:,}',
        'sab_group': sab['group'], 'sab_members': sab['members (count Discover shows)'], 'sab_counted': f"{sab['members who count']:g}",
        'sab_fakes': sab['first fix, attacker A: fake accounts'], 'sab_before_first': sab['first fix, attacker A: lists before'],
        'sab_after_first': sab['first fix, attacker A: lists after'], 'promo_first_gain': sab['first fix, attacker A: largest gain of another group'],
        'sab_fakes_d': sab['final, attacker D: fake accounts'], 'sab_before_final': sab['final, attacker D: lists before'],
        'sab_after_d': sab['final, attacker D: lists after'], 'promo_d_gain': sab['final, attacker D: largest gain of another group'],
        'promo_d4_fakes': sab['final, attacker D, 4 rivals: fake accounts'], 'promo_d4_lost': sab['final, attacker D, 4 rivals: lists the rivals lose'],
        'promo_d4_gain': sab['final, attacker D, 4 rivals: largest gain of another group'],
        'friends_over': f"{scope['friends']['of them in more than m groups (counted in full)']:,}",
        'friends_pairs': f"{scope['friends']['public friends that count, of tested members (pairs)']:,}",
        'act_changed': f"{scope['activity']['other members whose default list changed']:,}",
        'act_def_kept': p0(act.loc[[i for i in act.index if i.startswith('the definition alone')][0], 'accuracy kept']),
        'act_best_kept': p0(act['accuracy kept'].iloc[1:].max()),
        'cap_mean': f"{scope['shared cap']['other members whose list changed (default + personalised), mean'] + UP:.1f}",
        'cap_max': scope['shared cap']['the same, most in one trial'],
        'sens_sizes': f"{scope['sensitivity']['largest change, sizes']:g}", 'sens_pairs': f"{scope['sensitivity']['largest change, pairs']:g}",
        'shared_false_final': p0(RS('final', 'share naming groups that share nobody')),
        'shared_false_lo': p0(RS('final', 'share naming groups that share nobody, lowest draw')),
        'shared_false_hi': p0(RS('final', 'share naming groups that share nobody, highest draw')),
        'shared_false_eps5': p0(RS('eps5', 'share naming groups that share nobody')),
        'would_close': p0(RS('final', 'share of noisy counts that would be close')),
        'before_close': p0(RS('before', 'share of stated counts that are close')),
        'clip_close': p0(RS('clip', 'share of stated counts that are close')),
        'small_true_shown': p0(RS('final', 'share of "small group" reasons true (count Discover shows)')),
        'reasons_faithful': f'{faithful:,}', 'reasons_checked': f'{checked:,}',
        'personal_true': f"{total('true to the raw data, personalised lists', 'true'):,}",
        'personal_shown': f"{total('true to the raw data, personalised lists', 'shown'):,}",
        'true_personal': p1(total('true to the raw data, personalised lists', 'true') / total('true to the raw data, personalised lists', 'shown')),
        'default_true': f"{total('true to the raw data, default lists', 'true'):,}",
        'default_shown': f"{total('true to the raw data, default lists', 'shown'):,}",
        'final_hit': p0(T('final', 'hit_rate')), 'pop_hit': p0(T('popularity', 'hit_rate')),
        'no_group': f2(N('final', 'ndcg@5 no group yet (quiz)')), 'one_group': f2(N('final', 'ndcg@5 1 group (quiz)')),
        'new_members': f3(N('final', 'ndcg@5 new members (quiz)')), 'pop_new_members': f3(N('popularity', 'ndcg@5 new members (quiz)')),
        'found_nc': f"{N('final', 'found in new or small groups') + UP:.1f}",
        'share_new': p1(N('final', 'share new groups')), 'share_small': p1(N('final', 'share older small groups')),
        'pop_gini': f2(T('popularity', 'gini')), 'final_gini': f2(T('final', 'gini')),
        'unreach': reach['out of reach (closed or hidden groups)'], 'unreach_members': reach['members whose hidden groups are all out of reach'],
        'best_hit': p1(reach['best possible hit rate']),
        'faults': len(e6['checker_catches_faults']), 'checks': len({f_['check'] for f_ in e6['checker_catches_faults'].values()}),
        'members_all': f"{rules['Final design, all members']['members']:,}",
        # the model card's table
        'pop_hit_f': f3(T('popularity', 'hit_rate')), 'pop_lo': f3(T('popularity', 'ndcg@5 low')), 'pop_hi': f3(T('popularity', 'ndcg@5 high')),
        'pop_below': f"{T('popularity', 'lists below the quota (members who count)'):,.0f}", 'pop_cov': f"{T('popularity', 'coverage'):.0f}",
        'final_hit_f': f3(T('final', 'hit_rate')), 'final_lo': f3(T('final', 'ndcg@5 low')), 'final_hi': f3(T('final', 'ndcg@5 high')),
        'final_sd': f3(T('final', 'ndcg@5 sd')), 'final_cov': f"{T('final', 'coverage'):.0f}",
        'off_hit_f': f3(T('off', 'hit_rate')), 'off_newc': p1(T('off', 'newcomer_share')),
        'off_below': int(round(T('off', 'lists below the quota (members who count)'))), 'off_gini': f2(T('off', 'gini')),
    }


# README.md must quote these (the "Final" row of its progress table, and its E4 and E6 rows): text -> what it is
def readme_quotes(v):
    return {f"ε = {v['eps']}": 'the chosen epsilon', f"hit rate {v['final_hit']}": 'the hit rate', f"NDCG@5 {v['final_ndcg']}": 'NDCG@5',
            f"{v['final_newc_r9']} of slots for new or small groups": 'the newcomer share', f"{v['true_personal']} of reasons on personalised lists true":
            'the reasons that are true', f"{v['faults']} of {v['faults']} planted faults caught": 'the planted faults'}


def main(check_only=False):
    v = values()
    out_of_date = []
    for template, out in [('final_choices.md', R / 'final_choices.md'), ('model_card.md', ROOT / 'report' / 'model-card.md')]:
        text = (HERE / 'templates' / template).read_text(encoding='utf-8').format(**v)
        old = out.read_text(encoding='utf-8') if out.exists() else ''
        if check_only:
            if old.replace('\r\n', '\n') != text:
                out_of_date.append(str(out.relative_to(ROOT)))
        else:
            out.write_text(text, encoding='utf-8')
            print('wrote', out.relative_to(ROOT))
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    missing = [f'"{q}" ({what})' for q, what in readme_quotes(v).items() if q not in readme]
    if missing:
        print('README.md does not quote this run\'s numbers:', '; '.join(missing))
    else:
        print('README.md quotes this run\'s headline numbers.')
    if out_of_date:
        print('Out of date:', ', '.join(out_of_date))
    return 1 if (missing or out_of_date) else 0


if __name__ == '__main__':
    sys.exit(main(check_only='--check' in sys.argv[1:]))
