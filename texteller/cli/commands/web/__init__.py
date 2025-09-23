import os
import sys
import click
from pathlib import Path
from texteller.globals import Globals


@click.command()
@click.option(
    "--enable-http/--disable-http",
    default=None,
    help="Enable or disable HTTP/webserver functionality (defaults to global setting)",
)
def web(enable_http: bool | None = None):
    """Launch the web interface for TexTeller."""
    if enable_http is None:
        enable_http = Globals().enable_http
    if not enable_http:
        click.echo(
            click.style(
                "HTTP/webserver is disabled. Use --enable-http or set TEXTELLER_ENABLE_HTTP=1 to enable.",
                fg="yellow",
            )
        )
        sys.exit(1)

    os.system(f"streamlit run {Path(__file__).parent / 'streamlit_demo.py'}")
