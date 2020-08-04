import jpush
from jpush import common
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

from wallpaper.state import CustomResponse

_jpush = jpush.JPush('9e7c6b15842a8229f1163ad4', '7f2f2ce98b6ebd7ce8da0e3b')
_jpush.set_logging("DEBUG")


def alias():
    push = _jpush.create_push()
    alias = ["alias1", "alias2"]
    alias1 = {"alias": alias}
    print(alias1)
    push.audience = jpush.audience(
        jpush.tag("tag1", "tag2"),
        alias1
    )

    push.notification = jpush.notification(alert="Hello world with audience!")
    push.platform = jpush.all_
    print(push.payload)
    push.send()


def all():
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="!hello python jpush api")
    push.platform = jpush.all_
    try:
        response = push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn")
    except common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def audience(request):
    # register_id = request.POST.get('register_id')
    newsId = request.POST.get('newsId')
    id = request.POST.get('id')
    push = _jpush.create_push()
    push.platform = jpush.all_
    push.audience = jpush.all_
    # push.audience = {
    #     "registration_id": [register_id]
    # }
    push.notification = {
        "android": {
            "alert": "hello, JPush!",
            "title": "JPush test",
            # "intent": {
            #     "url": "dmczt://innodealing.com/main",
            # },
            "extras": {
                "newsId": newsId,
                "id": id
            },
            "uri_activity": 'com.innodealing.raymonkey.mvp.ui.activity.MainActivity',
        },
        "ios": {
            "alert": "hello, JPush!",
            "extras": {
                "newsId": newsId,
                "id": id
            },
        }
    }
    print(push.payload)
    push.send()
    return CustomResponse()


def notification():
    push = _jpush.create_push()

    push.audience = jpush.all_
    push.platform = jpush.all_

    ios = jpush.ios(alert="Hello, IOS JPush!", sound="a.caf", extras={'k1': 'v1'})
    android = jpush.android(alert="Hello, Android msg", priority=1, style=1, alert_type=1, big_text='jjjjjjjjjj',
                            extras={'k1': 'v1'})

    push.notification = jpush.notification(alert="Hello, JPush!", android=android, ios=ios)

    # pprint (push.payload)
    result = push.send()


def options():
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="Hello, world!")
    push.platform = jpush.all_
    push.options = {"time_to_live": 86400, "sendno": 12345, "apns_production": True}
    push.send()


def platfrom_msg():
    push = _jpush.create_push()
    push.audience = jpush.all_
    ios_msg = jpush.ios(alert="Hello, IOS JPush!", badge="+1", sound="a.caf", extras={'k1': 'v1'})
    android_msg = jpush.android(alert="Hello, android msg")
    push.notification = jpush.notification(alert="Hello, JPush!", android=android_msg, ios=ios_msg)
    push.message = jpush.message("content", extras={'k2': 'v2', 'k3': 'v3'})
    push.platform = jpush.all_
    push.send()


def silent():
    push = _jpush.create_push()
    push.audience = jpush.all_
    ios_msg = jpush.ios(alert="Hello, IOS JPush!", badge="+1", extras={'k1': 'v1'}, sound_disable=True)
    android_msg = jpush.android(alert="Hello, android msg")
    push.notification = jpush.notification(alert="Hello, JPush!", android=android_msg, ios=ios_msg)
    push.platform = jpush.all_
    push.send()


def sms():
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="a sms message from python jpush api")
    push.platform = jpush.all_
    push.smsmessage = jpush.smsmessage("a sms message from python jpush api", 0)
    print(push.payload)
    push.send()


def validate():
    push = _jpush.create_push()
    push.audience = jpush.all_
    push.notification = jpush.notification(alert="Hello, world!")
    push.platform = jpush.all_
    push.send_validate()
