# -*- coding: utf-8 -*-
import io
from urllib.parse import urlparse

from chaoslib.settings import load_settings, save_settings, \
    CHAOSTOOLKIT_CONFIG_PATH
import click
from logzero import logger
import requests
import simplejson as json
from typing import Any, Dict
from urllib3.exceptions import InsecureRequestWarning

from . import __version__
from .api import client_session
from .api.experiment import publish_experiment
from .api.execution import initialize_execution, fetch_execution
from .api.organization import request_orgs
from .api.ssl import verify_ssl_certificate
from .api.team import request_teams
from .api import urls
from .settings import set_settings, get_endpoint_url, get_orgs, \
    verify_tls_certs, enable_safeguards, enable_publishing, \
    disable_safeguards, disable_publishing, get_verify_tls, get_auth_token, \
    get_default_org

__all__ = ["signin", "publish", "org", "enable", "disable", "team"]


@click.group()
@click.version_option(version=__version__)
@click.option('--settings', default=CHAOSTOOLKIT_CONFIG_PATH,
              show_default=True, help="Path to the settings file.")
@click.pass_context
def cli(ctx: click.Context, settings: str = CHAOSTOOLKIT_CONFIG_PATH):
    ctx.obj = {}
    ctx.obj["settings_path"] = click.format_filename(settings)


@cli.command(help="Sign-in with your ChaosIQ credentials")
@click.pass_context
def signin(ctx: click.Context):
    """
    Sign-in to ChaosIQ.
    """
    settings_path = ctx.obj["settings_path"]
    establish_credentials(settings_path)


@cli.command(help="Set ChaosIQ organisation")
@click.pass_context
def org(ctx: click.Context):
    """
    List and select a new ChaosIQ organization and team to use.

    \b
    In order to benefit from these features, you must have registered with
    ChaosIQ and retrieved an access token. You should set that
    token in the configuration file with `chaos signin`.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path) or {}

    url = get_endpoint_url(
        settings, "https://console.chaosiq.io")

    token = get_auth_token(settings, url)
    disable_tls_verify = get_verify_tls(settings)

    if not token:
        establish_credentials(settings_path)
    else:
        default_org = select_organization(url, token, disable_tls_verify)
        click.echo("Using organization '{}'".format(
            click.style(default_org["name"], fg="blue")))
        default_team = select_team(url, token, default_org, disable_tls_verify)

        set_settings(
            url, token, disable_tls_verify, default_org, default_team,
            settings)
        save_settings(settings, settings_path)

        click.echo("ChaosIQ details saved at {}".format(
            settings_path))


@cli.command(help="Set ChaosIQ team")
@click.pass_context
def team(ctx: click.Context):
    """
    List and select a new ChaosIQ team to use within the default organization.

    \b
    In order to benefit from these features, you must have registered with
    ChaosIQ and retrieved an access token. You should set that
    token in the configuration file with `chaos signin`.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path) or {}

    url = get_endpoint_url(
        settings, "https://console.chaosiq.io")

    token = get_auth_token(settings, url)
    disable_tls_verify = get_verify_tls(settings)

    if not token:
        establish_credentials(settings_path)
    else:
        default_org = get_default_org(settings)
        default_team = select_team(url, token, default_org, disable_tls_verify)

        set_settings(
            url, token, disable_tls_verify, default_org, default_team,
            settings)
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
    ChaosIQ and retrieved an access token. You should set that
    token in the configuration file with `chaos signin`.
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


