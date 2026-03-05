# watch-dev

> Docker-based development environment for **Samsung Galaxy Watch (Wear OS)** apps on **Linux arm64 (aarch64)** hosts.

[![Docker Image](https://ghcr-badge.egpl.dev/manumnoha-sys/watch-dev/size)](https://github.com/manumnoha-sys/smartwatch/pkgs/container/watch-dev)
[![Image](https://img.shields.io/badge/ghcr.io-watch--dev-blue?logo=docker)](https://github.com/manumnoha-sys/smartwatch/pkgs/container/watch-dev)
[![Platform](https://img.shields.io/badge/platform-linux%2Farm64-lightgrey)](https://github.com/manumnoha-sys/smartwatch)

---

## Overview

Google does not publish Linux arm64 builds of Android Studio. This project provides a fully working alternative: a Docker image with **IntelliJ IDEA Community** (arm64 native), the **Android SDK**, and all necessary workarounds to build and deploy Wear OS apps from an arm64 machine.

| Component | Version |
|-----------|---------|
| Base OS | Ubuntu 22.04 (arm64) |
| Java | OpenJDK 17 |
| IDE | IntelliJ IDEA Community 2024.3.4 |
| Android SDK | platforms 34 + 35, build-tools 35.0.0 |
| Wear OS system image | `android-34;android-wear;arm64-v8a` |
| adb | 28.0.2 (native arm64) |

---

## Requirements

- Linux arm64 (aarch64) host
- Docker 20+
- X11 display (for IntelliJ IDEA GUI)

---

## Quick Start

```bash
# 1. Build the image (first time ~30–40 min)
bash build.sh

# 2. Start the container
bash run.sh

# 3. Open a shell inside
bash into.sh
```

Launch IntelliJ IDEA from inside the container or directly from the host:

```bash
docker exec -it watch-dev idea.sh
```

---

## Usage

### Building your app

Gradle is configured automatically. Create or clone a Wear OS project into `~/watch-projects/` on the host — it will be available at `~/projects/` inside the container.

```bash
# Inside the container
cd ~/projects/MyWatchApp
./gradlew assembleDebug
```

### Connecting a physical device

Wi-Fi ADB (recommended — no hardware acceleration in emulator):

```bash
adb connect <watch-ip>:5555
adb devices
```

### Creating a software emulator (slow, no KVM)

```bash
avdmanager create avd -n GalaxyWatch \
    -k "system-images;android-34;android-wear;arm64-v8a"
emulator -avd GalaxyWatch -no-window
```

---

## Persistent Volumes

Data that survives container restarts:

| Host path | Container path | Contents |
|-----------|---------------|----------|
| `~/watch-projects/` | `~/projects/` | Your app source code |
| `~/.android-docker/` | `~/.android/` | AVDs, emulator state |
| `~/.gradle-docker/` | `~/.gradle/` | Gradle build cache |

---

## Publishing

Requires a GitHub token with `write:packages` scope:

```bash
export GITHUB_TOKEN=<your_token>
bash push.sh
```

The script will tag and push the Docker image to `ghcr.io/manumnoha-sys/watch-dev:latest` and push any updated files to this repository.

---

## Architecture & Workarounds

See [SETUP.md](SETUP.md) for a detailed explanation of:

- Why IntelliJ IDEA is used instead of Android Studio
- How the native arm64 `adb` is sourced
- The `aapt2` QEMU wrapper (`build-tools` ships x86_64-only binaries)
- The apt multiarch gotcha when adding `amd64` packages on an arm64 Ubuntu image

---

## License

MIT
