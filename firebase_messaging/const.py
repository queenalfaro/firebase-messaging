"""Constants module."""

GCM_REGISTER_URL = "https://android.clients.google.com/c2dm/register3"
GCM_CHECKIN_URL = "https://android.clients.google.com/checkin"
GCM_SERVER_KEY_BIN = (
    b"\x04\x33\x94\xf7\xdf\xa1\xeb\xb1\xdc\x03\xa2\x5e\x15\x71\xdb\x48\xd3"
    + b"\x2e\xed\xed\xb2\x34\xdb\xb7\x47\x3a\x0c\x8f\xc4\xcc\xe1\x6f\x3c"
    + b"\x8c\x84\xdf\xab\xb6\x66\x3e\xf2\x0c\xd4\x8b\xfe\xe3\xf9\x76\x2f"
    + b"\x14\x1c\x63\x08\x6a\x6f\x2d\xb1\x1a\x95\xb0\xce\x37\xc0\x9c\x6e"
)
# urlsafe b64 encoding of the binary key with = padding removed
GCM_SERVER_KEY_B64 = (
    "BDOU99-h67HcA6JeFXHbSNMu7e2yNNu3RzoM"
    + "j8TM4W88jITfq7ZmPvIM1Iv-4_l2LxQcYwhqby2xGpWwzjfAnG4"
)

FCM_SUBSCRIBE_URL = "https://fcm.googleapis.com/fcm/connect/subscribe/"
FCM_SEND_URL = "https://fcm.googleapis.com/fcm/send/"

FCM_API = "https://fcm.googleapis.com/v1/"
FCM_REGISTRATION = "https://fcmregistrations.googleapis.com/v1/"
FCM_INSTALLATION = "https://firebaseinstallations.googleapis.com/v1/"
AUTH_VERSION = "FIS_v2"
SDK_VERSION = "w:0.6.6"
ANDROID_SDK_VERSION = "a:17.0.0"

DOORBELLS_ENDPOINT = "/clients_api/doorbots/{0}"

MCS_VERSION = 41
MCS_HOST = "mtalk.google.com"
MCS_PORT = 5228
MCS_SELECTIVE_ACK_ID = 12
MCS_STREAM_ACK_ID = 13

ANDROID_USER_AGENT = "Android-GCM/1.5"
ANDROID_OS_VERSION = "28"
ANDROID_GMS_VERSION = "220920023"
ANDROID_CLI_VERSION = "fcm-25.0.1"
ANDROID_TSDK_VERSION = "36"