# Chaos Toolkit Cloud extension for the Chaos Toolkit

[![Build Status](https://travis-ci.com/chaosiq/chaostoolkit-cloud.svg?branch=master)](https://travis-ci.com/chaosiq/chaostoolkit-cloud)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-cloud.svg)](https://www.python.org/)
[![Has wheel](https://img.shields.io/pypi/wheel/chaostoolkit-cloud.svg)](http://pythonwheels.com/)

This is the Chaos Toolkit Cloud extension package for the [Chaos Toolkit][chaostoolkit].

[chaostoolkit]: https://chaostoolkit.com/

## Purpose

The purpose of this package is to communicate with [Chaos Toolkit Cloud][ctk] in
order to:

* Publish experiments
* Publish executions of these experiments
* Control the execution via a set of controls

[ctk]: https://chaostoolkit.com/

## Install

Install this package as any other Python packages:

```
$ pip install -U chaostoolkit-cloud
```

## Usage

Once installed, `login`, `publish`, `enable` and `disable` will be added
to the `chaos` command.

```console
$ chaos
Usage: chaos [OPTIONS] COMMAND [ARGS]...

Options:
  --version           Show the version and exit.
  --verbose           Display debug level traces.
  --no-version-check  Do not search for an updated version of the
                      chaostoolkit.
  --change-dir TEXT   Change directory before running experiment.
  --no-log-file       Disable logging to file entirely.
  --log-file TEXT     File path where to write the command's log.  [default:
                      chaostoolkit.log]
  --settings TEXT     Path to the settings file.  [default:
                      /home/sylvain/.chaostoolkit/settings.yaml]
  --help              Show this message and exit.

Commands:
  disable   Disable a Chaos Toolkit's extension client feature
  discover  Discover capabilities and experiments.
  enable    Enable a Chaos Toolkit's extension client feature
  info      Display information about the Chaos Toolkit environment.
  init      Initialize a new experiment from discovered capabilities.
  login     Set the access token to communicate with Chaos Toolkit
  run       Run the experiment loaded from SOURCE, either a local file or a...
  validate  Validate the experiment at PATH.
```

### Login with the Chaos Toolkit

In order to work, you first need to authenticate with your account on the
[Chaos Toolkit Cloud][ctk]. First, go there and generate a new token. Copy that
token and paste it when asked from the next command:


```
$ chaos login
Chaos Toolkit Cloud url [https://console.chaostoolkit.com]: 
Chaos Toolkit Cloud token: 
Experiments and executions will be published to organization 'MyName'
Chaos Toolkit Cloud details saved at ~/.chaostoolkit/settings.yaml
```

This is now ready to be used.

### Publish experiments and executions as you run

Once this extension is installed, it starts transmitting the experiments
and their executions to the [Chaos Toolkit Cloud][ctk] in your account.

```
$ chaos run test.json
[2019-07-01 14:49:40 INFO] Validating the experiment's syntax
[2019-07-01 14:49:40 INFO] Experiment looks valid
[2019-07-01 14:49:40 INFO] Running experiment: Look token in file
[2019-07-01 14:49:40 INFO] Execution available at https://console.chaostoolkit.com/MyName/experiments/fc36eb45-4718-4c4a-a50e-503552116cf3/executions/c07afe83-b590-486f-b149-de3d6de7e155
[2019-07-01 14:49:40 INFO] Steady state hypothesis: Our hypothesis is tour token is part of the file
[2019-07-01 14:49:41 INFO] Probe: grep-file
[2019-07-01 14:49:41 INFO] Steady state hypothesis is met!
[2019-07-01 14:49:41 INFO] Action: remove-token
[2019-07-01 14:49:41 INFO] Steady state hypothesis: Our hypothesis is tour roken is part of the file
[2019-07-01 14:49:41 INFO] Probe: grep-file
[2019-07-01 14:49:42 INFO] Steady state hypothesis is met!
[2019-07-01 14:49:42 INFO] Let's rollback...
[2019-07-01 14:49:42 INFO] Rollback: remove-token
[2019-07-01 14:49:42 INFO] Action: remove-token
[2019-07-01 14:49:42 INFO] Experiment ended with status: completed
```

### Publish existing execution

The `publish` command enables you to manually push your experimental 
findings, typically recorded in the `journal.json`, to your Chaos Toolkit
account.

### Disable policies checking

During development time of your experiment, you may wish to disable checking
for policies as they can slow your work down. They aren't always relevant
either. To disable the extension from requesting if the execution is allowed
to carry on:

```console
$ chaos disable policies
```

Obviously, run the mirroring command to enable them back:

```console
$ chaos enable policies
```

### Disable publishing experiments and executions

If you need to disable publishing for a little whie

```console
$ chaos disable publish
```

Note, when you disable publishing, you essentialy disable the entire extension.

Obviously, run the mirroring command to enable publishing again:

```console
$ chaos enable publish
```

## Contribute

Contributors to this project are welcome as this is an open-source effort that
seeks [discussions][join] and continuous improvement.

[join]: https://join.chaostoolkit.org/

From a code perspective, if you wish to contribute, you will need to run a 
Python 3.5+ environment. Then, fork this repository and submit a PR. The
project cares for code readability and checks the code style to match best
practices defined in [PEP8][pep8]. Please also make sure you provide tests
whenever you submit a PR so we keep the code reliable.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

### Develop

If you wish to develop on this project, make sure to install the development
dependencies. But first, [create a virtual environment][venv] and then install
those dependencies.

[venv]: http://chaostoolkit.org/reference/usage/install/#create-a-virtual-environment

```console
$ pip install -r requirements-dev.txt -r requirements.txt
```

Then, point your environment to this directory:

```console
$ pip install -e .
```

Now, you can edit the files and they will be automatically be seen by your
environment, even when running from the `chaos` command locally.

### Test

To run the tests for the project execute the following:

```
$ pytest
```
