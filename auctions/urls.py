from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>/<str:title>/", views.active_listing, name="active_listing"),
    path("category/<str:category>/<int:id>/<str:title>", views.category_activeListing, name="category_activeListing"),
    path("categories", views.categories, name="categories-page"),
    path("categories/<str:category>", views.categories_listing, name="list_category"),
    path("watchlist/", views.view_watchlist, name="view_watchlist"),
    path("watchlist/remove-to-watchlist/<int:listing_id>", views.Watchlist_remove, name="Watchlist_remove"),
    path("remove-to-watchlist/<int:listing_id>", views.remove_to_watchlist, name="remove_to_watchlist"),
    path("add-to-watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("create-listing", views.create_listing, name="create_listing"),
    path("listing/close-auction/<int:listing_id>", views.close_auction, name="close_auction"),
    path('listing/place-bid/<int:listing_id>', views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment")
]
