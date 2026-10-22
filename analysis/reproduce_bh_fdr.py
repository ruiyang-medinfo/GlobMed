#!/usr/bin/env python3
"""Reproduce GlobMed run-level BH-FDR sensitivity results with Python 3.10+.

No third-party packages, network access, manuscript file, or machine-specific
paths are required. Inputs are printed run accuracies and comparison metadata.
Run: python3 reproduce_bh_fdr.py --data-dir data --output-dir results
"""
import argparse
import csv
import itertools
import json
import math
import statistics
from collections import defaultdict
from decimal import Decimal, localcontext
from pathlib import Path

THRESHOLDS = [0.05, 0.01, 0.001, 0.0001]

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    if not rows:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def p_df4(t):
    """Stable exact two-sided Student t tail for four degrees of freedom."""
    t = abs(t)
    if math.isinf(t):
        return 0.0
    h = math.hypot(t, 2.0)
    return (4.0 / (h * (h + t))) ** 2 * (1.0 + t / (2.0 * h))

def paired_test(a, b):
    """Decimal arithmetic; zero variance is flagged, not an estimable t test."""
    with localcontext() as ctx:
        ctx.prec = 60
        diffs = [y - x for x, y in zip(a, b)]
        mean = sum(diffs) / 5
        sd = (sum((d - mean)**2 for d in diffs) / 4).sqrt()
        if sd == 0:
            # These values reproduce the ORIGINAL plotting convention only.
            # The ordinary t statistic and p value remain missing in the output.
            return diffs, mean, sd, None, None, 0.0 if mean else 1.0
        t = mean * Decimal(5).sqrt() / sd
        z = abs(t)
        h = (z*z + 4).sqrt()
        p = float((4 / (h * (h + z)))**2 * (1 + z / (2*h)))
        assert abs(p - p_df4(float(t))) < max(1e-14, p*1e-11)
        return diffs, mean, sd, float(t), p, p

def p_from_diffs(values):
    mu, sd = statistics.mean(values), statistics.stdev(values)
    return p_df4(mu * math.sqrt(5) / sd) if sd else (0.0 if mu else 1.0)

def rounding_bounds(diffs, epsilon=0.01):
    """Conservative extrema for five differences within +/-epsilon pp.

    Each displayed accuracy has rounding error at most 0.005 percentage points.
    Each paired difference thus has error at most 0.01 pp, also conservatively
    for equally weighted run aggregates. At stationary points on each face,
    all free coordinates equal Q_fixed/S_fixed. Enumerate the 3**5 faces.
    Shared inputs impose constraints not used here, so these are outer bounds.
    """
    low = [d-epsilon for d in diffs]
    high = [d+epsilon for d in diffs]
    candidates = [diffs]
    for state in itertools.product((-1, 0, 1), repeat=5):
        free = [i for i,s in enumerate(state) if s == 0]
        fixed = [i for i,s in enumerate(state) if s != 0]
        x = [low[i] if s == -1 else high[i] if s == 1 else 0.0 for i,s in enumerate(state)]
        if not free:
            candidates.append(x)
            continue
        left, right = max(low[i] for i in free), min(high[i] for i in free)
        if left > right:
            continue
        s = math.fsum(x[i] for i in fixed)
        q = math.fsum(x[i]**2 for i in fixed)
        if s:
            c = q/s
            if not left <= c <= right:
                continue
        elif q == 0:
            c = (left+right)/2
            if c == 0:
                c = right if right else left
        else:
            continue
        for i in free:
            x[i] = c
        candidates.append(x)
    scores = [p_from_diffs(x) for x in candidates]
    pmin, pmax = min(scores), max(scores)
    if math.fsum(low) <= 0 <= math.fsum(high):
        pmax = 1.0
    return pmin, pmax

def bh_adjust(pvalues):
    """BH step-up adjusted p values, returned in the input order."""
    n = len(pvalues)
    order = sorted(range(n), key=lambda i:pvalues[i])
    adjusted = [0.0]*n
    cumulative_min = 1.0
    for k in range(n-1, -1, -1):
        i = order[k]
        cumulative_min = min(cumulative_min, pvalues[i]*n/(k+1))
        adjusted[i] = cumulative_min
    for alpha in THRESHOLDS:
        largest = max([0]+[k+1 for k,i in enumerate(order) if pvalues[i] < alpha*(k+1)/n])
        assert sum(p < alpha for p in adjusted) == largest
    return adjusted

