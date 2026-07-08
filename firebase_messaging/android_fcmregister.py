
from dataclasses import dataclass
import logging
import secrets
import time
from base64 import b64encode
from typing import Any

from aiohttp import ClientSession
from firebase_messaging.fcmpushclient import FcmPushClient, ErrorType
from firebase_messaging.fcmregister import FcmRegister, FcmRegisterConfig
from .const import (
    AUTH_VERSION,
    ANDROID_SDK_VERSION,
    FCM_INSTALLATION,
    GCM_REGISTER_URL,
    ANDROID_USER_AGENT,
    ANDROID_OS_VERSION,
    ANDROID_GMS_VERSION,
    ANDROID_CLI_VERSION,
    ANDROID_TSDK_VERSION,
)

_logger = logging.getLogger(__name__)


@dataclass
class AndroidRegisterConfig(FcmRegisterConfig):
    cert_sha1: str = ""
    app_name_hash: str = ""
    app_ver: str = ""
    app_ver_name: str = ""
    osv: str = ANDROID_OS_VERSION
    cliv: str = ANDROID_CLI_VERSION
    gmsv: str = ANDROID_GMS_VERSION
    target_ver: str = ANDROID_TSDK_VERSION


class AndroidFcmRegister(FcmRegister):
    config: AndroidRegisterConfig

    async def checkin_or_register(self) -> dict[str, Any]:
        if self.credentials and "gcm" in self.credentials:
            try:
                gcm_response = await self.gcm_check_in(
                    int(self.credentials["gcm"]["android_id"]),
                    int(self.credentials["gcm"]["security_token"]),
                )
                if gcm_response:
                    return self.credentials
            except Exception as e:
                _logger.warning("Verification of existing creds failed (%s). Re-register...", e)

        self.credentials = await self.register_android()
        if self.credentials_updated_callback:
            self.credentials_updated_callback(self.credentials)

        return self.credentials

    async def register_android(self) -> dict[str, Any]:
        keys = self.generate_keys()

        checkin_data = await self.gcm_check_in()
        if not checkin_data:
            raise RuntimeError("GCM Check-in failed")

        android_id = str(checkin_data["androidId"])
        security_token = str(checkin_data["securityToken"])

        installation = await self._fcm_install_android()
        if not installation:
            raise RuntimeError("Firebase Installation failed")

        fcm_token = await self._gcm_register_android(android_id, security_token, installation)
        if not fcm_token:
            raise RuntimeError("GCM register3 failed")

        res = {
            "keys": keys,
            "gcm": {
                "android_id": android_id,
                "security_token": security_token,
                "app_id": self.config.bundle_id,
            },
            "fcm": {
                "registration": {
                    "token": fcm_token
                }
            },
            "installation": installation,
            "config": {
                "bundle_id": self.config.bundle_id,
                "project_id": self.config.project_id,
                "vapid_key": self.config.vapid_key,
            },
        }
        return res

    async def _fcm_install_android(self) -> dict | None:
        fid = bytearray(secrets.token_bytes(17))
        fid[0] = 0b01110000 + (fid[0] % 0b00010000)
        fid64 = b64encode(fid).decode()[:22]

        headers = {
            "Content-Type": "application/json",
            "X-Android-Package": self.config.bundle_id,
            "X-Android-Cert": self.config.cert_sha1,
            "x-goog-api-key": self.config.api_key,
        }
        payload = {
            "fid": fid64,
            "appId": self.config.app_id,
            "authVersion": AUTH_VERSION,
            "sdkVersion": ANDROID_SDK_VERSION,
        }
        url = f"{FCM_INSTALLATION}projects/{self.config.project_id}/installations"

        async with self._session.post(
            url=url,
            headers=headers,
            json=payload,
            timeout=self.CLIENT_TIMEOUT,
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "fid": data["fid"],
                    "auth_token": data["authToken"]["token"],
                    "refresh_token": data["refreshToken"],
                    "expires_in": int(data["authToken"]["expiresIn"][:-1]),
                    "created_at": time.time(),
                }
            else:
                text = await resp.text()
                _logger.error("Ошибка во время Android fcm_install: %s", text)
                return None

    async def _gcm_register_android(
        self, android_id: str, security_token: str, installation: dict
    ) -> str | None:
        body = {
            "X-subtype": self.config.messaging_sender_id,
            "sender": self.config.messaging_sender_id,
            "X-app_ver": self.config.app_ver,
            "X-osv": self.config.osv,
            "X-cliv": self.config.cliv,
            "X-gmsv": self.config.gmsv,
            "X-appid": installation["fid"],
            "X-scope": "*",
            "X-Goog-Firebase-Installations-Auth": installation["auth_token"],
            "X-gmp_app_id": self.config.app_id,
            "X-firebase-app-name-hash": self.config.app_name_hash,
            "X-app_ver_name": self.config.app_ver_name,
            "app": self.config.bundle_id,
            "device": android_id,
            "app_ver": self.config.app_ver,
            "gcm_ver": self.config.gmsv,
            "plat": "0",
            "cert": self.config.cert_sha1.lower(),
            "target_ver": self.config.target_ver,
        }
        headers = {
            "Authorization": f"AidLogin {android_id}:{security_token}",
            "App": self.config.bundle_id,
            "Gcm_ver": self.config.gmsv,
            "User-Agent": ANDROID_USER_AGENT,
        }
        url = GCM_REGISTER_URL

        async with self._session.post(
            url=url,
            headers=headers,
            data=body,
            timeout=self.CLIENT_TIMEOUT,
        ) as resp:
            resp_text = await resp.text()
            if resp.status == 200 and "Error" not in resp_text:
                fcm_token = resp_text.split("=", 1)[1].strip()
                return fcm_token
            else:
                _logger.error("Error during Android register3: %s", resp_text)
                return None
