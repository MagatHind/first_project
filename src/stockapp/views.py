from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockCreateForm, StockSearchForm, StockUpdateForm, CreateUserForm
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
# Create your views here.

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		form=CreateUserForm()
		if request.method=='POST':
			form=CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user=form.cleaned_data.get('username')
				messages.success(request,'Account was created for '+ user)
				return redirect('/login')
		context={"form":form}
		return render(request,"register.html",context)

def loginPage(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:

		if request.method=='POST':
			username=request.POST.get('username')
			password=request.POST.get('password')
			user=authenticate(request,username=username,password=password)
			if user is not None:
				login(request,user)
				return redirect('home')
			else:
				messages.info(request,'Username OR password is incorrect')
				
		context={}
		return render(request,"login.html",context)
	
def logoutUser(request):
	logout(request)
	return redirect('/login')

@login_required(login_url='login')
def home(request):
	title = 'Welcome: This is the Home Page'
	context = {
	"title": title,
	}
	return render(request, "home.html",context)
@login_required(login_url='login')   
def list_item(request):
	title = 'LIST OF ITEMS'
	form = StockSearchForm(request.POST or None)
	queryset= Stock.objects.all()
	context = {
		"title": title,
		"queryset": queryset,
		"form": form,
	}
	if request.method == 'POST':
		queryset = Stock.objects.filter(#category__icontains=form['category'].value(),
										item_name__icontains=form['item_name'].value()
										)
		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
			instance = queryset
			for stock in instance:
			 writer.writerow([stock.category, stock.item_name, stock.quantity])
			return response
		context = {
		"form": form,
		"title": title,
		"queryset": queryset,
		}
	return render(request, "list_items.html", context)

@login_required(login_url='login')
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Saved')
		return redirect('/list_items')
	context = {
		"form": form,
		"title": "Add Item",
	}
	return render(request, "add_items.html", context)

@login_required(login_url='login')
def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = StockUpdateForm(instance=queryset)
	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Successfully Updated')
			return redirect('/list_items')
			
	context = {
		'form':form
	}
	return render(request, 'add_items.html', context)

@login_required(login_url='login')
def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Successfully Deleted')
		return redirect('/list_items')
	return render(request, 'delete_items.html')