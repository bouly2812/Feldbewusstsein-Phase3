#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

struct MessPunkt {
    double t;
    double rho;
    double psi;
    double extern_signal;
    bool metall_artefakt = false;
};

struct UebergangEvent {
    double t;
    int z_neu;
    double c;
    double rho;
    double psi;
};

struct AuswerteErgebnis {
    int uebergaenge = 0;
    std::vector<double> c_verlauf;
    std::vector<int> artefakt_flags;
    std::vector<UebergangEvent> events;
};

AuswerteErgebnis auswerten(const std::vector<MessPunkt>& daten,
                        double schwelle = 0.72,
                        int persistenz = 5,
                        double max_extern_kopplung = 0.85,
                        double min_psi = 0.35) {
    AuswerteErgebnis res;
    res.c_verlauf.reserve(daten.size());
    res.artefakt_flags.reserve(daten.size());

    int streak = 0;
    int z_state = 0;

    for (const auto& p : daten) {
        if (!std::isfinite(p.t) || !std::isfinite(p.rho) ||
            !std::isfinite(p.psi) || !std::isfinite(p.extern_signal)) {
            res.c_verlauf.push_back(0.0);
            res.artefakt_flags.push_back(1);
            streak = 0;
            continue;
        }

        double rho = std::clamp(p.rho, 0.0, 1.0);
        double psi = std::clamp(p.psi, 0.0, 1.0);
        double c = std::clamp(0.4 * rho + 0.4 * psi + 0.2 * rho * psi, 0.0, 1.0);
        res.c_verlauf.push_back(c);

        bool extern_dominiert = (std::abs(p.extern_signal) > max_extern_kopplung) && (psi < min_psi);
        int art_flag = (p.metall_artefakt || extern_dominiert) ? 1 : 0;
        res.artefakt_flags.push_back(art_flag);

        if (art_flag == 0 && c >= schwelle) {
            ++streak;
            if (streak >= persistenz) {
                ++z_state;
                ++res.uebergaenge;
                res.events.push_back({p.t, z_state, c, rho, psi});
                streak = 0;
            }
        } else {
            streak = 0;
        }
    }
    return res;
}

int main() {
    std::vector<MessPunkt> test_reihe = {
        {0.0, 0.20, 0.25, 0.05, false},
        {1.0, 0.55, 0.60, 0.10, false},
        {2.0, 0.75, 0.78, 0.10, false},
        {3.0, 0.80, 0.82, 0.10, false},
        {4.0, 0.78, 0.85, 0.10, false},
        {5.0, 0.82, 0.84, 0.10, false},
        {6.0, 0.79, 0.86, 0.10, false}
    };
    auto out = auswerten(test_reihe);
    std::cout << "Erkannte Uebergaenge: " << out.uebergaenge
              << " | Artefakt-Schritte: " << std::count(out.artefakt_flags.begin(), out.artefakt_flags.end(), 1)
              << "\n";
    return 0;
}