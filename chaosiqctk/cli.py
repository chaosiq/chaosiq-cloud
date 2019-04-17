# -*- coding: utf-8 -*-
import io

from chaoslib.settings import load_settings, save_settings, \
    CHAOSTOOLKIT_CONFIG_PATH
import click
import simplejson as json

from . import get_context, __version__
from .publish import publish as _publish
from .settings import set_settings

__all__ = ["login", "publish"]


@click.group()
@click.version_option(version=__version__)
@click.option('--settings', default=CHAOSTOOLKIT_CONFIG_PATH,
              show_default=True, help="Path to the settings file.")
@click.pass_context
def cli(ctx: click.Context, settings: str = CHAOSTOOLKIT_CONFIG_PATH):
    ctx.obj = {}
    ctx.obj["settings_path"] = click.format_filename(settings)


@cli.command(help="Set the access token to communicate with ChaosIQ")
@click.pass_context
def login(ctx: click.Context):
    """
    Login twith ChaosIQ
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path) or {}

    url = click.prompt(
        click.style("ChaosIQ url", fg='green'), type=str, show_default=True,
        default="https://chaosiq.io")

    token = click.prompt(
        click.style("ChaosIQ token", fg='green'), type=str, hide_input=True)

    set_settings(url, token, settings)
    save_settings(settings, settings_path)

    click.echo("ChaosIQ details saved at {}".format(
        settings_path))


@cli.command(help="Publish your experiment's journal to ChaosIQ")
@click.argument('journal')
@click.pass_context
def publish(ctx: click.Context, journal: str):
    """
    Publish your experiment's findings to ChaosIQ.

    \b
    In order to benefit from these features, you must have registered with
    ChaosIQ and retrieved an access token. You should set that token in the
    configuration file with `chaosiq login`.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)

    journal_path = journal
    with io.open(journal_path) as f:
        journal = json.load(f)
        experiment = journal.get("experiment")
        context = get_context(experiment, None, settings)
        _publish(context, journal_path, journal)
