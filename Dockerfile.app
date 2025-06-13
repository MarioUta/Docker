FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system tools
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    software-properties-common \
    lsb-release

# -----------------------------
# Install Node.js 18 (official source, not broken apt version)
# -----------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# -----------------------------
# Install Python 3.10 and pip
# -----------------------------
RUN apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-distutils

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 -

# Set python3 default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# -----------------------------
# Install MySQL client
# -----------------------------
RUN apt-get install -y default-mysql-client

# -----------------------------
# Set working directory
# -----------------------------
WORKDIR /app

# Copy and install Node dependencies
COPY node_server/package*.json ./node_server/
RUN cd node_server && npm install express cors body-parser nodemon && npm install

# Copy the rest of the code
COPY . .

# Expose necessary ports
EXPOSE 3000
EXPOSE 5000

# Start the Node.js server
CMD ["node", "node_server/server.js"]
