# Samsung Galaxy Watch Dev Environment on arm64

Docker-based development environment for Wear OS (Samsung Galaxy Watch) apps,
running on an **aarch64 (arm64) Linux host**.

---

## What's Inside

| Component | Version | Notes |
|-----------|---------|-------|
| Base image | Ubuntu 22.04 | arm64 |
| Java | OpenJDK 17 (arm64) | |
| IntelliJ IDEA Community | 2024.3.4 | arm64 native build |
| Android SDK | platforms 34 + 35 | |
| Build Tools | 35.0.0 | x86_64, run via QEMU |
| Wear OS system image | android-34;android-wear;arm64-v8a | for emulator |
| adb | 28.0.2 (arm64) | from apt, not SDK |
| aapt2 | 2.19 (x86_64 via QEMU) | see workarounds below |

---

## Quick Start

```bash
bash build.sh   # build the image (~40 min first time)
bash run.sh     # start the container
bash into.sh    # get a shell inside
```

Launch IntelliJ IDEA:
```bash
docker exec -it watch-dev idea.sh
```

---

## Architecture Decisions

### Why IntelliJ IDEA instead of Android Studio?

Google does **not** publish Linux arm64 builds of Android Studio. All download
URLs for Linux arm64 return 404. IntelliJ IDEA Community with the Android plugin
is the practical replacement — it provides the same Gradle/SDK integration.

### Why is adb replaced?

Google's `platform-tools` zip (which `sdkmanager` installs) ships only x86_64
Linux binaries. The `adb` inside it cannot execute on arm64. Fix: install the
native arm64 `adb` from Ubuntu apt (`adb` package, version 28.0.2) and copy it
over the SDK's binary.

### Why the aapt2 QEMU wrapper?

Google's Android build tools (`build-tools;35.0.0`) also only ship x86_64
binaries on Linux. `aapt2` (Android Asset Packaging Tool) is called by every
Gradle build and fails with "Exec format error" on arm64.

**Workaround:**
1. Install `qemu-user-static` and `libc6:amd64` — this lets arm64 Linux execute
   x86_64 ELF binaries via QEMU user-mode emulation.
2. Create a wrapper script at `/usr/local/bin/aapt2`:
   ```sh
   #!/bin/sh
   exec qemu-x86_64-static /opt/android-sdk/build-tools/35.0.0/aapt2 "$@"
   ```
3. Set `android.aapt2FromMavenOverride=/usr/local/bin/aapt2` in
   `~/.gradle/gradle.properties` — Gradle uses the wrapper for every project
   automatically, without any per-project configuration.

### apt multiarch gotcha

Ubuntu arm64 images use `ports.ubuntu.com` which has **no amd64 packages**.
Adding `amd64` architecture via `dpkg --add-architecture amd64` without first
pinning `ports.ubuntu.com` to arm64-only causes `apt-get update` to 404 on
every amd64 fetch and abort.

Fix applied in Dockerfile:
```dockerfile
# Pin ports.ubuntu.com to arm64 BEFORE adding amd64 arch
RUN sed -i 's|^deb http://ports.ubuntu.com|deb [arch=arm64] http://ports.ubuntu.com|g' \
        /etc/apt/sources.list && \
    dpkg --add-architecture amd64 && \
    echo 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu jammy main universe' \
        > /etc/apt/sources.list.d/amd64.list
    # ... (jammy-updates and jammy-security too)
```

---

## Verified Build Test

A minimal Wear OS APK was built inside the container:

```bash
# gradle.properties (auto-configured globally via Dockerfile)
android.aapt2FromMavenOverride=/usr/local/bin/aapt2

# app/build.gradle
android {
    compileSdk 35
    namespace 'com.example.wearapp'
    defaultConfig { minSdk 30; targetSdk 34 }
}

# Result
BUILD SUCCESSFUL
APK manifest: uses-feature android.hardware.type.watch  ✓
```

---

## Volume Mounts

| Host path | Container path | Purpose |
|-----------|---------------|---------|
| `~/watch-projects` | `/home/<user>/projects` | your app source code |
| `~/.android-docker` | `/home/<user>/.android` | AVD / emulator state |
| `~/.gradle-docker` | `/home/<user>/.gradle` | Gradle cache |

---

## Known Limitations

- **No hardware-accelerated emulator** — KVM is not available on this host.
  The Wear OS arm64-v8a system image can run in software emulation but will
  be slow. Connecting a physical Galaxy Watch over ADB (USB or Wi-Fi) is
  recommended for testing.
- **aapt2 runs under QEMU** — adds a small overhead per resource compilation
  step. Not noticeable in practice for incremental builds.
- **No Android Studio** — IntelliJ IDEA does not include the Device Manager UI
  for creating AVDs out of the box. Use `avdmanager` from the terminal:
  ```bash
  avdmanager create avd -n WearOS -k "system-images;android-34;android-wear;arm64-v8a"
  emulator -avd WearOS -no-window
  ```

---

## Pushing to Registry

Requires a GitHub personal access token with `write:packages` scope:

```bash
export GITHUB_TOKEN=<your_token>
bash push.sh
```

Image is published to `ghcr.io/manumnoha-sys/watch-dev:latest`.
