import os

import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.bottle import BottleIntegration

from bottle import route, run, HTTPResponse, HTTPError, BottleException

class BottleFail(BottleException):
    """Добавим красивый класс для наших исключений,
      чтобы видеть осмысленный текст в сентри"""
    def __init__(self, message):
      self.message = message

def set_sentry(init_string):
    """Функция инициализатор сентри, предназначена для разделения
    активации при запуске с консоли или из хероки, в хероки ползователь должен задать переменную
    SENTRY_INIT с валидной ссылкой для интеграции"""
    sentry_sdk.init(init_string,
                integrations=[ BottleIntegration() ])


@route("/success")
def get_success():
  return HTTPResponse(status="200 OK", body="<h2>Success route accessed<h2>")

@route("/fail")
def get_fail():
  try:
    raise BottleFail("Fail route occured!")
    #генерируем наше собственное осмысленное исключение
  except Exception as bf:
    capture_exception(bf)
    #Передаем данные об исключение обработчику sentry
  finally:
    return HTTPError(status="500 Route fail", body = "Fail route accessed")
    #Выводим штатную страничку - ошибку

if os.environ.get("APP_LOCATION") == "heroku":
    sentry_init = os.environ.get("SENTRY_INIT")
    if not sentry_init:
      raise BottleFail("Wrong sentry connection string!")
    set_sentry(sentry_init)
    run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        server="gunicorn",
        workers=3,
    )
else:
    set_sentry("")
    run(host="localhost", port=8080, debug=True)
