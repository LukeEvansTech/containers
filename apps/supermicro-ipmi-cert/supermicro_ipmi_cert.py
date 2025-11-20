#!/usr/bin/env python3

"""
Supermicro IPMI Certificate Deployment Tool
Deploys certificates to Supermicro IPMI interfaces via environment variables

Designed for use with Cert Warden post-processing:
https://www.certwarden.com/docs/using_certificates/post_process_bin/
"""

import os
import sys
import re
import requests
import logging
import json
import time
from base64 import b64encode
from datetime import datetime
from typing import Optional
import xml.etree.ElementTree as etree
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5.0


class IPMIUpdater:
    """IPMI certificate updater for a single host"""

    def __init__(self, ipmi_url: str, model: str, username: str, password: str):
        self.ipmi_url = ipmi_url.rstrip('/')
        self.model = model.upper()
        self.username = username
        self.password = password
        self.session = requests.session()

        # Handle H13 as X12/X13
        if self.model == 'H13':
            self.model = 'X12'
            logger.info("Treating H13 model as X12")

        # IPMI URLs
        self.login_url = f'{ipmi_url}/cgi/login.cgi'
        self.cert_info_url = f'{ipmi_url}/cgi/ipmi.cgi'
        self.upload_cert_url = f'{ipmi_url}/cgi/upload_ssl.cgi'
        self.url_redirect_template = f'{ipmi_url}/cgi/url_redirect.cgi?url_name=%s'
        self.reboot_url = f'{ipmi_url}/cgi/BMCReset.cgi'

        # Redfish URLs for X12/X13/H13
        if self.model in ['X12', 'X13']:
            self.login_url = f'{ipmi_url}/redfish/v1/SessionService/Sessions'
            self.cert_info_url = f'{ipmi_url}/redfish/v1/UpdateService/Oem/Supermicro/SSLCert'
            self.upload_cert_url = f'{ipmi_url}/redfish/v1/UpdateService/Oem/Supermicro/SSLCert/Actions/SmcSSLCert.Upload'
            self.reboot_url = f'{ipmi_url}/redfish/v1/Managers/1/Actions/Manager.Reset'

        self.use_b64encoded_login = True
        self._csrf_token = None
        self._auth_token = None

    def get_csrf_token(self, url_name):
        if self._csrf_token is not None:
            return self._csrf_token

        page_url = self.url_redirect_template % url_name
        result = self.session.get(page_url, verify=False)
        result.raise_for_status()

        match = re.search(r'SmcCsrfInsert\s*\("CSRF_TOKEN",\s*"([^"]*)"\);', result.text)
        if match:
            return match.group(1)

    def get_csrf_headers(self, url_name):
        page_url = self.url_redirect_template % url_name

        headers = {
            "Origin": self.ipmi_url,
            "Referer": page_url,
        }
        csrf_token = self.get_csrf_token(url_name)
        if csrf_token is not None:
            headers["CSRF_TOKEN"] = csrf_token

        return headers

    def get_xhr_headers(self, url_name):
        headers = self.get_csrf_headers(url_name)
        headers["X-Requested-With"] = "XMLHttpRequest"
        return headers

    def login(self) -> bool:
        """Log into IPMI interface"""
        logger.info("Logging into IPMI...")

        if self.model not in ["X12", "X13"]:
            # Legacy login
            if self.use_b64encoded_login:
                login_data = {
                    'name': b64encode(self.username.encode("UTF-8")),
                    'pwd': b64encode(self.password.encode("UTF-8")),
                    'check': '00'
                }
            else:
                login_data = {
                    'name': self.username,
                    'pwd': self.password
                }

            try:
                result = self.session.post(self.login_url, login_data, timeout=REQUEST_TIMEOUT, verify=False)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                return False
            if not result.ok:
                return False
            if '/cgi/url_redirect.cgi?url_name=mainmenu' not in result.text:
                return False

            # Set mandatory cookies
            url_parts = urlparse(self.ipmi_url)
            mandatory_cookies = {
                'langSetFlag': '0',
                'language': 'English'
            }
            for cookie_name, cookie_value in mandatory_cookies.items():
                self.session.cookies.set(cookie_name, cookie_value, domain=url_parts.hostname)

            return True

        else:
            # Redfish login for X12/X13/H13
            login_data = {
                'UserName': self.username,
                'Password': self.password
            }

            request_headers = {'Content-Type': 'application/json'}
            try:
                result = self.session.post(self.login_url, data=json.dumps(login_data),
                                         headers=request_headers, timeout=REQUEST_TIMEOUT, verify=False)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                return False
            if not result.ok:
                logger.error(f"Login failed with status: {result.status_code}")
                return False

            # Store auth token for X12/X13/H13
            self._auth_token = result.headers.get('X-Auth-Token')
            return True if self._auth_token else False

    def get_ipmi_cert_info(self) -> Optional[dict]:
        """Get current certificate info from IPMI"""
        logger.info("Checking current certificate...")

        if self.model in ["X12", "X13"]:
            request_headers = {
                'Content-Type': 'application/json',
                'X-Auth-Token': self._auth_token
            }

            try:
                r = self.session.get(self.cert_info_url, headers=request_headers, verify=False, timeout=REQUEST_TIMEOUT)
            except Exception as e:
                logger.error(f"Error getting cert info: {e}")
                return None
            if not r.ok:
                return None

            try:
                data = r.json()
                valid_from = datetime.strptime(data['VaildFrom'].rstrip(re.split('\d{4}', data['VaildFrom'])[1]), r"%b %d %H:%M:%S %Y")
                valid_until = datetime.strptime(data['GoodTHRU'].rstrip(re.split('\d{4}', data['GoodTHRU'])[1]), r"%b %d %H:%M:%S %Y")

                return {
                    'has_cert': True,
                    'valid_from': valid_from,
                    'valid_until': valid_until
                }
            except Exception as e:
                logger.error(f"Error parsing cert info: {e}")
                return None

        # Legacy certificate info
        headers = self.get_xhr_headers("config_ssl")
        cert_info_data = self._get_op_data('SSL_STATUS.XML', '(0,0)')

        try:
            result = self.session.post(self.cert_info_url, cert_info_data, headers=headers, timeout=REQUEST_TIMEOUT, verify=False)
        except Exception:
            return None
        if not result.ok:
            return None

        try:
            root = etree.fromstring(result.text)
            status = root.findall('.//SSL_INFO/STATUS')
            if not status:
                return None
            status = status[0]
            has_cert = bool(int(status.get('CERT_EXIST')))
            if has_cert:
                valid_from = datetime.strptime(status.get('VALID_FROM'), r"%b %d %H:%M:%S %Y")
                valid_until = datetime.strptime(status.get('VALID_UNTIL'), r"%b %d %H:%M:%S %Y")

                return {
                    'has_cert': has_cert,
                    'valid_from': valid_from,
                    'valid_until': valid_until
                }
        except Exception as e:
            logger.error(f"Error parsing cert info: {e}")
            return None

    def upload_cert(self, cert_data: bytes, key_data: bytes) -> bool:
        """Upload certificate to IPMI"""
        logger.info("Uploading certificate...")

        if self.model in ['X12', 'X13']:
            # For X12/X13/H13, only send the server certificate, not the full chain
            substr = b'-----END CERTIFICATE-----\n'
            cert_only = cert_data.split(substr)[0] + substr

            files_to_upload = {
                'cert_file': cert_only,
                'key_file': key_data
            }

            request_headers = {'X-Auth-Token': self._auth_token}

            try:
                result = self.session.post(self.upload_cert_url, files=files_to_upload,
                                         headers=request_headers, timeout=REQUEST_TIMEOUT, verify=False)
            except Exception as e:
                logger.error(f"Upload error: {e}")
                return False

            if 'SSL certificate and private key were successfully uploaded' not in result.text:
                logger.error(f"Upload failed: {result.text}")
                return False

            return True

        else:
            # Legacy upload
            files_to_upload = self._get_upload_data(cert_data, key_data)

            headers = self.get_csrf_headers("config_ssl")
            csrf_token = self.get_csrf_token("config_ssl")
            csrf_data = {}
            if csrf_token is not None:
                csrf_data["CSRF_TOKEN"] = csrf_token

            try:
                result = self.session.post(self.upload_cert_url, csrf_data, files=files_to_upload,
                                         headers=headers, timeout=REQUEST_TIMEOUT, verify=False)
            except Exception:
                return False
            if not result.ok:
                return False

            if 'Content-Type' not in result.headers.keys() or result.headers['Content-Type'] != 'text/html':
                return False
            if 'CONFPAGE_RESET' not in result.text:
                return False

            return True

    def _get_op_data(self, op, r):
        """Get operation data for legacy IPMI"""
        if self.model == "X11":
            data = {'op': op}
            if r is not None:
                data['r'] = r
            data['_'] = ''
            return data
        else:
            timestamp = datetime.utcnow().strftime('%a %d %b %Y %H:%M:%S GMT')
            data = {'time_stamp': timestamp}
            if r is not None:
                data[op] = r
            return data

    def _get_upload_data(self, cert_data, key_data):
        """Get upload data format based on model"""
        if self.model == "X11":
            return [
                ('cert_file', ('fullchain.pem', cert_data, 'application/octet-stream')),
                ('key_file', ('privkey.pem', key_data, 'application/octet-stream'))
            ]
        elif self.model == "X10":
            return [
                ('cert_file', ('cert.pem', cert_data, 'application/octet-stream')),
                ('key_file', ('privkey.pem', key_data, 'application/octet-stream'))
            ]
        else:  # X9
            return [
                ('sslcrt_file', ('cert.pem', cert_data, 'application/octet-stream')),
                ('privkey_file', ('privkey.pem', key_data, 'application/octet-stream'))
            ]

    def reboot_ipmi(self) -> bool:
        """Reboot IPMI to apply changes"""
        logger.info("Rebooting IPMI...")

        if self.model in ['X12', 'X13']:
            request_headers = {'X-Auth-Token': self._auth_token}

            try:
                result = self.session.post(self.reboot_url, headers=request_headers,
                                         timeout=REQUEST_TIMEOUT, verify=False)
            except Exception:
                return False
            if not result.ok:
                return False

            return True
        else:
            # Legacy reboot
            headers = self.get_xhr_headers("config_ssl")
            reboot_data = self._get_op_data('main_bmcreset', None)

            try:
                result = self.session.post(self.reboot_url, reboot_data, headers=headers,
                                         timeout=REQUEST_TIMEOUT, verify=False)
            except Exception:
                return False
            if not result.ok:
                return False

            return True


