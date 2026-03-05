# Samsung Galaxy Watch App

[![Docker Image](https://img.shields.io/badge/ghcr.io-watch--dev-blue?logo=docker)](https://github.com/manumnoha-sys/smartwatch/pkgs/container/watch-dev)
[![Platform](https://img.shields.io/badge/platform-linux%2Farm64-lightgrey)](https://github.com/manumnoha-sys/smartwatch)

End-to-end project for building a **Samsung Galaxy Watch (Wear OS)** app, with a cloud backend and a Docker-based development environment designed for **Linux arm64** hosts.

---

## Repository Structure

```
.
├── infra/          # Docker dev environment (arm64)
├── watch-app/      # Wear OS application (Samsung Galaxy Watch)
└── server/         # Cloud backend
```

### `infra/` — Development Environment

Docker image based on Ubuntu 22.04 with IntelliJ IDEA Community (arm64 native), the Android SDK, Wear OS system image, and all arm64 workarounds baked in. Published to `ghcr.io/manumnoha-sys/watch-dev`.

See [`infra/SETUP.md`](infra/SETUP.md) for a full explanation of the arm64 workarounds.

```bash
bash infra/build.sh   # build the image
bash infra/run.sh     # start the container
bash infra/into.sh    # open a shell inside
```

### `watch-app/` — Wear OS App

Android application targeting Samsung Galaxy Watch. Developed inside the `infra/` Docker container.

### `server/` — Cloud Backend

Backend service for data sync, push notifications, and the REST API consumed by the watch app.

---

## Quick Start

```bash
# 1. Start the dev container (pulls from GHCR if image not found locally)
bash infra/run.sh

# 2. Open a shell inside
bash infra/into.sh

# 3. Build the watch app
cd ~/projects/watch-app && ./gradlew assembleDebug
```

---

## Requirements

- Linux arm64 (aarch64) host
- Docker 20+
- X11 display (for IntelliJ IDEA GUI)
