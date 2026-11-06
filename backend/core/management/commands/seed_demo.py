import random
from datetime import datetime,timedelta,time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from menu.models import Category,MenuItem
from tables.models import DiningTable,TableSession
from orders.models import Order,OrderItem,Payment

MENU={
 'Mains':[('Chicken pilau','Fragrant rice with Kenyan spices',420,260,25),('Beef pilau','Slow cooked beef and spiced rice',480,300,30),('Nyama choma','Charcoal grilled goat',850,550,40),('Fried chicken','Crispy chicken pieces',520,330,25),('Chips masala','Chips in tomato masala',300,130,18)],
 'Sides':[('Ugali','Fresh maize meal',100,30,8),('Sukuma wiki','Greens with onion and tomato',140,55,12),('Chapati','Soft layered flatbread',80,25,10),('Kachumbari','Tomato and onion salad',100,35,8),('Mukimo','Mashed potato, peas and maize',240,100,20)],
 'Breakfast':[('Mandazi','Freshly fried sweet dough',60,20,12),('Mahamri','Coconut cardamom bread',80,25,15),('Masala omelette','Eggs with onion and chilli',240,100,12),('Boiled eggs','Two farm eggs',120,55,8)],
 'Drinks':[('Kenyan chai','Tea with milk and spice',100,25,8),('Dawa','Honey lime ginger drink',220,80,8),('Passion juice','Fresh passion fruit juice',180,60,6),('Mango juice','Fresh seasonal mango',180,60,6)],
 'Specials':[('Slow roasted goat','House special, cooked low and slow',1100,650,60),('Beef stew','Tender beef in rich gravy',460,260,35)]}

class Command(BaseCommand):
    help='Create demo restaurant menu, staff, tables, and 60 days of sample sales.'
    def add_arguments(self,parser):parser.add_argument('--reset',action='store_true')
    def handle(self,*args,**options):
        random.seed(23)
        if options['reset']:
            Payment.objects.all().delete();OrderItem.objects.all().delete();Order.objects.all().delete();TableSession.objects.all().delete();DiningTable.objects.all().delete();MenuItem.objects.all().delete();Category.objects.all().delete()
        categories={}
        for index,(name,rows) in enumerate(MENU.items()):categories[name],_=Category.objects.get_or_create(name=name,defaults={'sort_order':index})
        products=[]
        for group,rows in MENU.items():
            for name,desc,price,cost,prep in rows:
                photo={'Nyama choma':'/static/images/image%202.png','Chicken pilau':'/static/images/image%203.png','Fried chicken':'/static/images/image%204.png'}.get(name,'')
                product,_=MenuItem.objects.update_or_create(name=name,defaults={'category':categories[group],'description':desc,'price':Decimal(price),'cost_price':Decimal(cost),'prep_minutes':prep,'image_url':photo})
                products.append(product)
        for number in range(1,9):DiningTable.objects.get_or_create(number=number)
        for username,role in [('owner','owner'),('kitchen','kitchen'),('waiter','waiter')]:
            user,_=User.objects.get_or_create(username=username);user.set_password('demo1234');user.save()
            from accounts.models import StaffProfile
            StaffProfile.objects.update_or_create(user=user,defaults={'role':role})
        if not Order.objects.exists():self._seed_sales(products)
        else:self._plant_bad_day()
        self.stdout.write(self.style.SUCCESS('Demo staff: owner, kitchen, waiter — password: demo1234'))
    def _seed_sales(self,products):
        popular=[p for p in products if p.name in ('Chicken pilau','Chapati','Kenyan chai','Ugali','Sukuma wiki','Passion juice')]
        quiet=[p for p in products if p.name in ('Mahamri','Boiled eggs','Mukimo')]
        for day in range(60,0,-1):
            date=timezone.localdate()-timedelta(days=day)
            count=random.randint(4,9)+(5 if date.weekday()>=5 else 0)
            if day==3:count=1
            for _ in range(count):
                hour=random.choices([10,12,13,14,18,19,20],[1,2,5,2,1,3,1])[0]
                local=timezone.make_aware(datetime.combine(date,time(hour,random.randint(0,59))), timezone.get_current_timezone())
                table=DiningTable.objects.get(number=random.randint(1,8));session=TableSession.objects.create(table=table,guests=random.randint(1,5),status='closed')
                session.opened_at=local-timedelta(minutes=45);session.closed_at=local+timedelta(minutes=45);session.save(update_fields=['opened_at','closed_at'])
                order=Order.objects.create(session=session,status='served',created_at=local)
                order.preparing_at=local+timedelta(minutes=2);order.ready_at=order.preparing_at+timedelta(minutes=random.randint(12,24));order.served_at=order.ready_at+timedelta(minutes=5);order.save(update_fields=['created_at','preparing_at','ready_at','served_at'])
                chosen=random.choices(popular,k=random.randint(1,2))+random.sample(products,k=random.randint(1,2))
                if quiet and random.random()<.07:chosen.append(random.choice(quiet))
                total=Decimal('0')
                for product in chosen:
                    qty=random.choices([1,2],[8,2])[0];OrderItem.objects.create(order=order,menu_item=product,quantity=qty,unit_price=product.price);total+=product.price*qty
                Payment.objects.create(session=session,method=random.choice(['cash','mpesa']),amount=total,created_at=local+timedelta(minutes=50))
    def _plant_bad_day(self):
        today=timezone.localdate()
        bad_day=today-timedelta(days=14)
        comparison=bad_day-timedelta(days=7)
        target=Payment.objects.filter(created_at__date=bad_day).order_by('-amount').first()
        reference=Payment.objects.filter(created_at__date=comparison).order_by('-amount').first()
        if target and reference:
            target.amount=max(Decimal('1.00'),reference.amount/10)
            target.save(update_fields=['amount'])
