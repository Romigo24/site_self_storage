from django.core.mail import send_mail

def send_rent_reminder(order, days_left):
    subject = f'Напоминание: аренда заканчивается через {days_left} день(дней)'
    message = (
        f'Здравствуйте, {order.cuser.first_name}!\n\n'
        f'Срок вашей аренды заканчивается {order.end_storage.strftime("%d.%m.%Y")}.\n'
        f'Пожалуйста, продлите аренду или заберите вещи до этой даты.'
    )
    send_mail(
        subject,
        message,
        'noreply@example.com',
        [order.cuser.email],
        fail_silently=False
    )