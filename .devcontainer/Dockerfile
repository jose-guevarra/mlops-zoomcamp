FROM public.ecr.aws/amazonlinux/amazonlinux:latest

# Use venv dir local to Pipfile
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_VERBOSITY=-1

RUN dnf update -y && yum install -y sudo vim git unzip make wget \
    python3-pip python3.11 python3.11-pip glibc-langpack-en


RUN pip3.11 install pipenv


# User setup
ARG REMOTE_USER=dockeruser

RUN /usr/sbin/groupadd -r sudo \
    && /usr/sbin/useradd -rm -d /workspaces -s /bin/bash -g sudo -u 1001 $REMOTE_USER \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER $REMOTE_USER
