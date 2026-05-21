import sys
from datetime import datetime

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
except ImportError:
    print("[ERRO] Dependencias em falta. Execute: pip install pandas scikit-learn")
    sys.exit(1)

DATASET_FILE = 'triagens.csv'
OUTPUT_FILE  = 'base_conhecimento_b.pl'
RF_TREES     = 200
DT_MAX_DEPTH = 4
MIN_CF       = 0.60

try:
    df = pd.read_csv(DATASET_FILE)
    MIN_SAMPLES  = max(5, len(df) * 0.01)
except FileNotFoundError:
    print(f"[ERRO] {DATASET_FILE} nao encontrado. Corra primeiro: python gerar_dataset.py")
    sys.exit(1)

SINTOMAS = [
    'sem_respiracao', 'sem_pulso', 'resp_dificuldade', 'hemorragia', 'inconsciente',
    'convulsoes', 'dor_peito', 'dor_irradia', 'fala_dificil', 'fraqueza_lado',
    'febre_alta', 'confusao', 'dor_abd', 'febre_bebe',
    'tosse_febre', 'dor_persiste', 'vomitos', 'diarreia',
    'dor_garganta', 'constipacao', 'dor_leve', 'febre_baixa', 'mal_estar'
]

DESC_SINTOMA = {
    'sem_respiracao':   'paragem respiratoria',
    'sem_pulso':        'paragem cardiaca',
    'resp_dificuldade': 'dificuldade respiratoria grave',
    'hemorragia':       'hemorragia incontrolavel',
    'inconsciente':     'perda de consciencia',
    'convulsoes':       'convulsoes activas',
    'dor_peito':        'dor no peito',
    'dor_irradia':      'dor com irradiacao',
    'fala_dificil':     'dificuldade na fala',
    'fraqueza_lado':    'fraqueza unilateral',
    'febre_alta':       'febre alta (>39C)',
    'confusao':         'confusao mental',
    'dor_abd':          'dor abdominal intensa',
    'febre_bebe':       'febre em bebe (<3 meses)',
    'tosse_febre':      'tosse com febre',
    'dor_persiste':     'dor persistente sem alivio',
    'vomitos':          'vomitos repetidos',
    'diarreia':         'diarreia grave',
    'dor_garganta':     'dor de garganta',
    'constipacao':      'constipacao',
    'dor_leve':         'dor ligeira',
    'febre_baixa':      'febre baixa',
    'mal_estar':        'mal-estar geral',
}

NIVEL_LABELS = {
    'emergencia':          'EMERGENCIA',
    'muito_urgente':       'MUITO URGENTE',
    'urgente':             'URGENTE',
    'pouco_urgente':       'POUCO URGENTE',
    'sem_sintomas_alarme': 'SEM ALARME',
}
LEVEL_ORDER = ['emergencia', 'muito_urgente', 'urgente', 'pouco_urgente', 'sem_sintomas_alarme']


def gerar_explicacao(premises, level, cf, n_samples):
    positivos = [p for p in premises if not p.startswith('nao(')]
    negativos = [p[4:-1] for p in premises if p.startswith('nao(')]

    partes = []
    if positivos:
        descs = [DESC_SINTOMA.get(s, s) for s in positivos]
        partes.append('presenca de ' + ', '.join(descs))
    if negativos:
        descs = [DESC_SINTOMA.get(s, s) for s in negativos]
        partes.append('ausencia de ' + ', '.join(descs))

    condicao  = '; '.join(partes) if partes else 'padrao geral'
    nivel_txt = NIVEL_LABELS.get(level, level)
    cf_pct    = round(cf * 100)
    texto = f"Padrao ML ({nivel_txt}, confianca={cf_pct}%, n={n_samples}): {condicao}."
    return texto.replace("'", "''")


def extrair_regras_dt(clf, feature_names, class_names):
    tree        = clf.tree_
    class_names = list(class_names)
    regras      = []

    def percorrer(node, premissas_atuais):
        if tree.children_left[node] == -1:
            total = int(tree.n_node_samples[node])
            if total < MIN_SAMPLES:
                return
            vals       = tree.value[node][0]
            val_sum    = float(np.sum(vals))
            idx_classe = int(np.argmax(vals))
            cf         = float(vals[idx_classe]) / val_sum
            if cf < MIN_CF:
                return
            regras.append({
                'premises':  list(premissas_atuais),
                'level':     class_names[idx_classe],
                'cf':        round(cf, 2),
                'n_samples': total,
            })
            return

        feat = feature_names[tree.feature[node]]
        percorrer(tree.children_left[node],  premissas_atuais + [f'nao({feat})'])
        percorrer(tree.children_right[node], premissas_atuais + [feat])

    percorrer(0, [])
    return regras


def premises_to_prolog(premises):
    return ', '.join(premises)


