import json
from collections import Counter
from statistics import median


def load_results(path="governance_results.jsonl"):

    with open(path) as f:
        return [json.loads(line) for line in f]


def action_distribution(results):

    counter = Counter(r["governance_action"] for r in results)
    total = len(results)

    stats = {}

    print("\n=== Governance actions ===")

    for action, n in sorted(counter.items()):
        pct = round(100 * n / total, 2)
        stats[action] = {
            "count": n,
            "percentage": pct
        }
        print(f"{action:12} {n:4} ({pct:.1f}%)")

    return stats


def critic_statistics(results):

    critic_scores = {}

    for r in results:
        for finding in r["findings"]:
            critic_scores.setdefault(
                finding["critic"],
                []
            ).append(finding["score"])

    stats = {}

    print("\n=== Average critic scores ===")

    for critic, values in critic_scores.items():

        avg = round(sum(values) / len(values), 3)

        stats[critic] = {
            "average_score": avg,
            "n": len(values)
        }

        print(f"{critic:10} {avg}")

    return stats


def severity_distribution(results):

    counter = Counter(
        r["risk_level"]
        for r in results
    )

    print("\n=== Risk levels ===")

    stats = dict(counter)

    for level, n in counter.items():
        print(level, n)

    return stats


def agreement_statistics(results):

    values = [
        r["critic_agreement"]
        for r in results
    ]

    avg = round(sum(values) / len(values), 3)

    print(f"\nAverage critic agreement: {avg}")

    return {
        "average": avg,
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }


