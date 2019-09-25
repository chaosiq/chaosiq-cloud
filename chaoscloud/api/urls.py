from urllib.parse import urlparse

__all__ = ["base", "experiment", "execution", "clean", "safeguard", "host",
           "org", "full"]


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


def safeguard(base_execution_url: str) -> str:
    """
    Build the URL to fetch safeguards from for an execution
    """
    return '/'.join([base_execution_url, 'policies'])


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


def full(base: str, org_id: str, experiment_id: str = None,
         execution_id: str = None, with_experiments: bool = False,
         with_executions: bool = False, with_events: bool = False,
         with_safeguards: bool = False) -> str:
    """
    Build the appropriate url for various resources.

    * `experiment_id` set to `None`  but `with_experiments`  set to `True`
      will give `base/organizations/org_id/experiments`
    * `experiment_id` set
      will give `base/organizations/org_id/experiments/experiment_id`
    * `execution_id` set to `None`  but `with_executions`  set to `True`
      will give `base/organizations/org_id/experiments/experiment_id/executions`
    * `execution_id` set
      will give `base/organizations/org_id/experiments/experiment_id/executions/execution_id`
    * `with_events` set
      will give `base/organizations/org_id/experiments/experiment_id/executions/execution_id/events`
    * `with_safeguards` set
      will give `base/organizations/org_id/policies`
    """  # noqa: E501
    url = org(base, org_id)
    if with_experiments or experiment_id:
        url = experiment(url, experiment_id=experiment_id)
        if with_executions or execution_id:
            url = execution(url, execution_id=execution_id)
            if with_events:
                url = event(url)
    if with_safeguards:
        url = safeguard(url)
    return url