def train_and_export():
    try:
        df = pd.read_csv(DATASET_FILE)
    except FileNotFoundError:
        print(f"[ERRO] {DATASET_FILE} nao encontrado. Corra primeiro: python gerar_dataset.py")
        sys.exit(1)

    available_syms = [s for s in SINTOMAS if s in df.columns]
    X = df[available_syms].fillna(0).astype(int)
    y = df['nivel']
    n_examples = len(df)

    print(f"[OK] Dataset carregado: {n_examples} exemplos, {len(available_syms)} sintomas")
    print(f"     Distribuicao: {dict(y.value_counts())}")

    # Random Forest -> feature importances -> ordem_sintomas_ml
    print(f"\n[RF] A treinar Random Forest ({RF_TREES} arvores)...")
    rf = RandomForestClassifier(n_estimators=RF_TREES, random_state=42, class_weight='balanced')
    rf.fit(X, y)

    importances_raw = dict(zip(available_syms, rf.feature_importances_))

    # Bonus clinico de prioridade: garante que sintomas graves ficam sempre antes dos benignos,
    # independentemente do que o RF calcule nos dados sinteticos.
    CLINICAL_BONUS = {
        'sem_respiracao': 0.50, 'sem_pulso': 0.50, 'resp_dificuldade': 0.50,
        'hemorragia': 0.50, 'inconsciente': 0.50, 'convulsoes': 0.50,
        'dor_peito': 0.30, 'dor_irradia': 0.30, 'fala_dificil': 0.30,
        'fraqueza_lado': 0.30, 'confusao': 0.30,
        'febre_alta': 0.10, 'febre_bebe': 0.10, 'dor_abd': 0.10,
        'tosse_febre': 0.10, 'dor_persiste': 0.10,
        'vomitos': 0.10, 'diarreia': 0.10, 'dor_garganta': 0.10,
    }

    importances = [
        (s, importances_raw[s] + CLINICAL_BONUS.get(s, 0.0))
        for s in available_syms
    ]
    importances_sorted = sorted(importances, key=lambda x: -x[1])
    ordered_symptoms   = [s for s, _ in importances_sorted]

    print("[RF] Feature importances (Top 10, com bonus clinico de prioridade):")
    for s, imp in importances_sorted[:10]:
        bar = '#' * min(round(imp * 100), 60)
        print(f"     {s:<22} {imp:.4f}  {bar}")

    # Decision Tree -> regras NOVAS dt_NNN
    print(f"\n[DT] A treinar Decision Tree (max_depth={DT_MAX_DEPTH}, min_samples_leaf={MIN_SAMPLES})...")
    dt = DecisionTreeClassifier(
        max_depth=DT_MAX_DEPTH,
        min_samples_leaf=MIN_SAMPLES,
        random_state=42,
        class_weight='balanced'
    )
    dt.fit(X, y)

    regras_dt = extrair_regras_dt(dt, available_syms, dt.classes_)

    level_priority = {lv: i for i, lv in enumerate(LEVEL_ORDER)}
    regras_dt.sort(key=lambda r: (level_priority.get(r['level'], 99), -r['cf']))

    print(f"[DT] {len(regras_dt)} regras extraidas (filtros: CF>={MIN_CF}, n>={MIN_SAMPLES}):")
    for r in regras_dt:
        print(f"     {r['level']:<22} CF={r['cf']:.2f}  n={r['n_samples']:>3}  premissas={r['premises']}")

    # Escrever base_conhecimento_b.pl
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = [
        f'% BASE DE CONHECIMENTO B - Triagem SNS24 (Gerada por ML)',
        f'% Gerado automaticamente em: {now}',
        f'% Dataset: {DATASET_FILE} ({n_examples} exemplos)',
        f'% Modelos: Random Forest ({RF_TREES} arvores), Decision Tree (max_depth={DT_MAX_DEPTH})',
        f'% Filtros: CF >= {MIN_CF}, n_amostras >= {MIN_SAMPLES}',
        '',
        ':- multifile regra/4.',
        ':- multifile explicacao_regra/2.',
        ':- discontiguous regra/4.',
        ':- discontiguous explicacao_regra/2.',
        '',
        '% Sintomas ordenados por feature importance (RF) + bonus clinico de prioridade.',
    ]

    chunks = [ordered_symptoms[i:i+4] for i in range(0, len(ordered_symptoms), 4)]
    lines.append('ordem_sintomas_ml([')
    for i, chunk in enumerate(chunks):
        sep = '' if i == len(chunks) - 1 else ','
        lines.append('    ' + ', '.join(chunk) + sep)
    lines.append(']).')
    lines.append('')

    lines += [
        '% ----------------------------------------------------------------',
        '% REGRAS GERADAS PELA DECISION TREE',
        '% IDs dt_NNN distinguem-se dos r_XXX manuais da Parte A.',
        '% O motor combina-as automaticamente via findall sobre regra/4.',
        '% ----------------------------------------------------------------',
        '',
    ]

    if not regras_dt:
        lines += [
            f'% [AVISO] Nenhuma regra extraida. Tente reduzir MIN_CF ({MIN_CF}) ou MIN_SAMPLES ({MIN_SAMPLES}).',
            '',
        ]
    else:
        rules_by_level = {lv: [] for lv in LEVEL_ORDER}
        for r in regras_dt:
            if r['level'] in rules_by_level:
                rules_by_level[r['level']].append(r)

        counter = 1
        for lv in LEVEL_ORDER:
            group = rules_by_level[lv]
            if not group:
                continue
            label = NIVEL_LABELS.get(lv, lv.upper())
            lines.append(f'% {label}')
            for r in group:
                rule_id  = f'dt_{counter:03d}'
                prolog_p = premises_to_prolog(r['premises'])
                expl     = gerar_explicacao(r['premises'], lv, r['cf'], r['n_samples'])

                lines.append(f'% CF={r["cf"]:.2f}, n={r["n_samples"]}')
                lines.append(f'regra({rule_id}, se([{prolog_p}]), entao({lv}), {r["cf"]}).')
                lines.append(f"explicacao_regra({rule_id}, '{expl}').")
                lines.append('')
                counter += 1

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"\n[OK] Exportado: {OUTPUT_FILE}")
    print(f"     {len(regras_dt)} regras novas | {len(ordered_symptoms)} sintomas ordenados")


if __name__ == '__main__':
    train_and_export()