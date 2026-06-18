from django.shortcuts import render


def home(request):
    """Отображает главную страницу каталога."""
    return render(request, 'catalog/home.html')


def contacts(request):
    """Отображает страницу контактов и обрабатывает данные формы обратной связи."""
    success_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        print('Получено сообщение обратной связи:')
        print(f'Имя: {name}')
        print(f'Телефон: {phone}')
        print(f'Сообщение: {message}')

        success_message = 'Сообщение успешно отправлено!'

    context = {'success_message': success_message}
    return render(request, 'catalog/contacts.html', context)
