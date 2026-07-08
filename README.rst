==================
Firebase Messaging
==================

.. image:: https://badge.fury.io/py/firebase-messaging.svg
    :alt: PyPI Version
    :target: https://badge.fury.io/py/firebase-messaging

.. image:: https://github.com/sdb9696/firebase-messaging/actions/workflows/ci.yml/badge.svg?branch=main
    :alt: Build Status
    :target: https://github.com/sdb9696/firebase-messaging/actions/workflows/ci.yml?branch=main

.. image:: https://coveralls.io/repos/github/sdb9696/firebase-messaging/badge.svg?branch=main
    :alt: Coverage
    :target: https://coveralls.io/github/sdb9696/firebase-messaging?branch=main

.. image:: https://readthedocs.org/projects/firebase-messaging/badge/?version=latest
    :alt: Documentation Status
    :target: https://firebase-messaging.readthedocs.io/?badge=latest

.. image:: https://img.shields.io/pypi/pyversions/firebase-messaging.svg
    :alt: Py Versions
    :target: https://pypi.python.org/pypi/firebase-messaging#

A library to subscribe to GCM/FCM and receive notifications (Web and Android) within a python application.

When should I use `firebase-messaging` ?
----------------------------------------

- I want to **receive** push notifications sent using Firebase Cloud Messaging in a python application.

When should I not use `firebase-messaging` ?
--------------------------------------------

- I want to **send** push notifications (use the firebase SDK instead)
- My application is running on a FCM supported platform (Android, iOS, Web).

Install
-------

PyPi::

    $ pip install firebase-messaging


Requirements
------------

- Firebase configuration to receive notifications

Usage
-----

Must be run inside an asyncio event loop.

python::

    from firebase_messaging import FcmPushClient, FcmRegisterConfig

    def on_notification(obj, notification, data_message):
        # Do something with the notification
        pass

    credentials = None  # Start off with none or load from previous save
    def on_credentials_updated(creds):
        # save the credentials to a file here for future use

    fcm_config = FcmRegisterConfig(fcm-project-id, fcm-app-id, fcm-api-key, fcm-message-sender-id)
    pc = FcmPushClient(on_notification, fcm_config, credentials, on_credentials_updated)
    fcm_token = await pc.checkin_or_register()

    await pc.start()

    # Adapt the following for your usage
    while some_condition_to_keep_listening:
        asyncio.sleep(2)


Android Client Support
----------------------

This fork introduces native support for registering and connecting as an **Android client** rather than a Web Push client. This is useful for mimicking Android devices to receive unencrypted, raw FCM payloads directly.

Key Additions
~~~~~~~~~~~~~

* **``AndroidRegisterConfig``**: Extends ``FcmRegisterConfig`` to hold Android-specific metadata (e.g., Package/Bundle ID, SHA1 Certificate Fingerprint, Android GMS/OS versions).
* **``AndroidFcmRegister``**: Performs full GCM check-in, Firebase installation, and GCM device registration using Android credentials.
* **``AndroidPushClient``**: Connects to the MCS service as an Android client. Unlike Web Push, it directly decodes and forwards raw, unencrypted payloads.

Usage Example
~~~~~~~~~~~~~

Ensure you import the classes from the Android-specific modules::

    import asyncio
    import logging
    from firebase_messaging.android_fcmpushclient import AndroidPushClient
    from firebase_messaging.android_fcmregister import AndroidRegisterConfig

    # Callback function triggered when a push notification is received
    def on_notification(data, persistent_id, context):
        print(f"Received notification: {data}")

    def credentials_updated_callback(new_creds):
        # Save these credentials locally to avoid re-registering on every launch
        print("Credentials updated:", new_creds)

    async def main():
        # Full configuration block with non-constant parameters replaced by placeholders
        fcm_config = AndroidRegisterConfig(
            project_id="your-firebase-project-id",
            app_id="1:123456789012:android:abcdef1234567890",
            api_key="AIzaSyDummY_Key_For_Example_Only_abc123",
            messaging_sender_id="123456789012",
            bundle_id="com.example.androidapp",
            cert_sha1="A1B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6A1B2",
            app_name_hash="AbCdEfGhIjKlMnOpQrStUvWxYz1",
            app_ver="1000",
            app_ver_name="1.0.0",
            # Default environment parameters (can be omitted to use default constants)
            osv="28",
            cliv="fcm-25.0.1",
            gmsv="220920023",
            target_ver="36"
        )

        client = AndroidPushClient(
            callback=on_notification,
            fcm_config=fcm_config,
            credentials=None,  # Pass previously stored credentials dict here if available
            credentials_updated_callback=credentials_updated_callback,
        )

        # Register the device and retrieve the FCM token
        fcm_token = await client.checkin_or_register()
        print(f"FCM Android Token: {fcm_token}")

        # Connect to MCS and start listening for push notifications
        await client.start()

        while True:
            await asyncio.sleep(1)

    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())


Attribution
-----------

Code originally based on typescript/node implementation by
`Matthieu Lemoine <https://github.com/MatthieuLemoine/push-receiver>`_.
See `this blog post <https://medium.com/@MatthieuLemoine/my-journey-to-bring-web-push-support-to-node-and-electron-ce70eea1c0b0>`_ for more details.

Converted to python by
`lolisamurai <https://github.com/Francesco149/push_receiver>`_

http decryption logic in decrypt.py by
`Martin Thomson <https://github.com/web-push-libs/encrypted-content-encoding>`_
