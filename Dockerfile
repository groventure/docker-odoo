FROM debian:jessie
MAINTAINER Hellyna NG <hellyna@hellyna.com>

# Install node repository.
RUN set -x; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl && \
    curl -L https://deb.nodesource.com/setup_4.x | bash -

# Install dependencies
RUN set -x; \
        apt-get update && \
        apt-get install -y --no-install-recommends \
            # Required by pip install python-ldap
            libldap-2.4-2 \
            # Required by pip install psycopg2
            libpq5 \
            # Required by pip install python-ldap
            libsasl2-2 \
            # Required by pip install lxml
            libxml2 \
            # Required by pip install lxml
            libxslt1.1 \
            # Required by npm install -g less
            nodejs \
            postgresql-client \
            python && \
        # Required by npm install -g less
        update-alternatives --install \
            /usr/bin/node node /usr/bin/nodejs 10

# Install build dependencies
RUN set -x; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # Needed for git and python-pip for proper SSL verification of downloaded packages..
        ca-certificates \
        # Required by pip install python-ldap
        libldap2-dev \
        # Required by pip install psycopg2
        libpq-dev \
        # Required by pip install python-ldap
        libsasl2-dev \
        # Required by pip install lxml
        libxml2-dev \
        # Required by pip install lxml
        libxslt1-dev \
        # Required by pip install wheels
        gcc \
        git \
        # Required by pip install wheels
        python-dev \
        python-pip \
        python-setuptools && \
    # Required by pip install wheels
    pip install --upgrade pip

# Installing node dependencies
RUN set -x; \
    npm install -g less

# Get odoo sources
RUN set -x; \
    mkdir -p /opt && \
    git clone \
        --branch 9.0 \
        --depth 1 \
        https://github.com/OCA/OCB.git /opt/odoo && \
    ln -svf /opt/odoo/openerp-server /usr/bin/openerp-server && \
    groupadd --gid 107 odoo && \
    useradd -d /var/lib/odoo --create-home --uid 104 --gid 107 --system odoo && \
    rm -rf /opt/odoo/.git

# Install pip dependencies
RUN pip install -r /opt/odoo/requirements.txt

# Install Odoo
#ENV ODOO_VERSION 9.0
#ENV ODOO_RELEASE 20160301
#RUN set -x; \
#        curl -o odoo.deb -SL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}c.${ODOO_RELEASE}_all.deb \
#        && dpkg --force-depends -i odoo.deb \
#        && apt-get update \
#        && apt-get -y install -f --no-install-recommends \
#        && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy Odoo configuration file and entrypoint
COPY ./openerp-server.conf /opt/odoo/
COPY ./entrypoint.py /

# Mkdir and define volumes, as well as fix permissions.
RUN mkdir -p /mnt/extra-addons \
        && chown -R odoo /mnt/extra-addons \
        && chmod 0755 /entrypoint.py
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Set the default config file
ENV OPENERP_SERVER /opt/odoo/openerp-server.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.py"]
