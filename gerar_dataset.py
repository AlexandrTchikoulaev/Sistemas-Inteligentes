import re
import csv
import random

SINTOMAS = [
    'sem_respiracao', 'sem_pulso', 'resp_dificuldade', 'hemorragia', 'inconsciente',
    'convulsoes', 'dor_peito', 'dor_irradia', 'fala_dificil', 'fraqueza_lado',
    'febre_alta', 'confusao', 'dor_abd', 'febre_bebe',
    'tosse_febre', 'dor_persiste', 'vomitos', 'diarreia',
    'dor_garganta', 'constipacao', 'dor_leve', 'febre_baixa', 'mal_estar'
]

def parse_rules(filepath='base_conhecimento_a.pl'):
    rules = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[AVISO] {filepath} nao encontrado. A usar regras embutidas.")
        return get_embedded_rules()

    pattern = r'regra\(\s*(\w+)\s*,\s*se\(\[([^\]]*)\]\)\s*,\s*entao\(\s*(\w+)\s*\)\s*,\s*([\d.]+)\s*\)'
    for m in re.finditer(pattern, content):
        rule_id   = m.group(1)
        syms_raw  = m.group(2)
        level     = m.group(3)
        cf        = float(m.group(4))

        positive_syms = []
        negated_syms  = []
        for tok in syms_raw.split(','):
            tok = tok.strip()
            if not tok:
                continue
            neg_match = re.match(r'nao\((\w+)\)', tok)
            if neg_match:
                negated_syms.append(neg_match.group(1))
            else:
                positive_syms.append(tok)

        rules.append({
            'id':            rule_id,
            'positive_syms': positive_syms,
            'negated_syms':  negated_syms,
            'syms_raw':      syms_raw.strip(),
            'level':         level,
            'cf':            cf
        })

    if not rules:
        print("[AVISO] Nenhuma regra encontrada no parser. A usar regras embutidas.")
        return get_embedded_rules()

    print(f"[OK] {len(rules)} regras lidas de {filepath}")
    return rules

