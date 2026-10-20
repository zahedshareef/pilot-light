# Pilot Light (beta)

## Maintained fork: 0.9.2

This fork of CyrisXD/pilot-light hardens privileged installation and background recovery.

- The administrator script generates its sudoers configuration in a root-owned staging directory, validates it, and installs only the fixed power-management commands. There is no user-writable temporary configuration at the privilege boundary.
- The background agent checks every 10 seconds for a missing process or a heartbeat older than 20 seconds. It restores sleep and explicitly requests sleep after a crash or hang (usually within 30 seconds for a hang, subject to macOS scheduling).
- Keep-awake remains disabled until the helper is installed, the background agent is approved, and heartbeat writes succeed. Approve **Pilot Light** in System Settings > General > Login Items & Extensions when prompted. Existing installations must reinstall the helper for the new sleep permission.
- Failed Low Power Mode restoration retains the saved settings for a later retry. Recovery after a crash does not itself restore Low Power Mode; reopening the app retries restoration.
- Update checks point to this fork, so an upstream release does not replace these changes.

This build is ad-hoc signed, not Apple notarized. It remains a beta. Automated tests cover pure app logic and simulated watchdog cases; actual closed-lid sleep, thermal cutoffs, and battery cutoffs require supervised hardware validation. Keep the Mac ventilated during initial testing.

Validation: `python3 -m unittest discover -s tests -v`, plus the built executable's `--selftest` mode. Build to a chosen location using `APP_OUTPUT="/absolute/path/Pilot Light.app" ./build.sh`.

**Lid shut. Pilot light on.** A tiny macOS menu bar app that keeps your MacBook awake with the lid closed, so AI coding agents keep working, on under a third of the power.

![Your agents don’t need the lid open, or that much power. 16.7 W with the lid open, 4.8 W with it closed.](site/assets/og.png)

**Original project:** [CyrisXD/pilot-light](https://github.com/CyrisXD/pilot-light) · **Fork:** [zahedshareef/pilot-light](https://github.com/zahedshareef/pilot-light)

## What it does

When the lid closes while you're logged in, Pilot Light:

- keeps the Mac awake (power assertions like `caffeinate` can't survive a lid close; this uses the system sleep setting that can),
- switches to Low Power Mode, then restores your exact battery and charger settings when the lid opens,
- turns the display off,
- lets the Mac sleep anyway on serious heat or when the battery drops below your limit.

It keeps working behind the lock screen. Log out or switch users, and closing the lid sleeps the Mac as normal. Turn off **Keep awake when screen locked** and it also sleeps once the screen locks. The menu shows your Mac's own measured power draw with the lid open and closed.

Once a day it checks GitHub for a newer release and shows **Update available** in the menu if there is one. That's its only network request, and you can turn it off with **Check for updates daily**.

| | Measured¹ |
|---|---|
| Lid open | 16.7 W · ~6 h battery |
| Lid closed, Pilot Light on | 4.8 W · 20+ h battery |
| App memory | ~25 MB |
| App CPU while waiting | ~0% |
| Download | 900 KB |

¹ MacBook Pro with M5 Max (macOS 26.6), on battery. With Claude Code building and testing a website, lid closed: 2.3 W. Heavy local builds draw more, and battery hours are estimates.

## Install

1. Download the latest release and drag **Pilot Light** to Applications. It isn't notarized yet: the first time you open it, go to **System Settings › Privacy & Security** and click **Open Anyway**.
2. Click the flame in the menu bar, then **Install helper (admin)…**. This one admin prompt adds a sudoers rule that allows only `pmset` sleep and Low Power changes.
3. Approve the background agent in System Settings if prompted. Confirm the menu reports that keep-awake is on before closing the lid.

While Pilot Light is on, the Mac also won't idle-sleep with the lid open (the display still turns off).

If Pilot Light crashes, is force-quit, or stops updating its heartbeat, a background check restores sleep and explicitly requests it. See the fork notes above for timing and limitations.

## Uninstall

Choose **Remove helper…** from the Pilot Light menu, quit the app, and drag it to the Bin. This also unregisters the background agent. If removing the sudoers rule manually, first restore sleep with `sudo /usr/bin/pmset -a disablesleep 0`, then remove `/etc/sudoers.d/pilotlight`; manually removing the rule alone does not restore sleep or unregister the agent.

## Beta

Pilot Light is in public beta. The heat and battery cutoffs have only been tested on one Mac so far. If something doesn't behave as described, please [open an issue](https://github.com/CyrisXD/pilot-light/issues/new).

## Build from source

```bash
git clone https://github.com/zahedshareef/pilot-light
cd pilot-light
./build.sh
open ~/Applications/"Pilot Light.app"
```

Needs the Xcode command line tools. Builds a universal app (Apple silicon and Intel) for macOS 13 and later. The whole app is [`main.swift`](main.swift). Run `PilotLight --selftest` to check the core logic.

`measure.sh` logs whole-Mac power from battery telemetry if you want to reproduce the numbers: `./measure.sh closed-batt 10`.

## Support development

Pilot Light is free. If it keeps your agents running, you can [sponsor on GitHub](https://github.com/sponsors/CyrisXD) or [buy me a coffee](https://buymeacoffee.com/FiRmVXOZh).

## License

MIT © sudolabs
