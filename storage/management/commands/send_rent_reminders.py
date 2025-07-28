from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from storage.models import Order
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = ('Отправлять пользователям электронные'
            ' письма с напоминаниями об аренде')

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        notify_days = [30, 14, 7, 3]
        notify_days = [1, 30, 60, 90, 120, 150, 180]

        for days_left in notify_days:
            target_date = today + timedelta(days=days_left)

            orders = Order.objects.filter(end_storage=target_date)

            self.stdout.write(f'Найдено заказов: {orders.count()}')

            for order in orders:
                user = order.cuser
                if user.email:
                    send_mail(
                        subject=f'Напоминание: аренда заканчивается через {days_left} дн.',
                        message=(
                            f'Здравствуйте, {user.first_name}!\n\n'
                            f'Срок аренды бокса №{order.id} заканчивается '
                            f'{order.end_storage.strftime("%d.%m.%Y")}.\n'
                            f'Пожалуйста, продлите аренду или заберите вещи до этой даты.'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Напоминание отправлено: {user.email}, заказ #{order.id}, осталось {days_left} дн.'
                    ))

        for days_overdue in notify_days:
            overdue_date = today - timedelta(days=days_overdue)

            orders = Order.objects.filter(end_storage=overdue_date)

            for order in orders:
                user = order.cuser
                if user.email:
                    send_mail(
                        subject=f'Просрочка: {days_overdue} дней с окончания аренды',
                        message=(
                            f'Здравствуйте, {user.first_name}!\n\n'
                            f'Срок аренды бокса №{order.id} завершился {order.end_storage.strftime("%d.%m.%Y")}.\n'
                            f'Ваши вещи будут храниться дополнительно 6 месяцев '
                            f'согласно условиям хранения по повышенному тарифу.\n'
                            f'В случаи если вы их не заберете - вы их потеряете.'
                            f'Свяжитесь с нами срочно!.'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.WARNING(
                        f'Отправлено уведомление ({days_overdue} дней просрочки): {user.email}, заказ #{order.id}'
                    ))
