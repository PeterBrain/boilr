# Boilr Setup

- [Boilr Setup](#boilr-setup)
  - [Containerised in Docker (recommended)](#containerised-in-docker-recommended)
    - [Manually building \& run container](#manually-building--run-container)
    - [Docker Hub (ARMv6 only)](#docker-hub-armv6-only)
  - [PyPI - Python Package Index](#pypi---python-package-index)
  - [Manually build and install package](#manually-build-and-install-package)


## Containerised in Docker (recommended)

### Manually building & run container

```bash
docker-compose build
docker-compose up -d
```

### Docker Hub (ARMv6 only)

```bash
docker run --privileged -v ./config.yaml:/etc/boilr/config.yaml --device /dev/gpiomem:/dev/gpiomem peterbrain/boilr:latest
```

> [!NOTE]
> In order to install and use Docker on a Raspberry Pi 1 Model B, I had to set `sysctl vm.overcommit_memory=1` and restart after the installation.

## PyPI - Python Package Index

Boilr is not yet available on Python Package Index. Check back later

## Manually build and install package

```bash
pip install .
```

Create config folder and copy sample config file to config directory.

```bash
mkdir /etc/boilr
cp config.yaml /etc/boilr/
```

Edit the config file to your needs. Check out this [Sample configuration][config-reference] for reference.

```bash
vi /etc/boilr/config.yaml
```


[config-reference]: ../config.yaml
