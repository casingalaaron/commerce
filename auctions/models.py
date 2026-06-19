from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Categorie(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image_url = models.URLField(max_length=128, null=True)
    description = models.TextField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=256)
    category = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_listing")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="won_listing")

    def __str__(self):
        return f"{self.title} by {self.owner}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} bid on {self.listing}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.TextField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} Commented on Listing: {self.listing}"
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="user_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'listing'],
                name='watchlist_duplicate_prevention',
            )
        ]
    def __str__(self):
            return f"{self.user} added {self.listing.title} on his Watchlist"
