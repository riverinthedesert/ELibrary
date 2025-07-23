
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib import auth
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import EBooksModel, BorrowRecord, UserProfile
from .forms import EBooksForm, UserProfileForm
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np



def Registers(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        firstName = request.POST['first--name']
        lastName = request.POST['last--name']


        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return render(request, 'register.html')


        if User.objects.filter(username=email).exists():
            messages.info(request, 'Username already exists')
            return render(request, 'register.html')


        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=firstName,
                last_name=lastName
            )

            UserProfile.objects.create(user=user)


            auth_login(request, user)
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return render(request, 'register.html')
    else:
        return render(request, 'register.html')


def Login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']


        user = authenticate(username=email, password=password)

        if user is not None:

            auth_login(request, user)
            print('User logged in successfully')
            return redirect('home')
        else:
            messages.info(request, 'Invalid Credentials')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def home(request):
    return render(request, 'home.html')


def explore(request):
    edu_books = EBooksModel.objects.filter(category='Education')
    fiction_books = EBooksModel.objects.filter(category='Fiction')
    science_books = EBooksModel.objects.filter(category='Science')
    return render(request, 'explore.html',
                  {'edu_books': edu_books, 'fiction_books': fiction_books, 'science_books': science_books})


@login_required
def addBook(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = EBooksForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.author = user.first_name + " " + user.last_name
            book.author_id = user.id
            print(book.author)
            book.save()
            print()
            print()
            print(book.author)
            print("Book saved successfully")
            print()
            print()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = EBooksForm()
    return render(request, 'addBook.html', {'form': form})


def contri(request, user_id):
    books = EBooksModel.objects.filter(author_id=user_id)
    return render(request, 'contri.html', {'books': books})


def logout(request):
    auth.logout(request)
    return redirect('home')


def deleteBook(request, book_id):
    book = EBooksModel.objects.get(id=book_id)
    book.delete()
    return redirect('home')


def editBook(request, book_id):
    book = EBooksModel.objects.get(id=book_id)
    if request.method == 'POST':
        form = EBooksForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            print()
            print()
            print("Book updated successfully")
            print()
            print()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = EBooksForm(instance=book)

    if not (request.user.userprofile.role in ['ADMIN', 'LIBRARIAN'] or
            book.author_id == request.user.id):
        messages.error(request, 'You do not have permission to edit this book')
        return redirect('home')

    return render(request, 'editBook.html', {'form': form, 'book': book})


def viewBook(request, book_id):
    book = EBooksModel.objects.get(id=book_id)
    book.summary = book.summary.replace('\n', '<br/>')
    return render(request, 'viewBook.html', {'book': book})


def search_books(request):
    query = request.GET.get('q', '')
    if query:
        books = EBooksModel.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__icontains=query) |
            Q(summary__icontains=query)
        )
    else:
        books = EBooksModel.objects.all()
    return render(request, 'search_results.html', {'books': books, 'query': query})


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(EBooksModel, id=book_id)

    if book.status != 'AVAILABLE':
        messages.warning(request, 'Book is not available')
        return redirect('viewBook', book_id=book_id)


    book.status = 'BORROWED'
    book.borrower = request.user
    book.borrow_date = datetime.now().date()
    book.due_date = book.borrow_date + timedelta(days=14)  # 14天借阅期
    book.save()


    BorrowRecord.objects.create(
        book=book,
        user=request.user
    )

    messages.success(request, f'Successfully borrowed "{book.title}", due on {book.due_date}')
    return redirect('viewBook', book_id=book_id)


@login_required
def return_book(request, book_id):
    book = get_object_or_404(EBooksModel, id=book_id)

    if book.status != 'BORROWED' or book.borrower != request.user:
        messages.warning(request, 'Cannot return this book')
        return redirect('viewBook', book_id=book_id)


    book.status = 'AVAILABLE'
    book.borrower = None
    book.borrow_date = None
    book.due_date = None
    book.save()


    record = BorrowRecord.objects.filter(book=book, user=request.user, return_date__isnull=True).first()
    if record:
        record.return_date = datetime.now().date()
        record.save()

    messages.success(request, f'"{book.title}" has been returned')
    return redirect('viewBook', book_id=book_id)


def book_recommendations(request, book_id):
    current_book = get_object_or_404(EBooksModel, id=book_id)
    all_books = EBooksModel.objects.exclude(id=book_id)


    books_data = [{
        'id': book.id,
        'text': f"{book.title} {book.author} {book.category} {book.summary}"
    } for book in all_books]


    books_data.insert(0, {
        'id': current_book.id,
        'text': f"{current_book.title} {current_book.author} {current_book.category} {current_book.summary}"
    })


    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([book['text'] for book in books_data])


    cosine_sim = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()


    similar_indices = cosine_sim.argsort()[-6:-1][::-1]
    recommended_books = [all_books[i - 1] for i in similar_indices if i > 0]

    return render(request, 'recommendations.html', {
        'current_book': current_book,
        'recommended_books': recommended_books
    })


@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)


    borrow_records = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')

    return render(request, 'user_profile.html', {
        'form': form,
        'borrow_records': borrow_records
    })



def viewBook(request, book_id):
    book = EBooksModel.objects.get(id=book_id)
    book.summary = book.summary.replace('\n', '<br/>')


    is_borrowed_by_user = False
    if request.user.is_authenticated:
        is_borrowed_by_user = book.borrower == request.user

    return render(request, 'viewBook.html', {
        'book': book,
        'is_borrowed_by_user': is_borrowed_by_user
    })


@login_required
def all_borrow_records(request):
    if not request.user.userprofile.role in ['LIBRARIAN', 'ADMIN']:
        return redirect('home')

    records = BorrowRecord.objects.all().order_by('-borrow_date')
    return render(request, 'borrow_records.html', {'records': records})