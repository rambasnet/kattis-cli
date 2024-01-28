FROM pypy:3

# install basic packages
RUN apt update \
    && apt install -y \
    sqlite3 time curl git nano dos2unix \
    net-tools iputils-ping iproute2 sudo gdb less \
    openssl libssl-dev \
    ca-certificates \
    && apt clean


# install c/c++ and build tools
RUN apt install build-essential -y

# install java jdk that includes jre and java compiler
RUN apt install default-jdk -y

# install nodejs
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt install nodejs -y


ARG USER=user
ARG UID=1000
ARG GID=1000

# set environment variables
ENV USER                ${USER}
ENV HOME                /home/${USER}

WORKDIR ${HOME}

# install rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# create user and setup permissions on /etc/sudoers
RUN useradd -m -s /bin/bash -N -u $UID $USER && \
    echo "${USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers && \
    chmod 0440 /etc/sudoers && \
    chmod g+w /etc/passwd 

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# install zsh - use "Bira" theme with some customization. 
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.5/zsh-in-docker.sh)" -- \
    -t bira \
    -p git \
    -p ssh-agent \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions

# update path
ENV PATH="${HOME}/.local/bin:${PATH}:${HOME}/.cargo/bin"

USER user

CMD zsh
