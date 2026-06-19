from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from auctions.models import Categorie, Listing, Bid, Comment, Watchlist
from django import forms
from decimal import Decimal
from django.contrib import messages
from . models import User


def index(request):
    return render(request, "auctions/index.html", {
        "listing":Listing.objects.all().order_by('-created_at')
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def categories(request):
    return render(request, 'auctions/categories.html', {
        "category": Categorie.objects.all()
    })

def active_listing(request, id, title):

    if request.user.is_authenticated:
        listing = Listing.objects.get(id=id)
        comments = Comment.objects.filter(listing__id=id)
        bid = Bid.objects.filter(listing__id=id)
        watchlist_exist = Watchlist.objects.filter(user=request.user, listing__id=id).exists
        highest_bid = bid.filter(listing__id=id).values('amount').order_by('-amount').first()

        context = {
            "listing": listing,
            "bid": bid,
            "comment" : Comment.objects.filter(listing=listing)
        }

        if highest_bid:
            context["highest_bid"] = highest_bid
        if watchlist_exist:
            context["watchlist_exist"] = watchlist_exist
        return render(request, "auctions/listing.html", context)
    
    else:
        return render(request, "auctions/listing.html", {
            'listing': Listing.objects.get(id=id)
        })
    

def category_activeListing(request, category, id, title):
    listing = Listing.objects.get(id=id)
    comments = Comment.objects.filter(listing__id=id)
    bid = Bid.objects.filter(listing__id=id)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comment": comments,
        "bid": bid,
        "watchlist" : Watchlist.objects.all()
    })

def categories_listing(request, category):
    filtered_listing = Listing.objects.filter(is_active=True, category__name=category)
    return render(request, "auctions/category_listing.html",{
        "categories": Categorie.objects.all(),
        "listing": filtered_listing,
        "category": category
    })

def view_watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist":watchlist})

def Watchlist_remove(request, listing_id):
    user_id = request.user.id
    watchlist_exist = Watchlist.objects.filter(user__id=user_id, listing__id=listing_id).exists
    if request.method == "POST":
        if not watchlist_exist:
            messages.error(request, "Auction item not in watchlist, can't remove")
            return render(request, "auctions/watchlist.html", {
                "watchlist" : Listing.objects.all
            })
        else:
            watchlist = Watchlist.objects.get(user__id=user_id, listing__id=listing_id)
            watchlist.delete()
            messages.success(request, "Auction item has been removed from watchlist")
            return redirect('view_watchlist')
        
def remove_to_watchlist(request, listing_id):
    user_id = request.user.id
    listing = Listing.objects.get(id=listing_id)
    watchlist_exist = Watchlist.objects.filter(user__id=user_id, listing__id=listing_id).exists

    if request.method == "POST":
        #checks if watchlist have a value or if its a None
        if not watchlist_exist:
                return redirect('active_listing', id=listing_id, title=listing.title)
        else:
                watchlist = Watchlist.objects.filter(user__id=user_id, listing__id=listing_id)
                watchlist.delete()
                messages.success(request, "Auction item has been removed from watchlist")
                return redirect('active_listing', id=listing_id, title=listing.title)
            
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                user = request.user
                
                Watchlist.objects.create(user=user, listing=listing)
                context = {
                    "id" : listing,
                }
                #display message here:
                messages.success(request, "Added to your watchlist")
                return redirect('active_listing', id=listing_id, title=listing.title)
            except IntegrityError:
                return redirect('active_listing', id=listing_id, title=listing.title)
    else:
        messages.warning(request, "You must log in to add this in your watchlist!")
        return redirect('active_listing', id=listing_id, title=listing.title)

class CreateListingForm(forms.Form):
    title = forms.CharField(label="title", widget=forms.TextInput, required=True)
    starting_bid = forms.DecimalField(label="starting_bid", widget=forms.NumberInput, required=True)
    description = forms.CharField(label="description", widget=forms.Textarea ,required=True)
    image_url = forms.URLField(label="image_url",  widget=forms.URLInput, required=True)
    category = forms.ModelChoiceField(label="category", queryset=Categorie.objects.all(), required=True)

