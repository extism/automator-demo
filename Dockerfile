FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository universe
RUN apt-get update
RUN apt-get -y install build-essential curl python3.11 python3-pip git vim

# Install extism cli and sharedlib
RUN pip3 install poetry
RUN pip3 install git+https://github.com/extism/cli
RUN extism --prefix=/usr/local install latest
RUN pip3 install extism

# Install rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