@cli.command(help="Enable a ChaosIQ feature")
@click.argument('feature', type=click.Choice(['safeguards', 'publish']))
@click.pass_context
def enable(ctx: click.Context, feature: str):
    """
    Enable one of the extension's features: `publish` to push experiment
    and executions to ChaosIQ. `safeguards` to validate the
    run is allowed to continue at runtime.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)
    if feature == "safeguards":
        enable_safeguards(settings)
    elif feature == "publish":
        enable_publishing(settings)
    save_settings(settings, settings_path)


@cli.command(help="Disable a ChaosIQ feature")
@click.argument('feature', type=click.Choice(['safeguards', 'publish']))
@click.pass_context
def disable(ctx: click.Context, feature: str):
    """
    Disable one of the extension's features: `publish` which pushes experiment
    and executions to ChaosIQ. `safeguards` which validates the
    run is allowed to continue at runtime.
    """
    settings_path = ctx.obj["settings_path"]
    settings = load_settings(settings_path)
    if feature == "safeguards":
        disable_safeguards(settings)
    elif feature == "publish":
        disable_publishing(settings)
    save_settings(settings, settings_path)


###############################################################################
# Internals
###############################################################################
def establish_credentials(settings_path):
    settings = load_settings(settings_path) or {}

    default_url = get_endpoint_url(
        settings, "https://console.chaosiq.io")

    url = click.prompt(
        click.style("ChaosIQ url", fg='green'),
        type=str, show_default=True, default=default_url)
    url = urlparse(url)
    url = "://".join([url.scheme, url.netloc])

    token = click.prompt(
        click.style("ChaosIQ token", fg='green'),
        type=str, hide_input=True)
    token = token.strip()

    verify_tls = True
    try:
        r = verify_ssl_certificate(url, token)
        if r.status_code == 401:
            click.echo("Your token was not accepted by the server.")
            raise click.Abort()
    except requests.exceptions.SSLError:
        verify_tls = not click.confirm(
            "It looks like the server's TLS certificate cannot be verified. "
            "Do you wish to disable certificate verification for this server?")

    if not verify_tls:  # pragma: no cover
        requests.packages.urllib3.disable_warnings(
            category=InsecureRequestWarning)

    default_org = select_organization(url, token, verify_tls)
    if not default_org:
        click.secho(
            "No default organization selected! Aborting configuration.",
            fg="red")
        return

    default_team = select_team(url, token, default_org, verify_tls)
    if not default_team:
        click.secho(
            "No default team selected! Aborting configuration.",
            fg="red")
        return

    set_settings(url, token, verify_tls, default_org, default_team, settings)
    save_settings(settings, settings_path)

    click.echo("ChaosIQ details saved at {}".format(settings_path))


def select_organization(url: str, token: str, verify_tls: bool = True) -> str:
    """
    Select the organization to use as workspace.
    """
    default_org = None
    orgs_url = urls.org(urls.base(url))
    while True:
        r = request_orgs(orgs_url, token, verify_tls)
        if r is None:
            click.secho(
                "Failed to retrieve organizations from the ChaosIQ services.",
                fg="red")
            break

        if r.status_code in [401, 403]:
            click.secho(
                "Provided credentials are not allowed by ChaosIQ. "
                "Please verify your access token.", fg="red")
            break

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
            "Default organization to use", fg='green'), type=int)
        org_index = org_index - 1
        if -1 < org_index < len(orgs):
            org = orgs[org_index]
            default_org = {"name": org[1], "id": org[0]}
            break
        click.echo("Select a default organization to publish to")

    return default_org


def select_team(url: str, token: str, org: Dict[str, Any],
                verify_tls: bool = True) -> str:
    """
    Select the  team to publish experiments and executions to. Teams are
    selected as part oif the selected organization and only the ones the
    user, identified by the token, is member of.
    """
    default_team = None
    teams_url = urls.team(urls.org(urls.base(url), organization_id=org["id"]))
    while True:
        r = request_teams(teams_url, token, verify_tls)
        if r is None:
            click.secho(
                "Failed to retrieve teams, in organization '{}', from "
                "the ChaosIQ services.".format(org["name"]),
                fg="red")
            break

        if r.status_code in [401, 403]:
            click.secho(
                "Provided credentials are not allowed by ChaosIQ. "
                "Please verify your access token.", fg="red")
            break

        if r.status_code != 200:
            logger.debug(
                "Failed to fetch your teams at {}: {}".format(
                    teams_url, r.text))
            click.echo(
                click.style("Failed to fetch your teams", fg="yellow"))
            break

        teams = r.json()
        if not teams:
            click.echo(
                click.style(
                    "You must be part of at least a team in organization '{}' "
                    "to publish to it.".format(org["name"]), fg="red"))
            break

        if len(teams) == 1:
            default_team = teams[0]
            break
        click.echo(
            "Here are the teams you belong to in organization '{}':".format(
                click.style(org["name"], fg="blue")))
        teams = [(t['id'], t['name']) for t in teams]
        click.echo(
            "\n".join(["{}) {}".format(i+1, t[1]) for (i, t) in enumerate(
                teams)]))

        team_index = click.prompt(click.style(
            "Default team to publish to", fg='green'), type=int)
        team_index = team_index - 1
        if -1 < team_index < len(teams):
            team = teams[team_index]
            default_team = {"name": team[1], "id": team[0]}
            break
        click.echo(click.style("Please, select a valid team.", fg="yellow"))

    if default_team:
        click.echo(
            "Experiments and executions will be published to "
            "team '{}' in organization '{}'".format(
                click.style(default_team['name'], fg='blue'),
                click.style(org['name'], fg='blue')))

    return default_team
