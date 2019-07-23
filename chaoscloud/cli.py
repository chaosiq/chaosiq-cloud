# -*- coding: utf-8 -*-
import io
from urllib.parse import urlparse

from chaoslib.settings import load_settings, save_settings, \
    CHAOSTOOLKIT_CONFIG_PATH
import click
from logzero import logger
import requests
import simplejson as json

from . import __version__
from .api import client_session
from .api.experiment import publish_experiment
from .api.execution import initialize_execution, fetch_execution
from .api import urls
from .settings import set_settings, get_endpoint_url, get_orgs, \
    verify_tls_certs, enable_policies, enable_publishing, disable_policies, \
    disable_publishing

__all__ = ["login", "publish"]


@click.group()
@click.version_option(version=__version__)
@click.option('--settings', default=CHAOSTOOLKIT_CONFIG_PATH,
              show_default=True, help="Path to the settings file.")
@click.pass_context
def cli(ctx: click.Context, settings: str = CHAOSTOOLKIT_CONFIG_PATH):
    ctx.obj = {}
    ctx.obj["settings_path"] = click.format_filename(settings)


@cli.command(help="Set the access token to communicate with Chaos Toolkit")
@click.pass_context
def login(ctx: click.Context):
    """
    Login to the Chaos Toolkit Cloud
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path) or {}

    default_url = get_endpoint_url(
        settings, "https://console.chaostoolkit.com")
    url = click.prompt(
        click.style("Chaos Toolkit Cloud url", fg='green'),
        type=str, show_default=True, default=default_url)
    url = urlparse(url)
    url = "://".join([url.scheme, url.netloc])

    token = click.prompt(
        click.style("Chaos Toolkit Cloud token", fg='green'),
        type=str, hide_input=True)
    token = token.strip()

    disable_tls_verify = False
    try:
        r = requests.head(url, headers={
            "Authorization": "Bearer {}".format(token)
        })
        if r.status_code == 401:
            click.echo("Your token was not accepted by the server.")
            raise click.Abort()
    except requests.exceptions.SSLError:
        disable_tls_verify = click.confirm(
            "It looks like the server's TLS certificate cannot be verified. "
            "Do you wish to disable certificate verification for this server?")

    default_org = None
    orgs_url = urls.org(urls.base(url))
    while True:
        r = requests.get(orgs_url, headers={
            "Authorization": "Bearer {}".format(token)
        }, verify=not disable_tls_verify)
        if r.status_code != 200:
            logger.debug(
                "Failed to fetch your organizations at {}: {}".format(
                    orgs_url, r.text))
            click.echo(
                click.style("Failed to fetch your organizations", fg="yellow"))
            break

        orgs = r.json()
        if len(orgs) == 1:
            default_org = orgs[0]
            break
        click.echo("Here are your known organizations:")
        orgs = [(o['id'], o['name']) for o in orgs]
        click.echo(
            "\n".join(["{}) {}".format(i+1, o[1]) for (i, o) in enumerate(
                orgs)]))

        org_index = click.prompt(click.style(
            "Default organization to publish to", fg='green'), type=int)
        org_index = org_index - 1
        if -1 < org_index < len(orgs):
            default_org = orgs[org_index-1]
            break
        click.echo("Select a default organization to publish to")

    if default_org:
        click.echo(
            "Experiments and executions will be published to "
            "organization '{}'".format(
                click.style(default_org['name'], fg='blue')))

    set_settings(url, token, disable_tls_verify, default_org, settings)
    save_settings(settings, settings_path)

    click.echo("Chaos Toolkit Cloud details saved at {}".format(settings_path))


@cli.command(help="Publish your experiment's journal to Chaos Toolkit Cloud")
@click.argument('journal')
@click.pass_context
def publish(ctx: click.Context, journal: str):
    """
    Publish your experiment's findings to Chaos Toolkit Cloud.

    \b
    In order to benefit from these features, you must have registered with
    Chaos Toolkit Cloud and retrieved an access token. You should set that
    token in the configuration file with `chaos login`.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)

    journal_path = journal
    with io.open(journal_path) as f:
        journal = json.load(f)

        organizations = get_orgs(settings)
        url = get_endpoint_url(settings)
        verify_tls = verify_tls_certs(settings)

        experiment = journal.get("experiment")
        with client_session(url, organizations, verify_tls, settings) as s:
            publish_experiment(s, experiment)

            r = fetch_execution(s, journal)
            if not r:
                initialize_execution(s, experiment, journal)
            else:
                logger.info("Execution findings available at {}".format(
                    r.headers["Content-Location"]))


@cli.command(help="Enable a Chaos Toolkit Cloud feature")
@click.argument('feature', type=click.Choice(['policies', 'publish']))
@click.pass_context
def enable(ctx: click.Context, feature: str):
    """
    Enable one of the extension's features: `publish` to push experiment
    and executions to the Chaos Toolkit Cloud. `policies` to validate the
    run is allowed to continue at runtime.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)
    if feature == "policies":
        enable_policies(settings)
    elif feature == "publish":
        enable_publishing(settings)
    save_settings(settings, settings_path)


@cli.command(help="Disable a Chaos Toolkit Cloud feature")
@click.argument('feature', type=click.Choice(['policies', 'publish']))
@click.pass_context
def disable(ctx: click.Context, feature: str):
    """
    Disable one of the extension's features: `publish` which pushes experiment
    and executions to the Chaos Toolkit Cloud. `policies` which validates the
    run is allowed to continue at runtime.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)
    if feature == "policies":
        disable_policies(settings)
    elif feature == "publish":
        disable_publishing(settings)
    save_settings(settings, settings_path)