def timing(results):

    values = [r["execution_time"] for r in results]

    avg = sum(values) / len(values)

    stats = {
        "average": round(avg, 3),
        "median": round(median(values), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }

    print("\n=== Execution time ===")
    print(f"Average : {stats['average']} s")
    print(f"Median  : {stats['median']} s")
    print(f"Min     : {stats['min']} s")
    print(f"Max     : {stats['max']} s")

    return stats


def common_findings(results):

    counter = Counter()

    for r in results:
        for finding in r["findings"]:
            counter[finding["finding"]] += 1

    print("\n=== Top findings ===")

    top = []

    for finding, n in counter.most_common(10):

        print(f"{n:4} {finding}")

        top.append({
            "finding": finding,
            "count": n
        })

    return top

def critic_severity_statistics(results):

    print("\n=== Severity by critic ===")

    stats = {}

    for critic in ["Anomaly", "Policy", "Safety"]:

        counter = Counter()

        for r in results:
            for f in r["findings"]:
                if f["critic"] == critic:
                    counter[f["severity"]] += 1

        stats[critic] = dict(counter)

        print(f"\n{critic}")

        for sev, n in sorted(counter.items()):
            print(f"  {sev:8} {n}")

    return stats

def findings_by_critic(results):

    print("\n=== Common findings by critic ===")

    stats = {}

    for critic in ["Anomaly", "Policy", "Safety"]:

        counter = Counter()

        for r in results:
            for f in r["findings"]:
                if f["critic"] == critic:
                    counter[f["finding"]] += 1

        stats[critic] = dict(counter)

        print(f"\n{critic}")

        for finding, n in counter.most_common(5):
            print(f"{n:4} {finding}")

    return stats

def risk_score_statistics(results):

    scores = [
        r["overall_risk_score"]
        for r in results
        if "overall_risk_score" in r
    ]

    if not scores:
        return {}

    stats = {
        "mean": round(sum(scores)/len(scores),3),
        "min": round(min(scores),3),
        "max": round(max(scores),3)
    }

    print("\n=== Overall risk score ===")

    for k,v in stats.items():
        print(f"{k:8} {v}")

    return stats

def decision_matrix(results):

    print("\n=== Risk -> Decision ===")

    matrix = Counter()

    for r in results:

        matrix[
            (
                r["risk_level"],
                r["governance_action"]
            )
        ] += 1

    stats = {}

    for key,n in sorted(matrix.items()):

        print(
            f"{key[0]:10} -> {key[1]:12} {n}"
        )

        stats[str(key)] = n

    return stats

def critic_activation(results):

    print("\n=== Critic activation ===")

    stats = {}

    for critic in ["Anomaly","Policy","Safety"]:

        active = 0

        for r in results:

            for f in r["findings"]:

                if (
                    f["critic"] == critic
                    and f["severity"] != "Low"
                ):
                    active += 1
                    break

        pct = round(
            100*active/len(results),
            2
        )

        stats[critic] = pct

        print(
            f"{critic:10} {pct}%"
        )

    return stats

def agreement_distribution(results):

    counter = Counter(
        r["critic_agreement"]
        for r in results
    )

    print("\n=== Critic agreement distribution ===")

    stats = dict(counter)

    for k,v in sorted(counter.items()):
        print(k,v)

    return stats

def critic_latency(results):

    print("\n=== Critic latency ===")

    stats = {}

    for critic in [
        "policy",
        "safety",
        "anomaly"
    ]:

        values = [
            r[f"{critic}_time"]
            for r in results
            if f"{critic}_time" in r
        ]

        if not values:
            continue

        avg = round(sum(values)/len(values),3)

        stats[critic] = avg

        print(
            f"{critic:10} {avg}s"
        )

    return stats

def detection_metrics(results):
    """
    Evaluate governance system as a binary anomaly detector.

    Positive = anomalous trace
    Negative = normal trace

    Prediction is considered positive if the governance system
    decided anything other than ALLOW.
    """

    tp = fp = tn = fn = 0

    for r in results:

        actual_positive = (r["label"].lower() == "anomalous")

        predicted_positive = (r["risk_level"] != "Low")

        if actual_positive and predicted_positive:
            tp += 1

        elif actual_positive and not predicted_positive:
            fn += 1

        elif not actual_positive and predicted_positive:
            fp += 1

        else:
            tn += 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    accuracy = (tp + tn) / len(results)

    fpr = fp / (fp + tn) if fp + tn else 0
    fnr = fn / (fn + tp) if fn + tp else 0

    print("\n=== Detection metrics ===")

    print(f"TP : {tp}")
    print(f"FP : {fp}")
    print(f"TN : {tn}")
    print(f"FN : {fn}")

    print()

    print(f"Accuracy  : {accuracy:.3f}")
    print(f"Precision : {precision:.3f}")
    print(f"Recall    : {recall:.3f}")
    print(f"F1-score  : {f1:.3f}")
    print(f"FPR       : {fpr:.3f}")
    print(f"FNR       : {fnr:.3f}")

    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "false_positive_rate": round(fpr, 3),
        "false_negative_rate": round(fnr, 3),
    }

def build_summary(results):

    return {
        "num_traces": len(results),
        "actions": action_distribution(results),
        "risk_levels": severity_distribution(results),
        "critic_scores": critic_statistics(results),
        "critic_severity": critic_severity_statistics(results),
        "critic_activation": critic_activation(results),
        "agreement": agreement_statistics(results),
        "agreement_distribution": agreement_distribution(results),
        "risk_scores": risk_score_statistics(results),
        "decision_matrix": decision_matrix(results),
        "timing": timing(results),
        "findings": common_findings(results),
        "findings_by_critic": findings_by_critic(results),
        "detection_metrics": detection_metrics(results)
    }


def save_summary(summary, path="experiment_summary.json"):

    with open(path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary written to {path}")

def decision_consistency(results):

    print("\nDecision consistency")

    total = len(results)

    consistent = sum(
        r["risk_level"] == "Low" and r["governance_action"] == "ALLOW"
        or r["risk_level"] == "Medium" and r["governance_action"] == "REVIEW"
        or r["risk_level"] == "High" and r["governance_action"] == "INTERVENE"
        or r["risk_level"] == "Critical" and r["governance_action"] == "BLOCK"
        for r in results
    )

    print(f"{consistent}/{total} ({100*consistent/total:.1f}%)")


if __name__ == "__main__":

    results = load_results()

    summary = build_summary(results)

    save_summary(summary)

    decision_consistency(results)

    # print(summary)