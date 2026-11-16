import typer
from rich.console import Console
from .engine import analyze, remove_unused_features

app = typer.Typer()
console = Console()

def mb(b: int) -> float:
    return b / (1024 * 1024)

@app.command()
def inspect(path: str):
    console.print(f"Scanning [cyan]{path}[/cyan]")
    try:
        dt, p, issues, sizes, avg, small = analyze(path)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        raise typer.Exit(1)
    console.print(f"Version: {dt.version()}")
    console.print("\n[bold]Protocol Health[/bold]")
    console.print(f"   Reader: {p.min_reader_version} | Writer: {p.min_writer_version}")
    if issues:
        console.print(f"   [yellow]Unused features: {', '.join(issues)}[/yellow]")
    else:
        console.print("   [green]Clean[/green]")
    console.print("\n[bold]Performance Health[/bold]")
    total = sum(sizes)
    console.print(f"   Files: {len(sizes)} | Total: {mb(total):.1f} MB | Avg: {avg/1024/1024:.1f} MB")
    if small > 0:
        console.print(f"   [yellow]Small files (<32MB): {small} ({small/len(sizes)*100:.0f}%)[/yellow]")
    else:
        console.print("   [green]File sizes OK[/green]")
    fixes = []
    if issues:
        fixes.append("Run `delta-doctor fix --remove-unused` to remove unused writer features")
    if small > 0:
        fixes.append("Run `OPTIMIZE` to compact small files")
    if fixes:
        console.print("\n[bold]Recommendations[/bold]")
        for f in fixes:
            console.print(f"   [green]→[/green] {f}")

@app.command()
def fix(path: str, remove_unused: bool = False):
    console.print(f"Fixing [cyan]{path}[/cyan]")
    if not remove_unused:
        console.print("   [dim]Pass --remove-unused to clean protocol features[/dim]")
        return
    try:
        removed = remove_unused_features(path)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        raise typer.Exit(1)
    if removed:
        console.print(f"   [green]Removed: {', '.join(removed)}[/green]")
        console.print("   [dim]Warning: this modifies the Delta log directly. Use with caution.[/dim]")
    else:
        console.print("   [green]Nothing to remove[/green]")

if __name__ == "__main__":
    app()