def get_env_or_exit(var_name: str, description: str) -> str:
    """Get environment variable or exit with error"""
    value = os.environ.get(var_name)
    if not value:
        logger.error(f"Missing required environment variable: {var_name} ({description})")
        sys.exit(1)
    return value


def main():
    logger.info("=== Supermicro IPMI Certificate Deployment ===")

    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Get required environment variables
    ipmi_url = get_env_or_exit('IPMI_URL', 'IPMI interface URL')
    model = get_env_or_exit('IPMI_MODEL', 'Board model (X9, X10, X11, X12, X13, H13)')
    username = get_env_or_exit('IPMI_USERNAME', 'IPMI username')

    # Password can come from environment variable
    password_env_var = os.environ.get('IPMI_PASSWORD_ENV')
    if password_env_var:
        password = os.environ.get(password_env_var)
        if not password:
            logger.error(f"Password environment variable {password_env_var} is not set")
            sys.exit(1)
    else:
        password = get_env_or_exit('IPMI_PASSWORD', 'IPMI password')

    # Get certificate data from Cert Warden
    cert_pem = get_env_or_exit('CERTIFICATE_PEM', 'Certificate in PEM format')
    key_pem = get_env_or_exit('PRIVATE_KEY_PEM', 'Private key in PEM format')

    # Optional: no reboot flag
    no_reboot = os.environ.get('IPMI_NO_REBOOT', 'false').lower() in ('true', '1', 'yes')

    logger.info(f"Target: {ipmi_url}")
    logger.info(f"Model: {model}")
    logger.info(f"Username: {username}")
    logger.info(f"Reboot: {'No' if no_reboot else 'Yes'}")

    # Convert PEM strings to bytes
    cert_data = cert_pem.encode('utf-8')
    key_data = key_pem.encode('utf-8')

    # Clean certificate data (remove DH params if present)
    cert_data = b'\n'.join(re.findall(b'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', cert_data, re.DOTALL)) + b'\n'

    # Create updater and deploy
    updater = IPMIUpdater(ipmi_url, model, username, password)

    try:
        # Login
        if not updater.login():
            logger.error("Login failed")
            sys.exit(1)

        logger.info("Login successful")

        # Check current certificate
        cert_info = updater.get_ipmi_cert_info()
        if cert_info and cert_info.get('has_cert'):
            logger.info(f"Current certificate valid until: {cert_info['valid_until']}")

        # Upload certificate
        if not updater.upload_cert(cert_data, key_data):
            logger.error("Certificate upload failed")
            sys.exit(1)

        logger.info("Certificate uploaded successfully")

        # Verify upload
        new_cert_info = updater.get_ipmi_cert_info()
        if new_cert_info and new_cert_info.get('has_cert'):
            logger.info(f"New certificate valid until: {new_cert_info['valid_until']}")

        # Reboot if requested
        if not no_reboot:
            if updater.reboot_ipmi():
                logger.info("IPMI reboot initiated")
            else:
                logger.warning("Reboot failed, but certificate was uploaded")
        else:
            logger.info("Skipping reboot (manual reboot required)")

        logger.info("=== Deployment completed successfully ===")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
