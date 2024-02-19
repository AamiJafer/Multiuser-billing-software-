from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import auth
from django.utils.crypto import get_random_string
import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

def home(request):
  return render(request, 'home.html')

def login(request):
  return render(request, 'login.html')

def forgot_password(request):
  return render(request, 'forgot_password.html')

def cmp_register(request):
  return render(request, 'cmp_register.html')

def cmp_details(request,id):
  context = {'id':id}
  return render(request, 'cmp_details.html', context)

def emp_register(request):
  return render(request, 'emp_register.html')

def register_company(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    rfile = request.FILES.get('rfile')

    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already in Use !!')
        return redirect('cmp_register')
      
      elif Company.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('cmp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw, is_company = 1)
        cmp = Company( contact = phno, user = user_data, profile_pic = rfile)
        cmp.save()
        return redirect('cmp_details',user_data.id)

      else:
        messages.info(request, 'Sorry, Email already in Use !!')
        return redirect('cmp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'cmp_register.html')
  
def register_company_details(request,id):
  if request.method == 'POST':
    cname = request.POST['cname']
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    country = request.POST['country']
    pincode = request.POST['pincode']
    pannumber = request.POST['pannumber']
    gsttype = request.POST['gsttype']
    gstno = request.POST['gstno']

    if Company.objects.filter(pan_number = pannumber).exclude(pan_number='').exists():
      messages.info(request, 'Sorry, Pan number is already in Use !!')
      return redirect('cmp_details',id)
    
    if Company.objects.filter(gst_no = gstno).exclude(gst_no='').exists():
      messages.info(request, 'Sorry, GST number is already in Use !!')
      return redirect('cmp_details',id)

    code=get_random_string(length=6)

    usr = CustomUser.objects.get(id = id)
    cust = Company.objects.get(user = usr)
    cust.company_name = cname
    cust.address = address
    cust.city = city
    cust.state = state
    cust.company_code = code
    cust.country = country
    cust.pincode = pincode
    cust.pan_number = pannumber
    cust.gst_type = gsttype
    cust.gst_no = gstno
    cust.save()
    return redirect('login')

def register_employee(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    ccode = request.POST['ccode']
    rfile = request.FILES.get('rfile')

    if not Company.objects.filter(company_code = ccode).exists():
      messages.info(request, 'Sorry, Company Code is Invalid !!')
      return redirect('emp_register')
    
    cmp = Company.objects.get(company_code = ccode)
    emp_names = Employee.objects.filter(company = cmp).values_list('user',flat=True)
    for e in emp_names:
       usr = CustomUser.objects.get(id=e)
       if str(fname).lower() == (usr.first_name ).lower() and str(lname).lower() == (usr.last_name).lower():
        messages.info(request, 'Sorry, Employee With this name already exits, try adding an initial !!')
        return redirect('emp_register')
    
    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already exists !!')
        return redirect('emp_register')
      
      elif Employee.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('emp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw)
        emp = Employee(user = user_data, company = cmp, profile_pic = rfile, contact=phno)
        emp.save()
        return redirect('login')

      else:
        messages.info(request, 'Sorry, Email already exists !!')
        return redirect('emp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'emp_register.html')
  
def change_password(request):
  if request.method == 'POST':
    email= request.POST.get('email')
    if not CustomUser.objects.filter(email=email).exists():
      messages.success(request,'Sorry, No user found with this email !!')
      return redirect('forgot_password')
    
    else:
      otp = random.randint(100000, 999999)
      usr = CustomUser.objects.get(email=email)
      usr.set_password(str(otp))
      usr.save()

      subject = 'Password Reset Mail'
      message = f'Hi {usr.first_name} {usr.last_name}, Your Otp for password reset is {otp}'
      email_from = settings.EMAIL_HOST_USER
      recipient_list = [email ]
      send_mail(subject, message, email_from, recipient_list)
      messages.info(request,'Password reset mail sent !!')
      return redirect('forgot_password')

def user_login(request):
  if request.method == 'POST':
    email = request.POST['email']
    cpass = request.POST['pass']

    try:
      usr = CustomUser.objects.get(email=email)
      log_user = auth.authenticate(username = usr.username, password = cpass)
      if log_user is not None:
        if usr.is_company == 1:
          auth.login(request, log_user)
          return redirect('dashboard')
        else:
          emp = Employee.objects.get(user=usr)
          if emp.is_approved == 0:
            messages.info(request,'Employee is not Approved !!')
            return redirect('login')
          else:
            auth.login(request, log_user)
            return redirect('dashboard')
      messages.info(request,'Invalid Login Details !!')
      return redirect('login')
    
    except:
        messages.info(request,'Employee do not exist !!')
        return redirect('login')
    

def dashboard(request):
  context = {'usr':request.user}
  return render(request, 'dashboard.html', context)

def logout(request):
  auth.logout(request)
  return redirect('/')

def cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile.html',context)

def load_edit_cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile_edit.html',context)

def edit_cmp_profile(request):
  cmp =  Company.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = cmp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Sorry, Email Already in Use !!')
        return redirect('load_edit_cmp_profile')
      
    phno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('contact', flat=True)))
    gst_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('pan_number', flat=True)))
    gno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('gst_no', flat=True)))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['pan'] in gst_list:
      messages.info(request,'Sorry, PAN number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['gstnoval'] in gno_list:
      messages.info(request,'Sorry, GST number already in Use !!')
      return redirect('load_edit_cmp_profile')

    cmp.company_name = request.POST['cname']
    cmp.user.email = request.POST['email']
    cmp.user.first_name = request.POST['fname']
    cmp.user.last_name = request.POST['lname']
    cmp.contact = request.POST['phno']
    cmp.address = request.POST['address']
    cmp.city = request.POST['city']
    cmp.state = request.POST['state']
    cmp.country = request.POST['country']
    cmp.pincode = request.POST['pincode']
    cmp.pan_number = request.POST['pan']
    cmp.gst_type = request.POST['gsttype']
    cmp.gst_no = request.POST['gstnoval']
    old=cmp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      cmp.profile_pic=old
    else:
      cmp.profile_pic=new
    
    cmp.save() 
    cmp.user.save() 
    return redirect('cmp_profile') 
  
def emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile.html',context)

def load_edit_emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile_edit.html',context)

def edit_emp_profile(request):
  emp =  Employee.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = emp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Email Already in Use')
        return redirect('load_edit_emp_profile')
          
    phno_list = list(Employee.objects.exclude(user = request.user).values_list('contact', flat=True))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_emp_profile')

    emp.user.email = request.POST['email']
    emp.user.first_name = request.POST['fname']
    emp.user.last_name = request.POST['lname']
    emp.contact = request.POST['phno']
    old=emp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      emp.profile_pic=old
    else:
      emp.profile_pic=new
    
    emp.save() 
    emp.user.save() 
    return redirect('emp_profile') 

def load_staff_request(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 0)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_request.html',context)

def load_staff_list(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 1)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_list.html',context)

def accept_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.is_approved = 1
  emp.save()
  messages.info(request,'Employee Approved !!')
  return redirect('load_staff_request')

def reject_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.user.delete()
  emp.delete()
  messages.info(request,'Employee Deleted !!')
  return redirect('load_staff_request')

def creditNote(request):
  if request.user.is_company:
        cmp = request.user.company
  else:
        cmp = request.user.employee.company
  creditnotes=CreditNote.objects.filter(company=cmp)
  if not creditnotes:
    return render(request,'CreditNote.html',{'usr':request.user})
  else:
    return redirect('SalesReturn') 

def SalesReturn(request):
    print("Request user:", request.user)
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company
    print("Company:", cmp)
    parties = Party.objects.filter(company=cmp)
    items = Item.objects.filter(company=cmp)
    unit = Unit.objects.filter(company=cmp)
    max_reference_number = CreditNote.objects.filter(company=cmp).aggregate(Max('reference_no'))['reference_no__max']
    reference_number = max_reference_number + 1 if max_reference_number is not None else 1
    print("Reference number:", reference_number)
    context = {'usr':request.user, 'parties':parties, 'items':items,'unit':unit,'cmp':cmp,'reference_number': reference_number}
    return render(request,'SalesReturn.html',context)

def saveParty(request):
    if request.user.is_authenticated:
      if request.method == "POST":
          if request.user.is_company:
            cmp = request.user.company
          else:
            cmp = request.user.employee.company  
          print(cmp)
          usr = CustomUser.objects.get(username=request.user)
          party_name = request.POST['party_name']
          gst_no = request.POST['gst_no']
          mob = request.POST['party_num']
          gsttype = request.POST['gsttype']
          state = request.POST['supp_state']
          email = request.POST['email']
          addr = request.POST['party_addr']
          opbal = request.POST['creditamt']
          cr_limit = request.POST['crLimit']
          date = request.POST['credit_date']
          add1 = request.POST['addField1']
          add2 = request.POST['addField2']
          add3 = request.POST['addField3']
          
          user = request.user  
          party = Party(
              user=user,
              company=cmp,
              party_name=party_name,
              trn_no=gst_no,
              contact=mob,
              trn_type=gsttype,
              state=state,
              address=addr,
              email=email,
              openingbalance=opbal,
              creditlimit=cr_limit,
              current_date=date,
              additionalfield1=add1,
              additionalfield2=add2,
              additionalfield3=add3
          )
          party.save()
          print('Party created succefully ')
          return HttpResponse({"message": "success"})
      
def party_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  options={}
  option_objects=Party.objects.filter(company=cmp)
  for option in option_objects:
    options[option.id]=[option.id, option.party_name]
  return JsonResponse(options)

def get_partydetails(request):
  if request.method == 'POST':
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    party_id= request.POST.get('id').split(" ")[0]
    party=Party.objects.get(company=cmp,id=party_id)
    print(party.party_name)
    sales_invoice = SalesInvoice.objects.filter(party=party).first()

    balance=party.openingbalance
    phone=party.contact
    payment = party.payment
    if sales_invoice:
      invoiceno = sales_invoice.invoice_no
      print(invoiceno)
      invoicedate = sales_invoice.date
      placeofsupply = sales_invoice.address
    else:
      invoiceno = None
      invoicedate = None
      placeofsupply = None

    return JsonResponse({'balance':balance,'phone':phone,'invoiceno':invoiceno,'invoicedate':invoicedate,'placeofsupply':placeofsupply,'payment':payment})

@csrf_exempt
def create_unit(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  
    unit_name = request.POST.get('unit_name')
    new_unit = Unit.objects.create(company=cmp,unit_name=unit_name)
    response_data = {'unit_name': new_unit.unit_name, 'unit_id': new_unit.id}
    return JsonResponse(response_data)
  else:
    return JsonResponse({'error': 'Invalid method'}, status=400)


def saveItem(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  
    print(cmp)
    usr = CustomUser.objects.get(username=request.user)
    item_type=request.POST['item_type']
    item_name=request.POST['item_name']
    item_hsn=request.POST['item_hsn']
    item_unit=request.POST['item_unit']
    itm_taxable=request.POST['itm_taxable']
    itm_vat=request.POST['itm_vat']
    itm_sale_price=request.POST['itm_sale_price']
    itm_purchase_price=request.POST['itm_purchase_price']
    itm_stock_in_hand=request.POST['itm_stock_in_hand']
    itm_at_price=request.POST['itm_at_price']
    itm_date=request.POST['itm_date']
    item = Item(
              user=usr,
              company=cmp,
              itm_type=item_type,
              itm_name=item_name,
              itm_hsn=item_hsn,
              itm_unit=item_unit,
              itm_taxable=itm_taxable,
              itm_vat=itm_vat,
              itm_sale_price=itm_sale_price,
              itm_purchase_price=itm_purchase_price,
              itm_stock_in_hand=itm_stock_in_hand,
              itm_at_price=itm_at_price,
              itm_date=itm_date
          )
    item.save()
    print("Item saved")
    return HttpResponse({"message": "success"})
  
def item_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  options={}
  option_objects=Item.objects.filter(company=cmp)
  for option in option_objects:
    options[option.id]=[option.id, option.itm_name]
  return JsonResponse(options)
    
def get_itemdetails(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  item_id = request.POST.get('id').split(" ")[0]
  item=Item.objects.get(company=cmp,pk=item_id)
  hsn=item.itm_hsn
  price=item.itm_sale_price
  tax=item.itm_vat
  return JsonResponse({'hsn':hsn,'price':price,'tax':tax})

def fetch_item_details(request):
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
    item_id = request.POST.get('id')
    item = Item.objects.get(pk=item_id,company=cmp)
    data = {
                'hsn': item.itm_hsn,
                'price': item.itm_sale_price,
                'tax': item.itm_vat
            }
    return JsonResponse(data)

def get_item_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  options={}
  option_objects=Item.objects.filter(company=cmp)
  for option in option_objects:
    options[option.id]=[option.id, option.itm_name]
  return JsonResponse(options)

def saveCreditnote(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user)
    return_date=request.POST['returndate']
    reference_no=request.POST['refnum']
    subtotal=request.POST['subtotal']
    vat=request.POST['disvatper']
    adjustment=request.POST['adjustment']
    grandtotal=request.POST['grandTotal']
    party_status = request.POST.get('partystatus')
    print("Partystatus: ",party_status)
    creditnote = CreditNote.objects.create(user=usr, company=cmp,reference_no=reference_no,partystatus=party_status,returndate=return_date, subtotal=subtotal, vat=vat, adjustment=adjustment, grandtotal=grandtotal)
    if party_status=='partyon':
      party_details = request.POST.get('party_details')
      party_id = party_details.split()[0]
      party = Party.objects.get(pk=party_id)
      salesinvoice=SalesInvoice.objects.get(company=cmp,party=party)
      print(party.party_name)
      creditnote.party=party
      creditnote.salesinvoice=salesinvoice
      creditnote.save()

    # item_names = request.POST.getlist('item_name')
    # for item_name in item_names:
    #   print(item_name)
    # for item_data in item_names:

    #   item_data_parts = item_data.split()

    #     # Extract individual values
    #   itemid = item_data_parts[0]
    #   itmhsn = item_data_parts[1]
    #   itmsale_price = item_data_parts[2]
    #   itmvat = item_data_parts[3]

    #   print("Item ID:", itemid)
    #   print("Item HSN:", itmhsn)
    #   print("Item Sale Price:", itmsale_price)
    #   print("Item VAT:", itmvat)

    item_name = request.POST.getlist('item_name')
    quantity = request.POST.getlist('qty')
    price = request.POST.getlist('price')
    tax = request.POST.getlist('tax')
    discount = request.POST.getlist('discount')
    hsn = request.POST.getlist('hsn')
    total = request.POST.getlist('total')
    if len(item_name) == len(quantity) == len(price) == len(tax) == len(discount) == len(hsn) == len(total) and item_name and quantity and price and tax and discount and hsn and total:
      mapped=zip(item_name,quantity,price,tax,discount,hsn,total)
      mapped=list(mapped)
      for ele in mapped:
        item_name_parts = ele[0].split()
        
        item_id = item_name_parts[0]
        items = Item.objects.get(pk=item_id)
        it=Item.objects.get(user = request.user, id = item_id).itm_name
        print("item_name:", it)

        creditnoteitem=CreditNoteItem.objects.create(
                  user=usr,
                  credit_note=creditnote,
                  company=cmp,
                  items=items,
                  item=it,
                  hsn=ele[5],
                  quantity=ele[1],
                  tax=ele[3],
                  price=ele[2],
                  discount=ele[4],
                  total=ele[6])
      if 'save_new' in request.POST:
        return redirect('SalesReturn')
      else:
        return redirect('listout_page')
  else:  
    return redirect('SalesReturn')  
  
def listout_page(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company 
  creditnotes=CreditNote.objects.filter(company=cmp)
  context = {'usr':request.user,'creditnotes':creditnotes}
  return render(request,'listout.html',context)
  
def edit_creditnote(request,pk):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company
  parties = Party.objects.filter(company=cmp)
  items = Item.objects.filter(company=cmp)
  unit = Unit.objects.filter(company=cmp)
  creditnote_curr=CreditNote.objects.get(id=pk)
  creditnote_items=CreditNoteItem.objects.filter(credit_note=creditnote_curr)
  for item in creditnote_items:
    print(f"Item ID: {item.id}")
    print(f"Credit Note: {item.item}")
  context={'usr':request.user,
           'creditnoteitem_curr':creditnote_items,
           'credit_note':creditnote_curr,
           'parties':parties,
           'items':items,'unit':unit
          }
  return render(request,'edit_creditnote.html',context)

def delete_creditnote(request,pk):
  creditnote=CreditNote.objects.get(id=pk)
  creditnote.delete()
  return redirect('listout_page')

def updateCreditnote(request,pk):
  if request.method=="POST":
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user)
    creditnote=CreditNote.objects.get(id=pk)
    creditnote.user=request.user
    creditnote.company=cmp
    creditnote.returndate=request.POST['returndate']
    creditnote.reference_no=request.POST['refnum']
    creditnote.subtotal=request.POST['subtotal']
    creditnote.vat=request.POST['disvatper']
    creditnote.adjustment=request.POST['adjustment']
    creditnote.grandtotal=request.POST['grandTotal']
    creditnote.partystatus = request.POST.get('partystatus')
    creditnote.save()
    if creditnote.partystatus=='partyon':
      party_details = request.POST.get('party_details')
      party_id = party_details.split()[0]
      party = Party.objects.get(pk=party_id)
      salesinvoice=SalesInvoice.objects.get(company=cmp,party=party)
      print(party.party_name)
      creditnote.party=party
      creditnote.salesinvoice=salesinvoice
      creditnote.save()

    item_name = request.POST.getlist('item_name')
    quantity = request.POST.getlist('qty')
    price = request.POST.getlist('price')
    tax = request.POST.getlist('tax')
    discount = request.POST.getlist('discount')
    hsn = request.POST.getlist('hsn')
    total = request.POST.getlist('total')
    if len(item_name) == len(quantity) == len(price) == len(tax) == len(discount) == len(hsn) == len(total) and item_name and quantity and price and tax and discount and hsn and total:
      mapped=zip(item_name,quantity,price,tax,discount,hsn,total)
      mapped=list(mapped)
      credit_note_items = CreditNoteItem.objects.filter(credit_note=creditnote)

      item_ids=[]
      for ele in mapped:
        item_name_parts = ele[0].split()
        
        item_id = item_name_parts[0]
        item_ids.append(item_id)
        items = Item.objects.get(company=cmp,pk=item_id)
        it=Item.objects.get(user = request.user, id = item_id).itm_name
        print("item_name:", it)
        existing_credit_note_item = credit_note_items.filter(items=items).first()
        
        if existing_credit_note_item:
          existing_credit_note_item.quantity = ele[1]
          existing_credit_note_item.price = ele[2]
          existing_credit_note_item.tax = ele[3]
          existing_credit_note_item.discount = ele[4]
          existing_credit_note_item.hsn = ele[5]
          existing_credit_note_item.total = ele[6]
          existing_credit_note_item.save()
        else:
          CreditNoteItem.objects.create(
                user=usr,
                credit_note=creditnote,
                company=cmp,
                items=items,
                item=it,
                hsn=ele[5],
                quantity=ele[1],
                tax=ele[3],
                price=ele[2],
                discount=ele[4],
                total=ele[6]
            )
      existing_item_ids = [int(id.split('_')[-1]) for id in item_ids]
      items_to_delete = credit_note_items.exclude(items__id__in=existing_item_ids)
      items_to_delete.delete()
      return redirect('listout_page')