def create_listing(request):

    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            print("form is valid!")
            title = form.cleaned_data["title"]
            starting_bid = form.cleaned_data["starting_bid"]
            description = form.cleaned_data["description"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            owner = request.user
            is_active = True
            status = True

            listing = Listing.objects.create(title=title, 
                                   starting_bid=starting_bid, 
                                   description=description, 
                                   image_url=image_url,
                                   category=category,
                                   owner=owner,
                                   is_active=is_active)
            listing_id = listing.id
            
            messages.success(request, "Listing has been successfully created")
            return render(request, "auctions/listing.html", {
                "listing" : Listing.objects.get(id=listing_id),
                "listing_id" : listing_id,
                "watchlist" : Watchlist.objects.all(),
                "bid" : Bid.objects.filter(listing__id=listing.id)
            })
    return render(request, "auctions/create-listing.html", {
        "category": Categorie.objects.all(),
    })
def place_bid(request, listing_id):
    bidder = request.user
    listing = Listing.objects.get(id=listing_id)
    owner = listing.owner

    #check if the form is submitted in the POST
    if request.user.is_authenticated:
        if request.method == "POST":
            starting_bid = listing.starting_bid
            highest_bid = Bid.objects.filter(listing__id=listing_id).values('amount').order_by('-amount').first()
            
            #check is bid_amount has a value or null
            if not bidder == owner:
                bid_amount = Decimal(request.POST.get('bid'))

                if not bid_amount:
                    return redirect("active_listing", id=listing_id, title=listing.title)
                #else if it contains a value or not null
                else:
                    
                    if bid_amount > starting_bid:
                        print("Bid amount is equivalent or greater than Starting bid")
                        if highest_bid:
                            if bid_amount > highest_bid['amount']:
                                Bid.objects.create(bidder=bidder, listing=listing, amount=bid_amount)
                                messages.success(request, f" Your ${bid_amount} bid has been placed")
                                return redirect("active_listing", id=listing_id, title=listing.title)
                            else:
                                messages.warning(request, "Bid amount should be higher that current Price")
                                return redirect("active_listing", id=listing_id, title=listing.title)
                        else:
                            Bid.objects.create(bidder=bidder, listing=listing, amount=bid_amount)
                            messages.success(request, f" Your ${bid_amount} bid has been placed")
                            return redirect("active_listing", id=listing_id, title=listing.title)
                    
                    else:
                        messages.warning(request, "The amount must be greater than starting bid")
                        print("Warning: Bid should be equivalent or greater than Starting Bid and Current Price")
                        return redirect("active_listing", id=listing_id, title=listing.title)
    else:
        messages.warning(request, "You must log in to place a bid!")
        return redirect("active_listing", id=listing_id, title=listing.title)

def close_auction(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    bid = Bid.objects.filter(listing_id=listing_id)
    winner = Bid.objects.filter(id=listing_id).values('amount').order_by('-amount').first()
    
    if request.method == "POST":
        if user == listing.owner:
            listing.is_active = False
            listing.save()
            messages.success(request, "auction item has been closed")
            if bid:
                listing.winner = winner
                listing.save()
            return redirect('index')
        else:
            messages.warning(request, "You are not the listing owner, you don't have permission to close the auction!")
            return redirect('index')
    else:
        messages.error(request, "Button has not been triggered in the POST!")
        return redirect('index')

def comment(request, listing_id):
    user = request.user
    listing = Listing.objects.get(id=listing_id)
    
    if request.user.is_authenticated:
        if request.method == "POST":
            comment = request.POST.get('comment')
            print("Comment on POST")

            if not comment:
                print("Comment is empty")
                return render(request, "auctions/listing.html")
            
            else:
                Comment.objects.create(user=user, listing_id=listing_id, content=comment)
                messages.success(request,"Comment has been posted!")
                return redirect("active_listing", id=listing_id, title=listing.title)
        else:   
            messages.error(request, "Button has not been triggered in the POST!")
            return redirect("active_listing", id=listing_id, title=listing.title)
    else:
        messages.warning(request, "You must log in to add a comment!")
        return redirect("active_listing", id=listing_id, title=listing.title)