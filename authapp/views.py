from django.shortcuts import redirect
from django.contrib		 			import auth
from django.contrib.auth.forms 		import AuthenticationForm
from django.contrib					import messages
from django.contrib.auth.models 	import Group


def login(request):

	if request.method == 'POST':
		form 				= AuthenticationForm(request, request.POST)

		username 		= form.data.get('username')
		password 		= form.data.get('password')

		user 			= auth.authenticate(username=username, password=password)

		users_in_group = Group.objects.get(name="taxiadmin").user_set.all()
		users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

		if user is not None:

			auth.login(request, user)

			if request.user in users_in_group or request.user in users_in_group_collector:
				
				return redirect('taxi_show_index')

			else:
				
				auth.logout(request)

				messages.info(request, 'У Вас не достаточно прав для доступа в данный раздел! Обратитесь к администратору!')

				return redirect('taxi_show_index')

		else:

			messages.info(request, 'Комбинации пароль-логин не существует! Обратитесь к администратору!')

			return redirect('taxi_show_index')
	
	return redirect('taxi_show_index')


def logout(request):

	auth.logout(request)

	return redirect('taxi_show_index')

