# chaostoolkit-chaoshub

[![Build Status](https://travis-ci.org/chaosiq/chaosiq-chaostoolkit-plugin.svg?branch=master)](https://travis-ci.org/chaosiq/chaosiq-chaostoolkit-plugin)

The ChaosIQ plugin library for the [Chaos Toolkit][chaostoolkit].

[chaostoolkit]: https://chaostoolkit.org/

## Purpose

The purpose of this library is to communication with [ChaosIQ][] from the
Chaos Toolkit

[chaosiq]: https://chaosiq.io

## Install

Install this package as any other Python packages:

```
$ pip install -U chaosiq-chaostoolkit-plugin
```

Notice that this draws a few [dependencies][deps]:

[deps]: https://github.com/cchaosiq/chaosiq-chaostoolkit-plugin/blob/master/requirements.txt


## Usage

Once installed, `login` and `publish` subommands will be made available to
the new `chaosiq` command. You can use them as follows:

```
$ chaosiq login
```

```
$ chaos publish journal.json
```

The `login` sets the access token you generated from ChaosIQ to communicate
with its services.

The `publish` command enables you to manually push your experimental 
findings, typically recorded in the `journal.json`, to your ChaosIQ account.

By default, once you have logged into your ChaosIQ your experiment's findings
will be automatically pushed to ChaosIQ when you execute 
`chaos run`. You can turn this behaviour off by specifying `--no-publish`
as shown here:

```
$ chaos run experiment.json --no-publish
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
