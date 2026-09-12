from collections import defaultdict

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import Fee


@shared_task
def test_celery_task():
    return "Smart Campus Celery is working!"


@shared_task
def send_fee_reminders():
    today = timezone.localdate()

    pending_fees = Fee.objects.filter(
        status__in=["Pending", "Partial"],
        due_date__lte=today,
        student__email__isnull=False,
    ).exclude(
        student__email=""
    ).select_related("student")

    student_fees = defaultdict(list)

    for fee in pending_fees:
        balance = fee.amount - fee.paid_amount

        student_fees[fee.student.email].append({
            "student_name": fee.student.name,
            "fee_type": fee.fee_type,
            "amount": fee.amount,
            "paid_amount": fee.paid_amount,
            "balance": balance,
            "due_date": fee.due_date,
        })

    sent_count = 0

    for email, fees in student_fees.items():
        student_name = fees[0]["student_name"]

        message = f"Dear {student_name},\n\n"
        message += "This is a reminder regarding your pending fee(s):\n\n"

        for fee in fees:
            message += (
                f"Fee Type: {fee['fee_type']}\n"
                f"Total Amount: ₹{fee['amount']}\n"
                f"Paid Amount: ₹{fee['paid_amount']}\n"
                f"Remaining Amount: ₹{fee['balance']}\n"
                f"Due Date: {fee['due_date']}\n\n"
            )

        message += (
            "Please clear your pending fee(s) at the earliest.\n\n"
            "Regards,\n"
            "Smart Campus Administration"
        )

        send_mail(
            subject="Smart Campus - Fee Payment Reminder",
            message=message,
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        sent_count += 1

    return f"Fee reminders sent to {sent_count} student(s)."