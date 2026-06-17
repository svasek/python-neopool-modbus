# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0](https://github.com/svasek/python-neopool-modbus/compare/v3.1.3...v3.2.0) (2026-06-17)


### ✨ Features

* ✨ tier-2 register types and decoders ([#25](https://github.com/svasek/python-neopool-modbus/issues/25)) ([782619d](https://github.com/svasek/python-neopool-modbus/commit/782619df3e68d9e4e1663b9273222ea418ddfc72))

## [3.1.3](https://github.com/svasek/python-neopool-modbus/compare/v3.1.2...v3.1.3) (2026-06-17)


### 🐛 Bug Fixes

* **client:** 🩹 rename MBF_CELL_RUNTIME* combined keys to CELL_RUNTIME_* ([932e5ff](https://github.com/svasek/python-neopool-modbus/commit/932e5ffdb5b4f5e782d0b1ed35839dc84263f49b))

## [3.1.2](https://github.com/svasek/python-neopool-modbus/compare/v3.1.1...v3.1.2) (2026-06-17)


### 🐛 Bug Fixes

* **client:** 🩹 async_sync_device_time takes a unix timestamp ([08cadb5](https://github.com/svasek/python-neopool-modbus/commit/08cadb538abd1bd671298677fbe7f7e4af1a8c97))

## [3.1.1](https://github.com/svasek/python-neopool-modbus/compare/v3.1.0...v3.1.1) (2026-06-17)


### 🐛 Bug Fixes

* **decoders:** 🩹 rename cell-boost mode "active_with_redox" to "active_redox" ([fd73a95](https://github.com/svasek/python-neopool-modbus/commit/fd73a9512fbf201bef70269342ebc67f50f0ead6))

## [3.1.0](https://github.com/svasek/python-neopool-modbus/compare/v3.0.0...v3.1.0) (2026-06-17)


### ✨ Features

* **decoders:** ✨ rename get_filtration_speed to compute_filtration_speed_state ([#20](https://github.com/svasek/python-neopool-modbus/issues/20)) ([414b7ba](https://github.com/svasek/python-neopool-modbus/commit/414b7bae15f53675413fdfe03c4fb0e1d8a2f65e))

## [3.0.0](https://github.com/svasek/python-neopool-modbus/compare/v2.2.0...v3.0.0) (2026-06-17)


### ⚠ BREAKING CHANGES

* `async_read_all()` returns 32-bit register pairs as single combined keys instead of the `_LOW`/`_HIGH` halves.

### ✨ Features

* ✨ tier-1 extraction of integration logic into the library ([#18](https://github.com/svasek/python-neopool-modbus/issues/18)) ([94f2934](https://github.com/svasek/python-neopool-modbus/commit/94f293458fb8acdd2a5d2fe5d87691bec0396730))

## [2.2.0](https://github.com/svasek/python-neopool-modbus/compare/v2.1.1...v2.2.0) (2026-06-16)


### ✨ Features

* **api:** ✨ accept unit_id config key (with slave_id fallback) ([#16](https://github.com/svasek/python-neopool-modbus/issues/16)) ([ea720ec](https://github.com/svasek/python-neopool-modbus/commit/ea720ec8d402b1feec260bdb0595dff3410da9dd))

## [2.1.1](https://github.com/svasek/python-neopool-modbus/compare/v2.1.0...v2.1.1) (2026-06-14)


### 🐛 Bug Fixes

* 🩹 relax pymodbus upper bound for HA core hassfest ([c9d9133](https://github.com/svasek/python-neopool-modbus/commit/c9d9133d3d4cb057a14e3513f9c6b91688c3a557))

## [2.1.0](https://github.com/svasek/python-neopool-modbus/compare/v2.0.1...v2.1.0) (2026-06-13)


### ✨ Features

* **client:** ✨ add public async_read_register API ([#13](https://github.com/svasek/python-neopool-modbus/issues/13)) ([1dc6af1](https://github.com/svasek/python-neopool-modbus/commit/1dc6af10cc64cdb804d03886fd455fc896c0c959))
* **registers:** ✨ expand COMMAND_REGISTERS with 4 auto-clearing commands ([#12](https://github.com/svasek/python-neopool-modbus/issues/12)) ([a95de93](https://github.com/svasek/python-neopool-modbus/commit/a95de934754a32a84200e514cb5293d67b8b2580))

## [2.0.1](https://github.com/svasek/python-neopool-modbus/compare/v2.0.0...v2.0.1) (2026-06-10)


### 🐛 Bug Fixes

* **client:** 🐛 suppress verification warning for MBF_ACTION_COPY_TO_RTC ([#9](https://github.com/svasek/python-neopool-modbus/issues/9)) ([a0c16e9](https://github.com/svasek/python-neopool-modbus/commit/a0c16e97c282cd846aaa1d5982a056210a32b9f7))


### ♻️ Refactoring

* ♻️ adopt mypy strict alongside basedpyright ([#11](https://github.com/svasek/python-neopool-modbus/issues/11)) ([21e6f41](https://github.com/svasek/python-neopool-modbus/commit/21e6f41437a52a2bd22d97156d6c02a45aa2f025))

## [2.0.0](https://github.com/Svasek/python-neopool-modbus/compare/v1.1.0...v2.0.0) (2026-06-07)


### ⚠ BREAKING CHANGES

* callers that caught pymodbus.ConnectionException / pymodbus.ModbusException must catch NeoPoolError (or a subclass) instead.

### ✨ Features

* 💥 raise NeoPool*Error subclasses on every failure path ([#3](https://github.com/Svasek/python-neopool-modbus/issues/3)) ([f026d69](https://github.com/Svasek/python-neopool-modbus/commit/f026d69efc814e3f1ed560325f5a81dacba6ca84))

## [1.1.0](https://github.com/Svasek/python-neopool-modbus/compare/v1.0.0...v1.1.0) (2026-06-06)


### ✨ Features

* ✨ add async_probe_serial for one-shot device discovery ([#4](https://github.com/Svasek/python-neopool-modbus/issues/4)) ([29995b8](https://github.com/Svasek/python-neopool-modbus/commit/29995b8136d5de741220bd3259a4ed1ca669fc56))

## [1.0.0](https://github.com/Svasek/python-neopool-modbus/compare/v0.2.0...v1.0.0) (2026-06-06)


### ⚠ BREAKING CHANGES

* async_write_aux_relay() now raises ValueError when relay_index is outside 1-4, where the previous version returned None and logged an error. Callers that relied on the silent no-op must validate the index themselves or wrap the call in a try/except.
* PERIOD_MAP and PERIOD_SECONDS_TO_KEY have been removed from neopool_modbus.registers. They were only meaningful to the Home Assistant integration's `select` entity and live in custom_components/neopool/const.py from v4.0.0 onwards. Library consumers that imported either dict must inline the mapping themselves.

### ✨ Features

* 💥 raise ValueError on invalid AUX relay index ([269b7df](https://github.com/Svasek/python-neopool-modbus/commit/269b7df600471003f8bca15d9a60f7e3a3033579))
* 💥 remove PERIOD_MAP / PERIOD_SECONDS_TO_KEY, mark library Production/Stable ([827fe3d](https://github.com/Svasek/python-neopool-modbus/commit/827fe3d9b6699234ac6fdb0cea3ef751f451e4cb))


### 🐛 Bug Fixes

* 🩹 grant publish-pypi job contents:write for asset upload ([cd48aed](https://github.com/Svasek/python-neopool-modbus/commit/cd48aedc6e23773f2dc8ad2017919e7390ca85ee))
* **client:** 🐛 fall through to device read when timer cache is incomplete ([c5268ad](https://github.com/Svasek/python-neopool-modbus/commit/c5268ad74240ad7ce8312ac2e8b6106dd9e94d1d))
* **client:** 🐛 move get_client() and total_writes bump into _perform_write_timer try block ([e261f47](https://github.com/Svasek/python-neopool-modbus/commit/e261f473c15fb7f0dd8d62f19f48755585322153))
* **client:** 🐛 verify isError() on EEPROM save and EXEC after timer write ([488e8c5](https://github.com/Svasek/python-neopool-modbus/commit/488e8c544cf822e277a5fb9bc19e11dd9b877526))
* **client:** 🐛 verify isError() on every AUX relay write ([d5598f4](https://github.com/Svasek/python-neopool-modbus/commit/d5598f42c65856515a4fa02e2327d34ec4a60676))


### ♻️ Refactoring

* ♻️ collapse aux relay set/clear if-else into ternary ([aff22fa](https://github.com/Svasek/python-neopool-modbus/commit/aff22fa19df400fced0da4dd538447053df24c30))


### 🎨 Style

* 🎨 collapse one-statement raise to single line ([974e709](https://github.com/Svasek/python-neopool-modbus/commit/974e709de10bb838863edd84549caf13ebe3be7a))
* 💄 fix lint findings in test files (B/RUF/SIM) ([25c743c](https://github.com/Svasek/python-neopool-modbus/commit/25c743ca414aecaff080c3c89d3253501db202fb))
* 💄 replace ambiguous unicode dashes with ASCII hyphens ([8fbbc38](https://github.com/Svasek/python-neopool-modbus/commit/8fbbc384a1fdf65404cee4d5a5246b4978ff1653))

## [0.2.0](https://github.com/Svasek/python-neopool-modbus/compare/v0.1.0...v0.2.0) (2026-06-06)


### ✨ Features

* ✨ add decoders module ([6c69762](https://github.com/Svasek/python-neopool-modbus/commit/6c6976269c31dc8c82937a8bc323045917c55599))
* ✨ add registers module ([37ac24c](https://github.com/Svasek/python-neopool-modbus/commit/37ac24cd33101ad50e506cc0d113619113bae1fc))
* ✨ add status_mask module ([211bf66](https://github.com/Svasek/python-neopool-modbus/commit/211bf660b29b346a1a701f280c7868d636f7a827))
* ✨ define public exception hierarchy and module API ([d17d9a6](https://github.com/Svasek/python-neopool-modbus/commit/d17d9a67d03b431487bebcd52869a81a78080f87))
* ✨ port NeoPoolModbusClient to library ([d130527](https://github.com/Svasek/python-neopool-modbus/commit/d1305273b4ade760b912f45e86f75645b66e3cd2))


### 🐛 Bug Fixes

* 🩹 remove unsupported `//` comment from pyrightconfig.json ([504efcb](https://github.com/Svasek/python-neopool-modbus/commit/504efcba31dc6f033c1ad0721c2f4c6d975c9a58))


### 🎨 Style

* 🎨 reflow long lines after modbus_acall inlining ([6fdc344](https://github.com/Svasek/python-neopool-modbus/commit/6fdc344d87f789c011ab44549a68130ad4af2f5a))

## [Unreleased]

### Added

- Initial public API — `NeoPoolModbusClient`, register address constants, exceptions.
- Extracted from the Home Assistant `neopool` integration.
