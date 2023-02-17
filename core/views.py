from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, ShipmentDetails, Payment, AddSlider
from .forms import CheckoutForm, ContactForm
from django.utils import timezone
from paystack.utils import get_js_script


import random
import string
import logging

logger = logging.getLogger(__name__)
#def my_view(request, arg1, arg):
 #   if bad_mojo:
        # Log an error message
 #       logger.error('Something went wrong!')


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(View):
    def get(self, *args, **kwargs):
        # form
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, "main/checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:order-summary")



    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print("User is entering shipment details")
                email = form.cleaned_data.get('email')
                phone_no = form.cleaned_data.get('phone_no')

                if is_valid_form([email, phone_no]):
                    #order.ref_code = create_ref_code() # Saves the ref code inside the database directly
                    shipment_details = ShipmentDetails(
                        user=self.request.user,
                        email=email,
                        phone_no=phone_no,
                    )
                    shipment_details.save()
                    order.shipment_details = shipment_details
                    order.save()


                    return redirect('core:payment')
                else:
                    messages.info(self.request, "Please fill in the required shipment details fields")
                    return redirect('core:checkout')
            else:
                messages.warning(self.request, "Failed checkout")
                return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error("self.request, You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = order.get_total() * 100
        email = order.user.email
        button_id = ''
        js_url = get_js_script()
        ref = create_ref_code()

        # Create the payment: Should be in the post method but have not yet figured that out
        payment = Payment()
        payment.user = self.request.user
        payment.amount = order.get_total()
        payment.save()
        # Assign the payment to the order: Should be in the post method but have not yet figured that out
        order.ordered = True
        order.payment = payment
        order.ref_code = ref
        order.save()

        context = {
            'order': order,
            'js_url': js_url,
            'button_class': 'btn btn_success',
            'button_id': button_id,
            'key': settings.PAYSTACK_PUBLIC_KEY,
            'email': email,
            'amount': amount,
            'ref': ref,
        }
        return render(self.request, "main/payment.html", context)



#def payment_button(request):
 #   order = Order.objects.get(user=request.user, ordered=False)
  #  amount = order.get_total() * 100
   # shipment = ShipmentDetails.objects.get(user=request.user)
    #email = shipment.email
    # new_ref = ref
    # new_redirect_url = redirect_url
    # button_class = 'btn btn_success'
    # if not new_ref:
    #    new_ref = get_random_string().upper()
    # if not new_redirect_url:
    #    new_redirect_url = "{}?amount={}".format(
    #        reverse('paystack:verify_payment', args=[new_ref]), new_amount)
   # return {
        # 'button_class': button_class,
        # 'button_id': button_id,
    #    'key': settings.PAYSTACK_PUBLIC_KEY,
        # 'ref': new_ref,
     #   'email': email,
      #  'amount': amount,
        # 'redirect_url': new_redirect_url,
       # 'js_url': get_js_script()
    #}

class AboutView(ListView):
    model = Item
    template_name = "main/about.html"


class ContactView(View):
    def get(self, *args, **kwargs):
        form = ContactForm()
        context = {
            'form': form,
        }
        return render(self.request, "main/contact.html", context)

    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']

            try:
                send_mail(subject, message, from_email, ['ibrahimsanusi360@yahoo.com'])
                messages.success(self.request, "Success! Thank you for your message.")
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('core:contact')
        else:
            messages.warning(self.request, "Failed to send message! Try again")
            return redirect('core:contact')



class HomeView(ListView):
    def get(self, *args, **kwargs):
        slider = AddSlider.objects.all()
        item = Item.objects.all()
        context = {
         'slider': slider,
         'item': item
        }
        return render(self.request, "main/home.html", context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }

            return render(self.request, 'main/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error("self.request, You do not have an active order")
            return redirect("/")



class ItemDetailView(DetailView):
    model = Item
    template_name = "main/product_detail.html"

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)






