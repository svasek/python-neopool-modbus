# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.6.0](https://github.com/svasek/python-neopool-modbus/compare/v4.5.3...v4.6.0) (2026-08-27)


### ✨ Features

* **decoders:** ✨ add public decode_masked_flag helper ([#66](https://github.com/svasek/python-neopool-modbus/issues/66)) ([b039b0a](https://github.com/svasek/python-neopool-modbus/commit/b039b0abe2e8a7ffeaad49bad8e1176650c49c3c))

## [4.5.3](https://github.com/svasek/python-neopool-modbus/compare/v4.5.2...v4.5.3) (2026-08-26)


### 🐛 Bug Fixes

* **client:** 🐛 raise on rejected write instead of returning None ([#64](https://github.com/svasek/python-neopool-modbus/issues/64)) ([775d9e8](https://github.com/svasek/python-neopool-modbus/commit/775d9e8a1b5980e414247a681833f6f3674eea74))

## [4.5.2](https://github.com/svasek/python-neopool-modbus/compare/v4.5.1...v4.5.2) (2026-08-25)


### 🐛 Bug Fixes

* **client:** 🐛 write RMW results back into the register cache ([#62](https://github.com/svasek/python-neopool-modbus/issues/62)) ([8489cb4](https://github.com/svasek/python-neopool-modbus/commit/8489cb4432342bdd4d8823fcbaff41ca6f243017))

## [4.5.1](https://github.com/svasek/python-neopool-modbus/compare/v4.5.0...v4.5.1) (2026-07-23)


### 🐛 Bug Fixes

* **client:** 🐛 guard backwash against auto mode and align filtvalve API with relays ([#58](https://github.com/svasek/python-neopool-modbus/issues/58)) ([8109819](https://github.com/svasek/python-neopool-modbus/commit/81098195c6cf45413ac9b3de7c6636febf9545ae))

## [4.5.0](https://github.com/svasek/python-neopool-modbus/compare/v4.4.0...v4.5.0) (2026-07-23)


### ✨ Features

* **client:** ✨ add async_stop_backwash and skip verify for countdown registers ([#56](https://github.com/svasek/python-neopool-modbus/issues/56)) ([0d6e4d9](https://github.com/svasek/python-neopool-modbus/commit/0d6e4d91411dacbf42bff00abf8affc651ec350f))

## [4.4.0](https://github.com/svasek/python-neopool-modbus/compare/v4.3.1...v4.4.0) (2026-07-23)


### ✨ Features

* **client:** ✨ add async_start_backwash via FILTVALVE registers ([#54](https://github.com/svasek/python-neopool-modbus/issues/54)) ([4e434d5](https://github.com/svasek/python-neopool-modbus/commit/4e434d575f6718e88471587b62592e9985329446))

## [4.3.1](https://github.com/svasek/python-neopool-modbus/compare/v4.3.0...v4.3.1) (2026-07-22)


### 🐛 Bug Fixes

* **client:** gate filtration-state fixup to variable-speed pumps ([#52](https://github.com/svasek/python-neopool-modbus/issues/52)) ([86596ad](https://github.com/svasek/python-neopool-modbus/commit/86596add9ebe63965131e7ba8072b04dfcae68a8))

## [4.3.0](https://github.com/svasek/python-neopool-modbus/compare/v4.2.1...v4.3.0) (2026-07-17)


### ✨ Features

* **client:** add boost guard to manual filtration ([#50](https://github.com/svasek/python-neopool-modbus/issues/50)) ([ecfe26b](https://github.com/svasek/python-neopool-modbus/commit/ecfe26be17b357abfd2800ee9eb081e821b3adfc))

## [4.2.1](https://github.com/svasek/python-neopool-modbus/compare/v4.2.0...v4.2.1) (2026-07-11)


### 🐛 Bug Fixes

* **client:** 🐛 read relay auto-mode guard from timer cache ([#48](https://github.com/svasek/python-neopool-modbus/issues/48)) ([1abb9ef](https://github.com/svasek/python-neopool-modbus/commit/1abb9ef88c58c8e82a406834476e536950bb4b87))

## [4.2.0](https://github.com/svasek/python-neopool-modbus/compare/v4.1.0...v4.2.0) (2026-07-07)


### ✨ Features

* **exceptions:** ✨ add reason discriminator to NeoPoolInvalidStateError ([#47](https://github.com/svasek/python-neopool-modbus/issues/47)) ([91c09f6](https://github.com/svasek/python-neopool-modbus/commit/91c09f69c49f314ab116b5084c11ad27c9b821bd))


### 🐛 Bug Fixes

* **client:** 🩹 default apply=True on async_set_setpoint ([#45](https://github.com/svasek/python-neopool-modbus/issues/45)) ([eb8f536](https://github.com/svasek/python-neopool-modbus/commit/eb8f536b4455557ca97e01b57014065cc78b089c))

## [4.1.0](https://github.com/svasek/python-neopool-modbus/compare/v4.0.0...v4.1.0) (2026-07-07)


### ✨ Features

* **client:** ✨ add ConfigKind + async_set_config_option for discrete config slots ([#44](https://github.com/svasek/python-neopool-modbus/issues/44)) ([08d5a1e](https://github.com/svasek/python-neopool-modbus/commit/08d5a1e8d01c64ffe5c35d4779589670474b32d5))
* **client:** ✨ extend async_set_setpoint with SMART_TEMP kinds and apply kwarg ([#42](https://github.com/svasek/python-neopool-modbus/issues/42)) ([8fda90c](https://github.com/svasek/python-neopool-modbus/commit/8fda90cd10bc5eaba8db8741b5bf0bddfd24c921))

## [4.0.0](https://github.com/svasek/python-neopool-modbus/compare/v3.6.0...v4.0.0) (2026-07-07)


### ⚠ BREAKING CHANGES

* 💥 rename HIDRO/ION Low Flow status keys to Low + add Redox Low ([#40](https://github.com/svasek/python-neopool-modbus/issues/40))
* 💥 add high-level relay / setpoint / flag API ([#39](https://github.com/svasek/python-neopool-modbus/issues/39))

### ✨ Features

* 💥 add high-level relay / setpoint / flag API ([#39](https://github.com/svasek/python-neopool-modbus/issues/39)) ([30a5a8e](https://github.com/svasek/python-neopool-modbus/commit/30a5a8e3cb6356ada4e77cb47796069d51e5a899))
* 💥 rename HIDRO/ION Low Flow status keys to Low + add Redox Low ([#40](https://github.com/svasek/python-neopool-modbus/issues/40)) ([61f9747](https://github.com/svasek/python-neopool-modbus/commit/61f974764609b4c0979b5d7e67375edb2293ba70)), closes [#33](https://github.com/svasek/python-neopool-modbus/issues/33)

## [3.6.0](https://github.com/svasek/python-neopool-modbus/compare/v3.5.0...v3.6.0) (2026-07-02)


### ✨ Features

* **decoders:** ✨ add calculate_next_interval_time helper ([#37](https://github.com/svasek/python-neopool-modbus/issues/37)) ([e489a88](https://github.com/svasek/python-neopool-modbus/commit/e489a8884d70af5a8fa3b8497f5cdced70504d2f))
* **decoders:** ✨ add device time codec ([#38](https://github.com/svasek/python-neopool-modbus/issues/38)) ([eff733d](https://github.com/svasek/python-neopool-modbus/commit/eff733d483a569883ca3954c1e13eaa1086327e5))
* **decoders:** ✨ add parse_register_int helper ([#36](https://github.com/svasek/python-neopool-modbus/issues/36)) ([64cd80a](https://github.com/svasek/python-neopool-modbus/commit/64cd80a9b0c438d6cc41c384345f0a21b1319ff3))
* **registers:** ✨ add find_corrupted_gpio_registers helper ([#34](https://github.com/svasek/python-neopool-modbus/issues/34)) ([0ba247b](https://github.com/svasek/python-neopool-modbus/commit/0ba247b61aaceb5f167ed7a54b2fb92f9b6560e7))

## [3.5.0](https://github.com/svasek/python-neopool-modbus/compare/v3.4.1...v3.5.0) (2026-07-01)


### ✨ Features

* **decoders:** ✨ expose label collections and add ph alarm / filtvalve codecs ([#31](https://github.com/svasek/python-neopool-modbus/issues/31)) ([468db01](https://github.com/svasek/python-neopool-modbus/commit/468db016a0b114ec84314996f388f9b88b4e6a10))

## [3.4.1](https://github.com/svasek/python-neopool-modbus/compare/v3.4.0...v3.4.1) (2026-06-18)


### 🐛 Bug Fixes

* **client:** 🩹 log int value instead of TimerRelayMode repr in write debug ([648045d](https://github.com/svasek/python-neopool-modbus/commit/648045d4dee7859ec555d42be0b571c15f8272ad))

## [3.4.0](https://github.com/svasek/python-neopool-modbus/compare/v3.3.0...v3.4.0) (2026-06-18)


### ✨ Features

* **registers:** ✨ add named bitmask constants ([5f6417f](https://github.com/svasek/python-neopool-modbus/commit/5f6417f77a03c28f8b4fd4933dcc83ff16e37c1d))

## [3.3.0](https://github.com/svasek/python-neopool-modbus/compare/v3.2.0...v3.3.0) (2026-06-18)


### ✨ Features

* **registers:** ✨ add named constants for all integration-facing registers ([a8330d7](https://github.com/svasek/python-neopool-modbus/commit/a8330d728604a19a24b3b88415b218e268e343e9))

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
