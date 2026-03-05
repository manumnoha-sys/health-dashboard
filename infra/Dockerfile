FROM ubuntu:22.04

ARG IDEA_VERSION=2024.3.4
ARG USER_NAME=developer
ARG USER_UID=1000
ARG USER_GID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV IDEA_HOME=/opt/idea
ENV PATH=${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${IDEA_HOME}/bin:${PATH}
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV DISPLAY=:0

# System dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    wget curl unzip git sudo vim \
    # X11 / GUI dependencies for IntelliJ IDEA
    libx11-6 libxext6 libxrender1 libxtst6 libxi6 \
    libfreetype6 libfontconfig1 libxss1 libgbm1 \
    libgl1 libgl1-mesa-dri libglx-mesa0 \
    libxrandr2 libxcomposite1 libxcursor1 libxdamage1 \
    libxfixes3 libcairo2 libpango-1.0-0 libatk1.0-0 \
    libgdk-pixbuf2.0-0 libgtk-3-0 libnss3 \
    ca-certificates gnupg lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user matching host user
RUN groupadd -g ${USER_GID} ${USER_NAME} && \
    useradd -u ${USER_UID} -g ${USER_GID} -m -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Download and install IntelliJ IDEA Community (arm64 native)
RUN wget -q --show-progress --progress=bar:force \
        "https://download.jetbrains.com/idea/ideaIC-${IDEA_VERSION}-aarch64.tar.gz" \
        -O /tmp/idea.tar.gz && \
    tar -xzf /tmp/idea.tar.gz -C /opt && \
    mv /opt/idea-IC-* ${IDEA_HOME} && \
    rm /tmp/idea.tar.gz

# Install native arm64 adb (Google's platform-tools zip only ships x86_64)
# Also install qemu-user-static + x86_64 libc so the x86_64 aapt2 binary can run on arm64.
# Pin ports.ubuntu.com to arm64 only BEFORE adding amd64 arch, otherwise apt tries to
# fetch amd64 packages from ports.ubuntu.com which doesn't have them (404).
RUN sed -i 's|^deb http://ports.ubuntu.com|deb [arch=arm64] http://ports.ubuntu.com|g' /etc/apt/sources.list && \
    dpkg --add-architecture amd64 && \
    echo 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu jammy main universe' > /etc/apt/sources.list.d/amd64.list && \
    echo 'deb [arch=amd64] http://archive.ubuntu.com/ubuntu jammy-updates main universe' >> /etc/apt/sources.list.d/amd64.list && \
    echo 'deb [arch=amd64] http://security.ubuntu.com/ubuntu jammy-security main universe' >> /etc/apt/sources.list.d/amd64.list && \
    apt-get update && apt-get install -y -q adb qemu-user-static libc6:amd64 && \
    rm -rf /var/lib/apt/lists/*

# Install Android SDK command-line tools
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip \
        -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /tmp/cmdline-tools && \
    mv /tmp/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm -rf /tmp/cmdline-tools /tmp/cmdline-tools.zip

# Accept licenses and install Wear OS SDK components for arm64
RUN yes | sdkmanager --licenses && \
    sdkmanager \
        "platform-tools" \
        "build-tools;35.0.0" \
        "platforms;android-35" \
        "platforms;android-34" \
        "system-images;android-34;android-wear;arm64-v8a"

# Replace x86_64 adb from SDK with native arm64 binary
RUN cp /usr/bin/adb ${ANDROID_HOME}/platform-tools/adb

# Create aapt2 wrapper: SDK ships x86_64-only aapt2; run it via qemu-user-static
RUN printf '#!/bin/sh\nexec qemu-x86_64-static %s/build-tools/35.0.0/aapt2 "$@"\n' \
        "${ANDROID_HOME}" > /usr/local/bin/aapt2 && \
    chmod +x /usr/local/bin/aapt2

# Set ownership
RUN chown -R ${USER_NAME}:${USER_NAME} ${ANDROID_HOME} ${IDEA_HOME}

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

# Configure Gradle to use the local aapt2 wrapper for all projects
RUN mkdir -p ~/.gradle && \
    echo 'android.aapt2FromMavenOverride=/usr/local/bin/aapt2' >> ~/.gradle/gradle.properties

CMD ["/bin/bash", "-i"]