def get_embedded_rules():
    return [
        # EMERGENCIA
        {'id': 'r_em1', 'positive_syms': ['sem_respiracao'],               'negated_syms': [], 'syms_raw': 'sem_respiracao',                         'level': 'emergencia',          'cf': 0.95},
        {'id': 'r_em2', 'positive_syms': ['sem_pulso'],                    'negated_syms': [], 'syms_raw': 'sem_pulso',                              'level': 'emergencia',          'cf': 0.95},
        {'id': 'r_em3', 'positive_syms': ['resp_dificuldade'],             'negated_syms': [], 'syms_raw': 'resp_dificuldade',                       'level': 'emergencia',          'cf': 0.85},
        {'id': 'r_em4', 'positive_syms': ['hemorragia'],                   'negated_syms': [], 'syms_raw': 'hemorragia',                             'level': 'emergencia',          'cf': 0.85},
        {'id': 'r_em5', 'positive_syms': ['inconsciente'],                 'negated_syms': [], 'syms_raw': 'inconsciente',                           'level': 'emergencia',          'cf': 0.85},
        {'id': 'r_em6', 'positive_syms': ['febre_alta', 'confusao', 'dor_abd'], 'negated_syms': [], 'syms_raw': 'febre_alta, confusao, dor_abd',    'level': 'emergencia',          'cf': 0.88},
        {'id': 'r_em7', 'positive_syms': ['convulsoes'],                   'negated_syms': [], 'syms_raw': 'convulsoes',                             'level': 'emergencia',          'cf': 0.85},
        # MUITO URGENTE
        {'id': 'r_mu1', 'positive_syms': ['dor_peito', 'dor_irradia'],    'negated_syms': [], 'syms_raw': 'dor_peito, dor_irradia',                 'level': 'muito_urgente',       'cf': 0.90},
        {'id': 'r_mu2', 'positive_syms': ['dor_peito'],                    'negated_syms': [], 'syms_raw': 'dor_peito',                              'level': 'muito_urgente',       'cf': 0.60},
        {'id': 'r_mu3', 'positive_syms': ['fala_dificil'],                 'negated_syms': [], 'syms_raw': 'fala_dificil',                           'level': 'muito_urgente',       'cf': 0.80},
        {'id': 'r_mu4', 'positive_syms': ['fraqueza_lado'],                'negated_syms': [], 'syms_raw': 'fraqueza_lado',                          'level': 'muito_urgente',       'cf': 0.80},
        {'id': 'r_mu6', 'positive_syms': ['dor_abd'],                      'negated_syms': ['febre_alta'], 'syms_raw': 'dor_abd',                                'level': 'muito_urgente',       'cf': 0.60},
        {'id': 'r_mu7', 'positive_syms': ['confusao'],                     'negated_syms': [], 'syms_raw': 'confusao',                               'level': 'muito_urgente',       'cf': 0.80},
        {'id': 'r_mu8', 'positive_syms': ['fala_dificil', 'fraqueza_lado'],'negated_syms': [], 'syms_raw': 'fala_dificil, fraqueza_lado',            'level': 'muito_urgente',       'cf': 0.92},
        {'id': 'r_mu9', 'positive_syms': ['febre_alta', 'dor_abd'],        'negated_syms': [], 'syms_raw': 'febre_alta, dor_abd',                    'level': 'muito_urgente',       'cf': 0.72},
        {'id': 'r_ur7', 'positive_syms': ['febre_bebe', 'vomitos', 'diarreia'],'negated_syms': [], 'syms_raw': 'febre_bebe, vomitos, diarreia',     'level': 'muito_urgente',       'cf': 0.88},
        # URGENTE
        {'id': 'r_ur1', 'positive_syms': ['febre_bebe'],                   'negated_syms': [], 'syms_raw': 'febre_bebe',                             'level': 'urgente',             'cf': 0.90},
        {'id': 'r_ur2', 'positive_syms': ['febre_alta', 'tosse_febre'],    'negated_syms': [], 'syms_raw': 'febre_alta, tosse_febre',                'level': 'urgente',             'cf': 0.80},
        {'id': 'r_ur3', 'positive_syms': ['vomitos', 'diarreia'],          'negated_syms': [], 'syms_raw': 'vomitos, diarreia',                      'level': 'urgente',             'cf': 0.75},
        {'id': 'r_ur4', 'positive_syms': ['febre_alta'],                   'negated_syms': [], 'syms_raw': 'febre_alta',                             'level': 'urgente',             'cf': 0.50},
        {'id': 'r_ur5', 'positive_syms': ['dor_persiste'],                 'negated_syms': [], 'syms_raw': 'dor_persiste',                           'level': 'urgente',             'cf': 0.40},
        {'id': 'r_ur6', 'positive_syms': ['dor_garganta'],                 'negated_syms': [], 'syms_raw': 'dor_garganta',                           'level': 'urgente',             'cf': 0.55},
        {'id': 'r_ur8', 'positive_syms': ['febre_alta', 'tosse_febre', 'dor_persiste'], 'negated_syms': [], 'syms_raw': 'febre_alta, tosse_febre, dor_persiste', 'level': 'urgente', 'cf': 0.85},
        {'id': 'r_ur9', 'positive_syms': ['dor_abd'],                      'negated_syms': ['vomitos', 'diarreia'], 'syms_raw': 'dor_abd, nao(vomitos), nao(diarreia)', 'level': 'urgente', 'cf': 0.80},
        # POUCO URGENTE
        {'id': 'r_pu1', 'positive_syms': ['constipacao'],                  'negated_syms': [], 'syms_raw': 'constipacao',                            'level': 'pouco_urgente',       'cf': 0.70},
        {'id': 'r_pu2', 'positive_syms': ['dor_leve'],                     'negated_syms': [], 'syms_raw': 'dor_leve',                               'level': 'pouco_urgente',       'cf': 0.65},
        {'id': 'r_pu3', 'positive_syms': ['febre_baixa'],                  'negated_syms': [], 'syms_raw': 'febre_baixa',                            'level': 'pouco_urgente',       'cf': 0.60},
        {'id': 'r_pu4', 'positive_syms': ['dor_leve', 'mal_estar'],        'negated_syms': [], 'syms_raw': 'dor_leve, mal_estar',                    'level': 'pouco_urgente',       'cf': 0.70},
        # SEM ALARME
        {'id': 'r_sa1', 'positive_syms': ['mal_estar'],                    'negated_syms': [], 'syms_raw': 'mal_estar',                              'level': 'sem_sintomas_alarme', 'cf': 0.55},
        {'id': 'r_sa2', 'positive_syms': ['constipacao', 'febre_baixa'],   'negated_syms': [], 'syms_raw': 'constipacao, febre_baixa',               'level': 'sem_sintomas_alarme', 'cf': 0.65},
    ]

NOISE_PROB    = 0.05
N_PER_CF_UNIT = 15

def generate_example(positive_syms, negated_syms, level, noise=NOISE_PROB):
    row = {s: 0 for s in SINTOMAS}
    for s in positive_syms:
        if s in row:
            row[s] = 1
    for s in negated_syms:
        if s in row:
            row[s] = 0
    for s in SINTOMAS:
        if s not in positive_syms and s not in negated_syms:
            if random.random() < noise:
                row[s] = 1
    row['nivel'] = level
    return row

def generate_dataset(rules, output_file='triagens.csv', seed=42):
    random.seed(seed)
    rows = []

    for rule in rules:
        n = max(5, round(rule['cf'] * N_PER_CF_UNIT))
        for _ in range(n):
            rows.append(generate_example(rule['positive_syms'], rule['negated_syms'], rule['level']))

    for _ in range(25):
        row = {s: 0 for s in SINTOMAS}
        if random.random() < 0.4:
            row['mal_estar'] = 1
        if random.random() < 0.3:
            row['constipacao'] = 1
        if random.random() < 0.2:
            row['febre_baixa'] = 1
        row['nivel'] = 'sem_sintomas_alarme'
        rows.append(row)

    random.shuffle(rows)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=SINTOMAS + ['nivel'])
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    counts = Counter(r['nivel'] for r in rows)
    print(f"[OK] Dataset gerado: {len(rows)} exemplos -> {output_file}")
    for nivel, n in sorted(counts.items()):
        print(f"  {nivel}: {n}")

if __name__ == '__main__':
    rules = parse_rules('base_conhecimento_a.pl')
    generate_dataset(rules)