from django.contrib import admin
from .models import Item, Order, OrderItem, ShipmentDetails, Payment, AddSlider

def make_order_received(modeladmin, request, queryset):
    queryset.update(being_delivered=True, received=True)

make_order_received.short_description = 'Update orders to received'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'shipment_details',
                    'payment'
                    ]

    list_display_links = [
        'user',
        'shipment_details',
        'payment',
    ]

    list_filter = [
        'ordered',
        'being_delivered',
        'received',
    ]

    search_fields = [
        'user__username',
        #'ref_code',
    ]

    actions = [
        make_order_received
    ]


class ShipmentDetailsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email',
        'phone_no',
    ]


    search_fields = [
        'user',
        'email',
        'phone_no'
    ]


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShipmentDetails, ShipmentDetailsAdmin)
admin.site.register(Payment)
admin.site.register(AddSlider)

