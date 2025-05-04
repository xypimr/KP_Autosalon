# salon/middleware.py

import time
from django.utils.deprecation import MiddlewareMixin
from .models import AccessLog

class AccessLogMiddleware(MiddlewareMixin):
    """
    Записывает в таблицу AccessLog каждый запрос с информацией
    о пользователе, IP, пути, методе и статусе ответа.
    """

    def process_request(self, request):
        # Сохраним время начала обработки, чтобы при желании вычислять длительность
        request._start_time = time.time()

    def process_response(self, request, response):
        try:
            # Получаем пользователя; если не аутентифицирован — None
            user = request.user if request.user.is_authenticated else None

            # IP-адрес: учитываем возможные прокси через X-Forwarded-For
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = (x_forwarded_for.split(',')[0]
                  if x_forwarded_for else request.META.get('REMOTE_ADDR'))

            # Формируем запись
            AccessLog.objects.create(
                user=user,
                ip_address=ip,
                path=request.get_full_path(),
                method=request.method,
                status_code=response.status_code,
            )
        except Exception:
            # Игнорируем любые ошибки in logging
            pass

        return response