def level(p, cap):
    return sum(p < threshold for threshold in THRESHOLDS[:cap])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent/'data')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent/'results')
    args = parser.parse_args()
    raw = read_csv(args.data_dir/'run_accuracy.csv')
    comparisons = read_csv(args.data_dir/'comparisons.csv')
    values = {}
    languages = list(dict.fromkeys(r['language'] for r in raw))
    for r in raw:
        key = (r['kind'],r['model'],r['dataset'],int(r['run']),r['language'])
        assert key not in values, ('Duplicate input',key)
        values[key] = Decimal(r['accuracy_percent'])
    assert len(values) == 23040 and len(comparisons) == 4992

    def get_runs(kind,model,datasets,language):
        langs = languages if language == 'Overall' else [language]
        return [sum(values[(kind,model,d,run,l)] for d in datasets for l in langs)/Decimal(len(datasets)*len(langs)) for run in range(1,6)]

    results = []
    for c in comparisons:
        kind = 'fine' if c['family'] == 'globmed_finetuning' else 'base'
        datasets = c['datasets'].split(';')
        a_language = c['reference'] if c['family']=='language_disparity' else c['language']
        a = get_runs(kind,c['model1'],datasets,a_language)
        b = get_runs(kind,c['model2'],datasets,c['language'])
        dif,mean,sd,t,p,convention = paired_test(a,b)
        low,high = rounding_bounds([float(x) for x in dif])
        low,high = min(low,convention),max(high,convention)
        cap = 4 if c['group']=='Fig4' else 3
        row = dict(comparison_id=c['id'],family=c['family'],group=c['group'],figure=int(c['figure']),panel=c['panel'],model_A=c['model1'],model_B=c['model2'],reference_language=a_language,target_language=c['language'],datasets=c['datasets'],n_runs=5,df=4,mean_A_percent=float(sum(a)/5),mean_B_percent=float(sum(b)/5),difference_B_minus_A_pp=float(mean),SD_A_pp=statistics.stdev(map(float,a)),SD_B_pp=statistics.stdev(map(float,b)),SD_difference_pp=float(sd),t_statistic=t,p_raw=p,p_original_convention=convention,raw_level_original=level(convention,cap),zero_variance=(sd==0),rounding_p_lower=low,rounding_p_upper=high)
        for prefix,vs in [('A',a),('B',b)]:
            for i,x in enumerate(vs,1):row[f'{prefix}_run{i}']=float(x)
        results.append(row)
        if len(results)%1000==0:
            print(f'Recomputed {len(results)} comparisons',flush=True)

    families=defaultdict(list)
    for i,r in enumerate(results):families[r['family']].append(i)
    assert {k:len(v) for k,v in families.items()}=={'language_disparity':4928,'medical_finetuning':10,'reasoning':6,'globmed_finetuning':48}
    for indices in families.values():
        adjusted=bh_adjust([results[i]['p_original_convention'] for i in indices])
        conservative=bh_adjust([1.0 if results[i]['zero_variance'] else results[i]['p_raw'] for i in indices])
        lower=bh_adjust([results[i]['rounding_p_lower'] for i in indices])
        upper=bh_adjust([results[i]['rounding_p_upper'] for i in indices])
        for i,q,qc,lo,hi in zip(indices,adjusted,conservative,lower,upper):
            r=results[i];cap=4 if r['group']=='Fig4' else 3
            r.update(family_size=len(indices),p_BH_original_convention=q,p_BH_conservative=qc,BH_level_original=level(q,cap),BH_level_conservative=(None if r['zero_variance'] else level(qc,cap)),lost_significance_conservative=(not r['zero_variance'] and r['p_raw']<0.05<=qc),lost_significance_original=(r['p_original_convention']<0.05<=q),rounding_BH_lower=lo,rounding_BH_upper=hi,rounding_sensitive_at_005=(lo<0.05<=hi),inferential_status='Zero variance; ordinary t test not estimable' if r['zero_variance'] else 'Rounding sensitive at 0.05' if lo<0.05<=hi else 'Finite t test from printed runs')
    summary=[]
    for f,indices in families.items():
        rs=[results[i] for i in indices]
        summary.append(dict(family=f,comparisons=len(rs),zero_variance=sum(r['zero_variance'] for r in rs),raw_significant_original=sum(r['p_original_convention']<.05 for r in rs),BH_significant_original=sum(r['p_BH_original_convention']<.05 for r in rs),raw_significant_finite=sum(r['p_raw'] is not None and r['p_raw']<.05 for r in rs),BH_significant_conservative=sum(not r['zero_variance'] and r['p_BH_conservative']<.05 for r in rs),lost_significance_original=sum(r['lost_significance_original'] for r in rs),level_changes_original=sum(r['raw_level_original']!=r['BH_level_original'] for r in rs),level_changes_conservative=sum(not r['zero_variance'] and r['raw_level_original']!=r['BH_level_conservative'] for r in rs)))
    args.output_dir.mkdir(parents=True,exist_ok=True)
    write_csv(args.output_dir/'all_comparisons.csv',results)
    write_csv(args.output_dir/'family_summary.csv',summary)
    write_csv(args.output_dir/'lost_significance.csv',[r for r in results if r['lost_significance_original']])
    write_csv(args.output_dir/'marker_level_changes_conservative.csv',[r for r in results if not r['zero_variance'] and r['raw_level_original']!=r['BH_level_conservative']])
    assert {r['comparison_id'] for r in results if r['lost_significance_original']} == {r['comparison_id'] for r in results if r['lost_significance_conservative']}
    write_csv(args.output_dir/'zero_variance.csv',[r for r in results if r['zero_variance']])
    write_csv(args.output_dir/'rounding_sensitive.csv',[r for r in results if r['rounding_sensitive_at_005'] and not r['zero_variance']])
    (args.output_dir/'results.json').write_text(json.dumps({'summary':summary,'comparisons':results},ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
