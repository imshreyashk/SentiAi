import json
import os
import sys
import time
from stadium_engine import StadiumOperationsEngine, TelemetryPayload

# ── ANSI palette ──────────────────────────────────────────────────────────────
RST  = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

# Foreground
FG_WHITE   = "\033[97m"
FG_CYAN    = "\033[96m"
FG_YELLOW  = "\033[93m"
FG_GREEN   = "\033[92m"
FG_RED     = "\033[91m"
FG_MAGENTA = "\033[95m"
FG_BLUE    = "\033[94m"
FG_GRAY    = "\033[90m"

# Background
BG_BLACK   = "\033[40m"
BG_BLUE    = "\033[44m"
BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_MAGENTA = "\033[45m"

# ── Terminal helpers ───────────────────────────────────────────────────────────
def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 100

def hr(char: str = "─", color: str = FG_GRAY) -> str:
    return f"{color}{char * width()}{RST}"

def center(text: str, color: str = FG_WHITE, fill: str = " ") -> str:
    w = width()
    clean = text  # raw length approximation (ignores escape bytes)
    pad = max(0, (w - len(clean)) // 2)
    return f"{color}{fill * pad}{text}{fill * pad}{RST}"

# ── Threat-level styling ───────────────────────────────────────────────────────
def threat_style(score: float) -> tuple[str, str, str]:
    """Returns (level_label, fg_color, bg_color) based on score."""
    if score < 40.0:
        return "LOW   ", FG_GREEN,   BG_BLACK
    elif score < 70.0:
        return "MEDIUM", FG_YELLOW,  BG_BLACK
    else:
        return "HIGH  ", FG_RED,     BG_BLACK

# ── Banner ────────────────────────────────────────────────────────────────────
BANNER_LINES = [
    "  ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗ █████╗ ██╗      ██████╗ ██╗████████╗ ██████╗██╗  ██╗  ",
    "  ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔══██╗██║     ██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║  ",
    "  ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║███████║██║     ██████╔╝██║   ██║   ██║     ███████║  ",
    "  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══██║██║     ██╔═══╝ ██║   ██║   ██║     ██╔══██║  ",
    "  ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║██║  ██║███████╗██║     ██║   ██║   ╚██████╗██║  ██║  ",
    "  ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝  ",
]

def print_banner(tick: int) -> None:
    pulse_colors = [FG_CYAN, FG_BLUE, FG_MAGENTA, FG_BLUE]
    color = pulse_colors[tick % len(pulse_colors)]
    print()
    for line in BANNER_LINES:
        sys.stdout.write(f"{BOLD}{color}{line}{RST}\n")
    tagline = f"FIFA 2026 · STADIUM COMMAND NETWORK · SENTINAI-PITCH · ACTIVE CONTROL PROTOCOL"
    sys.stdout.write(center(f"{BOLD}{FG_WHITE}{tagline}{RST}") + "\n")
    sys.stdout.write(hr("═", FG_CYAN) + "\n")

# ── Section headers ───────────────────────────────────────────────────────────
def section_header(title: str, color: str = FG_CYAN) -> None:
    sys.stdout.write(f"\n{BOLD}{color}  ▌ {title}{RST}\n")
    sys.stdout.write(f"{DIM}{hr('─', FG_GRAY)}{RST}\n")

# ── Telemetry incident panel ──────────────────────────────────────────────────
def print_telemetry(payload: TelemetryPayload, score: float, ts: str) -> None:
    label, fg, _ = threat_style(score)
    occ_pct = (payload.current_occupancy / payload.max_capacity) * 100

    bar_len  = 30
    filled   = min(int((occ_pct / 100) * bar_len), bar_len)
    bar_color = fg
    bar = f"{bar_color}{'█' * filled}{FG_GRAY}{'░' * (bar_len - filled)}{RST}"

    sys.stdout.write(
        f"  {FG_GRAY}[{ts}]{RST}  "
        f"{BOLD}{FG_WHITE}GATE {str(payload.gate_id):<12}{RST}  "
        f"THREAT {BOLD}{fg}{label}{RST}  "
        f"SCORE {BOLD}{fg}{score:>6.2f}/100{RST}\n"
    )
    sys.stdout.write(
        f"  {DIM}Occupancy:{RST} {bar} {FG_WHITE}{occ_pct:>6.1f}%{RST}  "
        f"{DIM}({payload.current_occupancy:,}/{payload.max_capacity:,}){RST}\n"
    )
    sys.stdout.write(
        f"  {DIM}Transit:{RST} {FG_YELLOW}{payload.transit_status.upper():<10}{RST}  "
        f"{DIM}Temperament:{RST} {FG_MAGENTA}{payload.crowd_temperament.upper():<10}{RST}  "
        f"{DIM}Language:{RST} {FG_CYAN}{payload.active_language.upper()}{RST}\n"
    )
    sys.stdout.write(f"{DIM}{hr('·', FG_GRAY)}{RST}\n")

# ── Mitigation actions panel ──────────────────────────────────────────────────
def print_mitigation(gate_id: str, score: float, mitigation_json: str) -> None:
    label, fg, _ = threat_style(score)
    data = json.loads(mitigation_json)

    tag = f"[GATE {gate_id}]"
    sys.stdout.write(
        f"  {BOLD}{fg}■ {tag:<14}{RST} "
        f"{BOLD}{FG_WHITE}THREAT LEVEL: {fg}{label}{RST}\n"
    )
    sys.stdout.write(
        f"    {FG_BLUE}▶ ROUTING   {RST}{FG_WHITE}{data['dynamic_routing']}{RST}\n"
    )
    sys.stdout.write(
        f"    {FG_YELLOW}▶ STAFF     {RST}{FG_WHITE}{data['staff_allocation']}{RST}\n"
    )
    sys.stdout.write(
        f"    {FG_MAGENTA}▶ BROADCAST {RST}{FG_CYAN}\"{data['broadcast_msg']}\"{RST}\n"
    )
    sys.stdout.write(f"{DIM}{hr('·', FG_GRAY)}{RST}\n")

# ── Simulation events ─────────────────────────────────────────────────────────
EVENTS = [
    TelemetryPayload("A-NORTH",  320, 1000, "normal",  "calm",    "en"),
    TelemetryPayload("B-WEST",   760, 1000, "delayed", "anxious", "fr"),
    TelemetryPayload("C-EAST",   980, 1000, "blocked", "violent", "es"),
    TelemetryPayload("D-SOUTH",  200,  800, "normal",  "calm",    "ar"),
    TelemetryPayload("E-VIP",    410,  500, "delayed", "angry",   "en"),
    TelemetryPayload("F-PRESS",  150,  300, "normal",  "calm",    "fr"),
]

# ── Main loop ─────────────────────────────────────────────────────────────────
def run() -> None:
    engine   = StadiumOperationsEngine()
    tick     = 0
    window   = 3          # events visible at once
    interval = 4          # seconds per cycle

    print(f"{BOLD}{FG_CYAN}  Initialising SentinAI-Pitch Command Network...{RST}")
    time.sleep(1.2)

    while True:
        ts_now  = time.strftime("%H:%M:%S")
        indices = [(tick + i) % len(EVENTS) for i in range(window)]
        batch   = [EVENTS[i] for i in indices]

        scores       = [engine.evaluate_threat_score(p) for p in batch]
        mitigations  = [engine.broker_mitigation(p)     for p in batch]

        clear()
        print_banner(tick)

        # ── TELEMETRY PANEL
        section_header("LIVE TELEMETRY INCIDENTS", FG_CYAN)
        for p, sc in zip(batch, scores):
            print_telemetry(p, sc, ts_now)

        # ── MITIGATION PANEL
        section_header("AUTOMATED COGNITIVE MITIGATION ACTIONS", FG_YELLOW)
        for p, sc, m in zip(batch, scores, mitigations):
            print_mitigation(str(p.gate_id), sc, m)

        # ── Footer
        sys.stdout.write(hr("═", FG_CYAN) + "\n")
        sys.stdout.write(
            f"  {DIM}CYCLE {tick + 1:04d}  ·  {ts_now}  ·  "
            f"GATES MONITORED: {len(EVENTS)}  ·  ACTIVE WINDOW: {window}  ·  "
            f"NEXT REFRESH IN {interval}s  ·  Ctrl+C TO EXIT{RST}\n"
        )

        tick += 1
        time.sleep(interval)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n\n{BOLD}{FG_CYAN}  SentinAI-Pitch Command Network — SESSION TERMINATED.{RST}\n")
        sys.exit(0)
