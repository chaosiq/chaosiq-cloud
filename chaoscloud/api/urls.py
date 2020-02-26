from urllib.parse import urlparse

__all__ = ["base", "experiment", "execution", "clean", "safeguard", "host",
           "org", "full", "team", "verification", "verification_run",
           "verification_run_events"]


def base(base_url: str) -> str:
    """
    Build the base URL of our API endpoint
    """
    return '/'.join([base_url, 'api', 'v1'])


def experiment(base_url: str, experiment_id: str = None) -> str:
    """
    Build the URL for an experiment to be published to.
    """
    if not experiment_id:
        return '/'.join([base_url, 'experiments'])
    return '/'.join([base_url, 'experiments', experiment_id])


def execution(base_url: str, execution_id: str = None) -> str:
    """
    Build the URL for a journal to be pushed to.
    """
    if not execution_id:
        return '/'.join([base_url, 'executions'])
    return '/'.join([base_url, 'executions', execution_id])


def event(base_url: str) -> str:
    """
    Build the URL for an execution's event.
    """
    return '/'.join([base_url, 'events'])


def org(base_url: str, organization_id: str = None) -> str:
    """
    Build the URL to access organizations
    """
    if not organization_id:
        return '/'.join([base_url, 'organizations'])
    return '/'.join([base_url, 'organizations', organization_id])


def team(base_url: str, team_id: str = None) -> str:
    """
    Build the URL to access teams in an organization
    """
    if not team_id:
        return '/'.join([base_url, 'teams'])
    return '/'.join([base_url, 'teams', team_id])


def safeguard(base_execution_url: str) -> str:
    """
    Build the URL to fetch safeguards from for an execution
    """
    return '/'.join([base_execution_url, 'policies'])


def verification(base_url: str, verification_id: str = None) -> str:
    """
    Build the URL to communicate with the verification API.
    """
    if not verification_id:
        return '/'.join([base_url, 'verifications'])
    return '/'.join([base_url, 'verifications', verification_id])


def verification_run(base_verification_url: str,
                     verification_run_id: str = None) -> str:
    """
    Build the URL to communicate with the verification run API.
    """
    if not verification_run_id:
        return '/'.join([base_verification_url, 'runs'])
    return '/'.join([base_verification_url, 'runs', verification_run_id])


def verification_run_events(base_verification_run_url: str) -> str:
    """
    Build the URL to communicate with the verification run event API.
    """
    return '/'.join([base_verification_run_url, 'events'])


def clean(url: str) -> str:
    """
    Transforms the actual resource URL to something users can go fetch.

    This should be fixed in the server itself at some point.
    """
    return url.replace("/api/", "/")


def host(url: str) -> str:
    """
    Get the host address of the URL
    """
    return urlparse(url).netloc


def full(base: str, org_id: str, team_id: str, experiment_id: str = None,
         execution_id: str = None, verification_id: str = None,
         verification_run_id: str = None,
         with_experiments: bool = False,
         with_executions: bool = False, with_events: bool = False,
         with_safeguards: bool = False, with_verifications: bool = False,
         with_verification_runs: bool = False,
         with_verification_run_events: bool = False) -> str:
    """
    Build the appropriate url for various resources.

    * `experiment_id` set to `None`  but `with_experiments`  set to `True`
      will give `base/organizations/org_id/teams/team_id/experiments`
    * `experiment_id` set
      will give `base/organizations/org_id/teams/team_id/experiments/experiment_id`
    * `execution_id` set to `None`  but `with_executions`  set to `True`
      will give `base/organizations/org_id/teams/team_id/experiments/experiment_id/executions`
    * `execution_id` set
      will give `base/organizations/org_id/teams/team_id/experiments/experiment_id/executions/execution_id`
    * `with_events` set
      will give `base/organizations/org_id/teams/team_id/experiments/experiment_id/executions/execution_id/events`
    * `with_safeguards` set
      will give `base/organizations/org_id/teams/team_id/policies`
    * `verification_id` set to `None`  but `with_verifications`  set to `True`
      will give `base/organizations/org_id/teams/team_id/verifications`
    * `verification_id` set
      will give `base/organizations/org_id/teams/team_id/verifications/verification_id`
    * `verification_run_id` set to `None`  but `with_verification_runs`  set to `True`
      will give `base/organizations/org_id/teams/team_id/verifications/verification_id/runs`
    * `verification_run_id` set
      will give `base/organizations/org_id/teams/team_id/verifications/verification_id/runs/verification_run_id`
    * `with_verification_run_events` set to `True`
      will give `base/organizations/org_id/teams/team_id/verifications/verification_id/runs/verification_run_id/events`
    """  # noqa: E501
    url = team(org(base, org_id), team_id)
    if with_experiments or experiment_id:
        url = experiment(url, experiment_id=experiment_id)
        if with_executions or execution_id:
            url = execution(url, execution_id=execution_id)
            if with_events:
                url = event(url)
    if with_safeguards:
        url = safeguard(url)
    if with_verifications or verification_id:
        url = verification(url, verification_id=verification_id)
        if with_verification_runs or verification_run_id:
            url = verification_run(
                url, verification_run_id=verification_run_id)
            if with_verification_run_events:
                url = verification_run_events(url)
    return url
