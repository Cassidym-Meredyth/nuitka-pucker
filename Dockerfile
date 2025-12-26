FROM python:3.9-slim-trixie AS builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    patchelf \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libglx-mesa0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import sqlcipher3; print(sqlcipher3.__file__)"

RUN nuitka --version

COPY ./Code /app/Code

WORKDIR /app/Code/

RUN python -m nuitka --standalone --onefile \
  --enable-plugin=pyqt5 \
  --include-package=sqlcipher3 \
  --output-filename=Crystal \
  main.pyw

FROM python:3.9-slim-trixie

WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libglx-mesa0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/Code/Crystal /app/Crystal


CMD ["./Crystal"]