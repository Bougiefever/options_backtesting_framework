import click


@click.group()
def main():
    """Main command group."""
    pass


@main.group()
def config():
    """Configuration command group."""
    pass


@config.command()
def show():
    """Show configuration command."""
    click.echo("Showing configuration...")


@main.group()
def backtest():
    """Backtest command group."""
    pass


@backtest.command()
def butterfly():
    """Butterfly backtest command."""
    click.echo("Running butterfly backtest...")


@backtest.command()
def vertical():
    """Vertical backtest command."""
    click.echo("Running vertical backtest...")
