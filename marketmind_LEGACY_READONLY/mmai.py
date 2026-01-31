import subprocess, sys
from routes import dual_card_bp  # import the blueprint

app.register_blueprint(dual_card_bp)


MODULES = {
    # ✅ Trader + Metrics BOTH start the main Flask service
    "trader":  r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",
    "metrics": r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",

    # ✅ Seeder scripts
    "seeder1": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_data_seeder.py",
    "seeder2": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_seeder_app_ver15.py",
    "seeder3": r"MarketMindAI\MarketMindData\marketmind_data_seeder.py",
    "seeder4": r"MarketMindAI\MarketMindData\market_mind_data_seeder.py",

    # ✅ Utility scripts
    "rss":     r"MarketMindAI\MarketMindTrader\marketmind\rss_parser.py",
    "agents":  r"MarketMindAI\marketmind_agents\main.py",
    "tagger":  r"MarketMindAI\intention_tagger.py",
    "stream":  r"MarketMindAI\StreamMonitor.py",
}

def run_module(name):
    if name not in MODULES:
        print(f"[!] Unknown module '{name}'. Options: {', '.join(MODULES.keys())}")
        sys.exit(1)

    target = MODULES[name]
    print(f"[INFO] Launching module: {name} -> {target}")
    subprocess.run([sys.executable, target])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python mmai.py <module>\nAvailable: {', '.join(MODULES.keys())}")
        sys.exit(1)

    run_module(sys.argv[1])
