from django.db import models
from django.contrib.auth.models import User



class EBooksModel(models.Model):
    title = models.CharField(max_length=80)
    summary = models.TextField(max_length=2000)
    pages = models.CharField(max_length=80)
    pdf = models.FileField(upload_to='pdfs/')
    author = models.CharField(max_length=80)
    category = models.CharField(max_length=80)
    author_id = models.IntegerField(default=0)

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BORROWED', 'Borrowed'),
        ('RESERVED', 'Reserved'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )
    borrower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='borrowed_books'
    )
    borrow_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class BorrowRecord(models.Model):
    book = models.ForeignKey(EBooksModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    class Meta:
        ordering = ['-borrow_date']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('LIBRARIAN', 'Librarian'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"