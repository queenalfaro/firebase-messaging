
import logging

from firebase_messaging.fcmpushclient import FcmPushClient, ErrorType
from firebase_messaging.proto.mcs_pb2 import DataMessageStanza
from .android_fcmregister import AndroidRegisterConfig, AndroidFcmRegister

_logger = logging.getLogger(__name__)


class AndroidPushClient(FcmPushClient):
    fcm_config: AndroidRegisterConfig

    async def checkin_or_register(self) -> str:
        self.register = AndroidFcmRegister(
            self.fcm_config,
            self.credentials,
            self.credentials_updated_callback,
            http_client_session=self._http_client_session,
        )
        self.credentials = await self.register.checkin_or_register()
        await self.register.close()
        return self.credentials["fcm"]["registration"]["token"]

    def _handle_data_message(self, msg: DataMessageStanza) -> None:
        if (
            self._app_data_by_key(msg, "message_type", do_not_raise=True)
            == "deleted_messages"
        ):
            return

        has_crypto = any(x.key == "crypto-key" for x in msg.app_data)

        if not has_crypto:
            print("UNCRYPTED")
            app_data_dict = {x.key: x.value for x in msg.app_data}
            app_data_dict["_raw_msg"] = msg
            
            try:
                self.callback(app_data_dict, msg.persistent_id, self.callback_context)
                self._reset_error_count(ErrorType.NOTIFY)
            except Exception as e:
                self._try_increment_error_count(ErrorType.NOTIFY)
                logging.error(e, exc_info=True)
        else:
            print("CRYPTED")
            super()._handle_data_message(msg)
