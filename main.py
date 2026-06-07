#!/usr/bin/env python3
"""NetCrawler — AI-powered pentesting agent."""
from __future__ import annotations
import logging
import sys
import typer
from tui.app import NetCrawlerApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
    ]
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    add_completion=False,
    name="netcrawler",
    help="""
\b
NetCrawler — AI-Powered Pentesting Agent
=========================================
An autonomous recon and vulnerability scanning agent powered
by a local LLM (Ollama). Runs fully offline.

\b
Examples:
  netcrawler example.com
  netcrawler 192.168.1.1 --profile aggressive
  netcrawler example.com --model mistral --profile stealth
  netcrawler example.com --scope "example.com,api.example.com"
  netcrawler example.com --scope "192.168.1.0/24" --profile aggressive
  netcrawler example.com --timeout 30 --verbose

\b
Profiles:
  stealth     Passive recon only — no active scanning
  default     Balanced — recon, port scan, web fingerprint, service enum
  aggressive  Full scan — all modules, fuzzing, vuln detection

\b
Scope:
  Comma-separated list of allowed hosts, domains, or CIDR ranges.
  The agent will refuse to scan anything outside this list.
  The primary target is always implicitly in scope.

\b
Legal:
  Only scan targets you have explicit written permission to test.
    """,
)

PROFILES = {
    "stealth":    "Passive recon only — no active scanning",
    "default":    "Balanced — recon + port scan + web fingerprint + service enum",
    "aggressive": "Full scan — everything including fuzzing, vuln scan, all services",
}


@app.command()
def run(
    target: str = typer.Argument(
        ...,
        help="Target to scan — IP address, CIDR range, domain, or URL",
        metavar="TARGET",
    ),
    model: str = typer.Option(
        "deepseek-r1:14b",
        "--model", "-m",
        help="Ollama model to use for reasoning",
        metavar="MODEL",
    ),
    profile: str = typer.Option(
        "default",
        "--profile", "-p",
        help="Scan profile: stealth / default / aggressive",
        metavar="PROFILE",
    ),
    scope: str = typer.Option(
        "",
        "--scope", "-s",
        help='Engagement scope — comma separated hosts/CIDRs e.g. "example.com,192.168.1.0/24"',
        metavar="SCOPE",
    ),
    timeout: int = typer.Option(
        0,
        "--timeout", "-t",
        help="Max scan duration in minutes (0 = no limit)",
        metavar="MINUTES",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show raw tool output alongside AI interpretation",
    ),
    debug: bool = typer.Option(
        False,
        "--debug", "-d",
        help="Enable debug logging",
    ),
):
    """Scan a TARGET using the AI-driven agent."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    if profile not in PROFILES:
        typer.echo(f"[!] Unknown profile '{profile}'. Choose from: {', '.join(PROFILES)}")
        raise typer.Exit(1)

    logger.info(f"Starting NetCrawler scan: target={target}, profile={profile}, model={model}")
    
    try:
        tui = NetCrawlerApp(
            target=target,
            model=model,
            profile=profile,
            scope=scope,
            verbose=verbose,
            timeout_minutes=timeout,
        )
        tui.run()
        logger.info("Scan completed successfully")
    except KeyboardInterrupt:
        logger.warning("Scan interrupted by user")
        typer.echo("\n[!] Scan interrupted by user")
        raise typer.Exit(130)
    except Exception as e:
        logger.error(f"Scan failed with error: {e}", exc_info=True)
        typer.echo(f"[!] Scan failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
