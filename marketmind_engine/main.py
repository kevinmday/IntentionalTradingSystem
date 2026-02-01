"""
Engine entrypoint (launcher authority).

This file now directly owns module dispatch.
Legacy mmai.py is no longer imported because it is not import-safe.
"""

import sys
import subprocess


MODULES = {
    # Trader + Metrics BOTH start the main Flask service
    "trader":  r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",
    "metrics": r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",

    # Seeder scripts
    "seeder1": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_data_seeder.py",
    "seeder2": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_seeder_app_ver15.py",
    "seeder3": r"MarketMindAI\MarketMindData\marketmind_data_seeder.py",
    "seeder4": r"MarketMindAI\MarketMindData\market_mind_data_seeder.py",

    # Utility scripts
    "rss":     r"MarketMindAI\MarketMindTrader\marketmind\rss_parser.py",
    "agents":  r"MarketMindAI\marketmind_agents\main.py",
    "tagger":  r"MarketMindAI\intention_tagger.py",
    "stream":  r"MarketMindAI\StreamMonitor.py",
}


def run_module(name: str):
    if name not in MODULES:
        print(f"[!] Unknown module '{name}'. Options: {', '.join(MODULES.keys())}")
        sys.exit(1)

    target = MODULES[name]
    print(f"[ENGINE] Launching module: {name} -> {target}")
    subprocess.run([sys.executable, target])
