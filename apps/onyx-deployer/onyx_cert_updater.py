#!/usr/bin/env python3

"""
NVIDIA Onyx Switch Certificate Updater (JSON API)

Updates SSL/TLS certificates on NVIDIA Onyx switches via the JSON API.
Supports importing external certificates and setting them as the HTTPS certificate.
"""

import os
import sys
import argparse
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import ssl
import http.cookiejar
from datetime import datetime

REQUEST_TIMEOUT = 30


class PostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom redirect handler that preserves POST data on redirects"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """
        Override to preserve POST method and data on redirect
        """
        new_req = urllib.request.Request(
            newurl,
            data=req.data,
            headers={k: v for k, v in req.headers.items()},
            method=req.get_method()
        )
        return new_req


class OnyxCertUpdater:
    """Certificate updater for NVIDIA Onyx switches via JSON API"""

    def __init__(self, hostname, username, password, debug=False):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.base_url = f"https://{hostname}"

        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("OnyxCertUpdater")

        # Create SSL context that ignores certificate verification
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # Setup cookie handling for session management
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self.ssl_context),
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            PostRedirectHandler()
        )

    def login(self):
        """
        Login to switch via form-based authentication
        :return: bool
        """
        login_url = f"{self.base_url}/admin/launch?script=rh&template=login&action=login"

        login_data = urllib.parse.urlencode({
            'f_user_id': self.username,
            'f_password': self.password
        }).encode('utf-8')

        self.logger.debug(f"Logging in to {self.hostname}")

        try:
            request = urllib.request.Request(
                login_url,
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response = self.opener.open(request, timeout=REQUEST_TIMEOUT)

            # Check if we got redirected to home (successful login)
            if response.geturl() and 'home' in response.geturl():
                self.logger.info("Login successful")
                return True

            # Also check for session cookie
            for cookie in self.cookie_jar:
                if cookie.name == 'session':
                    self.logger.info("Login successful (session cookie obtained)")
                    return True

            self.logger.error("Login failed - no session cookie obtained")
            return False

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

    def execute_command(self, cmd):
        """
        Execute a command via JSON API
        :param cmd: Command string to execute
        :return: dict with response or None on error
        """
        # Use json-login endpoint - PostRedirectHandler will preserve POST data on redirect
        api_url = f"{self.base_url}/admin/launch?script=rh&template=json-request&action=json-login"

        payload = json.dumps({"cmd": cmd}).encode('utf-8')

        self.logger.debug(f"Executing command: {cmd[:100]}...")

        try:
            request = urllib.request.Request(
                api_url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            response = self.opener.open(request, timeout=REQUEST_TIMEOUT)
            response_data = response.read().decode('utf-8')

            # Handle empty response
            if not response_data:
                self.logger.error("Empty response from server")
                return None

            result = json.loads(response_data)

            if result.get('status') == 'OK':
                self.logger.debug(f"Command successful: {result.get('status_message', '')}")
                return result
            else:
                self.logger.error(f"Command failed: {result.get('status_message', 'Unknown error')}")
                return result

        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return None

    def get_current_cert_info(self):
        """
        Get information about the current HTTPS certificate
        :return: dict with cert info or None
        """
        result = self.execute_command("show web")
        if not result or result.get('status') != 'OK':
            return None

        data = result.get('data', [])
        for section in data:
            if section.get('header') == 'Web User Interface':
                cert_name = section.get('HTTPS certificate name')
                return {
                    'cert_name': cert_name,
                    'https_enabled': section.get('HTTPS enabled') == 'yes'
                }
        return None

    def get_cert_validity(self, cert_name):
        """
        Get certificate validity dates
        :param cert_name: Name of certificate
        :return: dict with validity info or None
        """
        result = self.execute_command(f"show crypto certificate")
        if not result or result.get('status') != 'OK':
            return None

        data = result.get('data', [])
        for cert in data:
            for key in cert.keys():
                if cert_name in key:
                    cert_data = cert[key]
                    for item in cert_data:
                        if 'Validity' in item:
                            validity = item['Validity'][0]
                            return {
                                'starts': validity.get('Starts'),
                                'expires': validity.get('Expires')
                            }
        return None

    def import_certificate(self, cert_name, cert_pem, key_pem):
        """
        Import a certificate and private key
        :param cert_name: Name for the certificate
        :param cert_pem: PEM-encoded certificate
        :param key_pem: PEM-encoded private key
        :return: bool
        """
        # Import public certificate
        self.logger.info(f"Importing public certificate as '{cert_name}'")
        cert_cmd = f'crypto certificate name {cert_name} public-cert pem "{cert_pem}"'
        result = self.execute_command(cert_cmd)
        if not result or result.get('status') != 'OK':
            self.logger.error(f"Failed to import public certificate: {result}")
            return False

        # Import private key
        self.logger.info(f"Importing private key for '{cert_name}'")
        key_cmd = f'crypto certificate name {cert_name} private-key pem "{key_pem}"'
        result = self.execute_command(key_cmd)
        if not result or result.get('status') != 'OK':
            self.logger.error(f"Failed to import private key: {result}")
            return False

        self.logger.info("Certificate and key imported successfully")
        return True

    def set_https_certificate(self, cert_name):
        """
        Set the certificate to use for HTTPS
        :param cert_name: Name of certificate to use
        :return: bool
        """
        self.logger.info(f"Setting HTTPS certificate to '{cert_name}'")
        result = self.execute_command(f"web https certificate name {cert_name}")
        if not result or result.get('status') != 'OK':
            self.logger.error(f"Failed to set HTTPS certificate: {result}")
            return False

        return True

    def delete_certificate(self, cert_name):
        """
        Delete a certificate
        :param cert_name: Name of certificate to delete
        :return: bool
        """
        self.logger.info(f"Deleting certificate '{cert_name}'")
        result = self.execute_command(f"no crypto certificate name {cert_name}")
        if not result or result.get('status') != 'OK':
            self.logger.error(f"Failed to delete certificate: {result}")
            return False
        return True

    def save_config(self):
        """
        Save configuration to persistent storage
        :return: bool
        """
        self.logger.info("Saving configuration")
        result = self.execute_command("write memory")
        if not result or result.get('status') != 'OK':
            self.logger.error(f"Failed to save configuration: {result}")
            return False
        return True


def parse_cert_expiry(pem_file):
    """Parse certificate expiration date from PEM file"""
    try:
        from OpenSSL import crypto as c
        with open(pem_file, 'rb') as fh:
            cert = c.load_certificate(c.FILETYPE_PEM, fh.read())
        return datetime.strptime(cert.get_notAfter().decode('utf8'), "%Y%m%d%H%M%SZ")
    except ImportError:
        # Fall back to openssl command if pyOpenSSL not available
        import subprocess
        result = subprocess.run(
            ['openssl', 'x509', '-enddate', '-noout', '-in', pem_file],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Parse "notAfter=Nov 24 22:30:18 2026 GMT"
            date_str = result.stdout.strip().split('=')[1]
            return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
    return None


def read_pem_file(filepath):
    """Read PEM file and return contents"""
    with open(filepath, 'r') as f:
        return f.read().strip()


def main():
    parser = argparse.ArgumentParser(
        description='Update NVIDIA Onyx switch SSL certificate via JSON API'
    )
    parser.add_argument('--hostname', required=True,
                        help='Onyx switch hostname or IP address')
    parser.add_argument('--username', required=True,
                        help='Switch username with admin access')
    parser.add_argument('--password', required=True,
                        help='Switch password')
    parser.add_argument('--cert-name', default='custom-cert',
                        help='Name for the certificate on the switch (default: custom-cert)')
    parser.add_argument('--key-file', required=True,
                        help='X.509 Private key filename (PEM format)')
    parser.add_argument('--cert-file', required=True,
                        help='X.509 Certificate filename (PEM format)')
    parser.add_argument('--force-update', action='store_true',
                        help='Force update even if certificate seems current')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save configuration after update')
    parser.add_argument('--quiet', action='store_true',
                        help='Minimal output')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = parser.parse_args()

    # Validate files exist
    if not os.path.isfile(args.key_file):
        print(f"ERROR: --key-file '{args.key_file}' doesn't exist!")
        sys.exit(2)
    if not os.path.isfile(args.cert_file):
        print(f"ERROR: --cert-file '{args.cert_file}' doesn't exist!")
        sys.exit(2)

    # Create updater
    updater = OnyxCertUpdater(
        hostname=args.hostname,
        username=args.username,
        password=args.password,
        debug=args.debug
    )

    # Login
    if not updater.login():
        print("ERROR: Login failed!")
        sys.exit(2)

    # Get current certificate info
    current_info = updater.get_current_cert_info()
    if current_info and not args.quiet:
        print(f"Current HTTPS certificate: {current_info.get('cert_name')}")

    # Check if update is needed (compare expiry dates)
    new_expiry = parse_cert_expiry(args.cert_file)
    if new_expiry and not args.quiet:
        print(f"New certificate expires: {new_expiry}")

    # Check existing cert with same name
    existing_validity = updater.get_cert_validity(args.cert_name)
    if existing_validity and not args.force_update:
        existing_expiry_str = existing_validity.get('expires')
        if existing_expiry_str:
            existing_expiry = datetime.strptime(existing_expiry_str, "%Y/%m/%d %H:%M:%S")
            if new_expiry and existing_expiry == new_expiry:
                print("Certificate already up to date (expiry dates match)")
                sys.exit(0)

    # Read certificate and key files
    cert_pem = read_pem_file(args.cert_file)
    key_pem = read_pem_file(args.key_file)

    # Delete existing certificate with same name if it exists
    if existing_validity:
        if not args.quiet:
            print(f"Removing existing certificate '{args.cert_name}'")
        updater.delete_certificate(args.cert_name)

    # Import new certificate
    if not updater.import_certificate(args.cert_name, cert_pem, key_pem):
        print("ERROR: Failed to import certificate!")
        sys.exit(2)

    # Set as HTTPS certificate
    if not updater.set_https_certificate(args.cert_name):
        print("ERROR: Failed to set HTTPS certificate!")
        sys.exit(2)

    # Save configuration
    if not args.no_save:
        if not updater.save_config():
            print("WARNING: Failed to save configuration!")

    if not args.quiet:
        print("Certificate updated successfully!")

    # Verify
    new_info = updater.get_current_cert_info()
    if new_info and not args.quiet:
        print(f"HTTPS certificate is now: {new_info.get('cert_name')}")

    sys.exit(0)


if __name__ == "__main__":
    main()
