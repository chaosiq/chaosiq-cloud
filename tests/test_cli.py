from tempfile import NamedTemporaryFile
from unittest.mock import patch

from chaoslib.settings import load_settings
from click.testing import CliRunner
import requests_mock

from chaoscloud.cli import cli


@patch('chaoscloud.cli.signin', spec=True)
def test_signin(signin):
    url = 'https://console.chaos-awesome-toolkit.com'
    token = 'XYZ'
    selected_org_index = '2'
    selected_team_index = '1'

    inputs = '\n'.join([
        url,
        token,
        selected_org_index,
        selected_team_index
    ])

    with requests_mock.mock() as m:
        m.head(url)
        m.get("{}/api/v1/organizations".format(url), json=[
            {
                "id": "abc",
                "name": "myorg"
            },
            {
                "id": "tyu",
                "name": "otherorg"
            }
        ])

        m.get("{}/api/v1/organizations/tyu/teams".format(url), json=[
            {
                "id": "123",
                "name": "myteam"
            },
            {
                "id": "456",
                "name": "otherteam"
            }
        ])

        runner = CliRunner()
        with NamedTemporaryFile(suffix="yaml") as settings:
            result = runner.invoke(
                cli, ["--settings", settings.name, "signin"], input=inputs)

            assert result.exit_code == 0
            assert result.exception is None

            settings.seek(0)
            settings = load_settings(settings.name)

            assert 'console.chaos-awesome-toolkit.com' in settings["auths"]
            auth = settings["auths"]['console.chaos-awesome-toolkit.com']
            assert auth["type"] == "bearer"
            assert auth["value"] == "XYZ"

            assert "provider" in settings["controls"]["chaosiq-cloud"]
            provider = settings["controls"]["chaosiq-cloud"]["provider"]
            assert provider["module"] == "chaoscloud.controls"
            assert provider["type"] == "python"
            assert len(provider["arguments"]["organizations"]) == 1

            org = provider["arguments"]["organizations"][0]
            assert org["default"] is True
            assert org["id"] == "tyu"
            assert org["name"] == "otherorg"
            assert org["teams"] == [{
                "id": "123",
                "name": "myteam",
                "default": True
            }]


@patch('chaoscloud.cli.org', spec=True)
def test_org(org):
    url = 'https://console.chaos-awesome-toolkit.com'
    token = 'XYZ'

    with requests_mock.mock() as m:
        m.head(url)
        m.get("{}/api/v1/organizations".format(url), json=[
            {
                "id": "abc",
                "name": "myorg"
            },
            {
                "id": "tyu",
                "name": "otherorg"
            }
        ])

        m.get("{}/api/v1/organizations/tyu/teams".format(url), json=[
            {
                "id": "123",
                "name": "myteam"
            },
            {
                "id": "456",
                "name": "otherteam"
            }
        ])

        runner = CliRunner()
        with NamedTemporaryFile(suffix="yaml") as settings_file:

            use_org_selected_org_index = '2'
            selected_team_index = '1'
            use_org_inputs = '\n'.join([
                url,
                token,
                use_org_selected_org_index,
                selected_team_index
            ])

            result = runner.invoke(
                cli, ["--settings", settings_file.name, "org"],
                input=use_org_inputs)

            assert result.exit_code == 0
            assert result.exception is None

            settings_file.seek(0)
            settings = load_settings(settings_file.name)

            assert 'console.chaos-awesome-toolkit.com' in settings["auths"]
            auth = settings["auths"]['console.chaos-awesome-toolkit.com']
            assert auth["type"] == "bearer"
            assert auth["value"] == "XYZ"

            assert "provider" in settings["controls"]["chaosiq-cloud"]
            provider = settings["controls"]["chaosiq-cloud"]["provider"]
            assert provider["module"] == "chaoscloud.controls"
            assert provider["type"] == "python"
            assert len(provider["arguments"]["organizations"]) == 1

            orgs = provider["arguments"]["organizations"][0]
            assert orgs["id"] == "tyu"
            assert orgs["name"] == "otherorg"
            assert orgs["teams"] == [{
                "id": "123",
                "name": "myteam",
                "default": True
            }]
