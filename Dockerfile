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

# Set ownership
RUN chown -R ${USER_NAME}:${USER_NAME} ${ANDROID_HOME} ${IDEA_HOME}

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

CMD ["/bin/bash", "-i"]
