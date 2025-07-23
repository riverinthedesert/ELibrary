from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('explore', views.explore, name='explore'),
  path('register', views.Registers, name='register'),
  path('login', views.Login, name='login'),
  path('addBook/<int:user_id>', views.addBook, name='addBook'),
  path('addBook', views.addBook, name='addBook'),
  path('contri/<int:user_id>', views.contri, name='contri'),
  path('logout', views.logout, name='logout'),
  path('deleteBook/<int:book_id>', views.deleteBook, name='deleteBook'),
  path('editBook/<int:book_id>', views.editBook, name='editBook'),
  path('viewBook/<int:book_id>', views.viewBook, name='viewBook'),
  path('search/', views.search_books, name='search_books'),
  path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
  path('return/<int:book_id>/', views.return_book, name='return_book'),
  path('recommend/<int:book_id>/', views.book_recommendations, name='book_recommendations'),
  path('profile/', views.user_profile, name='user_profile'),
  path('borrow-records/', views.all_borrow_records, name='all_borrow_records'),
]