# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/chaosiq/chaosiq-cloud/compare/0.12.0...HEAD

## [0.12.0][] - 2020-09-07

[0.12.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.11.0...0.12.0

### Changed

-   Moved to implement the verification mainloop using the new ChaosToolkit
    library's event interface. [#70][70]

[70]: https://github.com/chaosiq/chaosiq-cloud/issues/70

## [0.11.0][] - 2020-08-17

[0.11.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.10.2...0.11.0

### Changed

-   Pinning chaostoolkit dependency as its internals will change in the next
    release with [chaostoolkit-lib#172][chaostoolkit-lib#172] and likely break our plugin

[chaostoolkit-lib#172]: https://github.com/chaostoolkit/chaostoolkit-lib/pull/172

## [0.10.2][] - 2020-05-05

[0.10.2]: https://github.com/chaosiq/chaosiq-cloud/compare/0.10.1...0.10.2

### Changed

-   Now terminates a verification on user interruption as soon as the signal
    is received; does not wait for the next frequency.

## [0.10.1][] - 2020-04-30

[0.10.1]: https://github.com/chaosiq/chaosiq-cloud/compare/0.10.0...0.10.1

### Added

-   New `--no-verify-tls` flag to `chaos verify` command

## [0.10.0][] - 2020-03-05

[0.10.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.5...0.10.0

### Changed

-  Add prometheus greater/lower tolerances

## [0.9.5][] - 2020-03-05

[0.9.5]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.4...0.9.5

### Changed

-  Set journal status as verification status

## [0.9.4][] - 2020-02-27

[0.9.4]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.3...0.9.4

### Changed

-  Set the execution state when the run has completed successfully [#59][59]

[59]: https://github.com/chaosiq/chaosiq-cloud/issues/59

[27]: https://github.com/chaosiq/chaosiq-cloud/issues/27

## [0.9.3][] - 2020-02-26

[0.9.3]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.2...0.9.3

### Changed

-  Do not override default team id when none is found in the experiment

## [0.9.2][] - 2020-02-26

[0.9.2]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.1...0.9.2

### Changed

-  Use default selected team when none found in the verification file

## [0.9.1][] - 2020-02-26

[0.9.1]: https://github.com/chaosiq/chaosiq-cloud/compare/0.9.0...0.9.1

### Changed

-  Support the new verification URL scheme

## [0.9.0][] - 2020-02-26

[0.9.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.8.0...0.9.0

### Added

-  Send events during verification run

## [0.8.0][] - 2020-02-17

[0.8.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.7.1...0.8.0

### Added

- Added first tolerances
- Added first probes

## [0.7.1][] - 2020-02-05

[0.7.1]: https://github.com/chaosiq/chaosiq-cloud/compare/0.7.0...0.7.1

### Changed

- Included the `chaoscloud.verify` package.

[verification]: https://chaosiq.io/resources/chaos-engineering/from-chaos-to-verification

## [0.7.0][] - 2020-02-05

[0.7.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.6.0...0.7.0

### Added

- The `verify` command for running a [system verification][verification]. [#34][34]

[verification]: https://chaosiq.io/resources/chaos-engineering/from-chaos-to-verification

## [0.6.0][] - 2020-01-15

[0.6.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.5.0...0.6.0

### Added

- Generate a `".chaosiq"` workspace file for registering experiment IDs
  related to their local file names. [#30][30]

### Changed

- Adapted to use the organization/team schema of the remote API [#27][27]
- Fixed: features were reset to default value when updating settings [#31][31]

[27]: https://github.com/chaosiq/chaosiq-cloud/issues/27
[30]: https://github.com/chaosiq/chaosiq-cloud/issues/30
[31]: https://github.com/chaosiq/chaosiq-cloud/issues/31

## [0.5.0][] - 2019-11-26

[0.5.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.4.1...0.5.0

### Added

- Store the experiment and execution identifiers in the journal as an extension
  named `"chaosiq"` so that they can used later on.
- Store the safeguards that interrupted an execution into the `"chaosiq"`
  extension of the journal [#22][22]
- More graceful bail when certificate verification fails

[22]: https://github.com/chaosiq/chaosiq-cloud/issues/22

## [0.4.1][] - 2019-09-29

[0.4.1]: https://github.com/chaosiq/chaosiq-cloud/compare/0.4.0...0.4.1

### Changed

- Defaulting to UTC when no local timezone could be found

## [0.4.0][] - 2019-09-27

[0.4.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.3.0...0.4.0

### Changed

- A little more robust to failure to fetch organizations
- Catch SIGTERM to interrupt execution gracefully

## [0.3.0][] - 2019-09-25

[0.3.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.2.0...0.3.0

### Changed

- Renamed package to `chaosiq-cloud` to align with the product

## [0.2.0][] - 2019-07-26

[0.2.0]: https://github.com/chaosiq/chaosiq-cloud/compare/0.1.0...0.2.0

### Added

-   [Renamed `login` to `signin`](https://github.com/chaosiq/chaosiq-cloud/issues/10)
-   [Add `org` command to switch default organisation](https://github.com/chaosiq/chaosiq-cloud/issues/11)

## [0.1.0][] - 2019-07-24

[0.1.0]: https://github.com/chaosiq/chaosiq-cloud/tree/0.1.0

### Added

-   Initial release