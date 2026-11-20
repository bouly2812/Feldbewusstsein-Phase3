import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Sample:
    t: float
    rho: float
    psi: float
    extern_signal: float = 0.0
    metallic_artifact: bool = False


def load_model_config(model_path: Path) -> tuple[float, int, float, float]:
    if not model_path.exists():
        return 0.72, 5, 0.85, 0.35
    data = json.loads(model_path.read_text(encoding="utf-8"))
    coupling = data.get("parameters", {}).get("coupling_c", {})
    env = data.get("environment_and_artifacts", {})
    return (
        float(coupling.get("transition_threshold", 0.72)),
        int(coupling.get("persistence_steps", 5)),
        float(env.get("max_extern_coupling", 0.85)),
        float(env.get("min_psi_for_internal_transition", 0.35)),
    )


def load_samples_from_csv(csv_path: Path) -> list[Sample]:
    samples: list[Sample] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metal_raw = str(row.get("metallic_artifact", "0")).strip().lower()
            samples.append(
                Sample(
                    t=float(row["t"]),
                    rho=float(row["rho"]),
                    psi=float(row["psi"]),
                    extern_signal=float(row.get("extern_signal", 0.0)),
                    metallic_artifact=metal_raw in {"1", "true", "yes", "ja"},
                )
            )
    return samples


def compute_c(rho: float, psi: float) -> float:
    rho_c = max(0.0, min(1.0, rho))
    psi_c = max(0.0, min(1.0, psi))
    return max(0.0, min(1.0, 0.4 * rho_c + 0.4 * psi_c + 0.2 * rho_c * psi_c))


def run_protocol(
    samples: list[Sample],
    threshold: float = 0.72,
    persistence: int = 5,
    max_extern: float = 0.85,
    min_psi: float = 0.35,
) -> dict:
    streak = 0
    z_state = 0
    transitions = []
    trace = []

    for s in samples:
        c = compute_c(s.rho, s.psi)
        extern_dominated = abs(s.extern_signal) > max_extern and s.psi < min_psi
        artifact_flag = bool(s.metallic_artifact or extern_dominated)

        if not artifact_flag and c >= threshold:
            streak += 1
            if streak >= persistence:
                z_state += 1
                transitions.append(
                    {
                        "t": s.t,
                        "z_state": z_state,
                        "c": round(c, 4),
                        "rho": s.rho,
                        "psi": s.psi,
                    }
                )
                streak = 0
        else:
            streak = 0

        trace.append(
            {
                "t": s.t,
                "z_state": z_state,
                "c": round(c, 4),
                "artifact_flag": int(artifact_flag),
                "streak": streak,
            }
        )

    return {
        "concept": "Feldbewusstsein",
        "threshold": threshold,
        "persistence": persistence,
        "transition_count": len(transitions),
        "artifact_count": sum(item["artifact_flag"] for item in trace),
        "transitions": transitions,
        "trace": trace,
    }


def export_report(report: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parents[2]
    thr, pers, max_ext, min_p = load_model_config(
        base_dir / "model" / "strang3_state_model.json"
    )
    csv_file = base_dir / "examples" / "testlauf_feldbewusstsein.csv"
    samples = load_samples_from_csv(csv_file)

    res = run_protocol(
        samples,
        threshold=thr,
        persistence=pers,
        max_extern=max_ext,
        min_psi=min_p,
    )

    out_dir = base_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    export_report(res, out_dir / "bericht_feldbewusstsein.json")

    print(
        json.dumps(
            {
                "concept": res["concept"],
                "transition_count": res["transition_count"],
                "artifact_count": res["artifact_count"],
                "transitions": res["transitions"],
            },
            indent=2,
        )
    )