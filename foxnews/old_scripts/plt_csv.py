import csv
import matplotlib.pyplot as plt
import seaborn as sns

csv_path = './output/wc_predict.csv'
with open(csv_path, 'rt') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    targets = [r['target'] for r in rows]
    warmth = [float(r['warmth_norm']) for r in rows]
    competence = [float(r['competence_norm']) for r in rows]

    plt.clf()
    plt.scatter(warmth, competence)
    for t, w, c in zip(targets, warmth, competence):
        plt.text(w, c, t)
    plt.xlabel("warmth")
    plt.ylabel("competence")
    plt.axhline(0, color='gray', linestyle='dashed')
    plt.axvline(0, color='gray', linestyle='dashed')
    plt.draw()
    plt.show()
