from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import openai, os
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from .models import *
import stripe


def index(request):
    return render(request, "index.html", {})


def services(request):
    return render(request, "services.html", {})


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        kontentas = request.POST.get('content')
        Kontaktai.objects.create(user=name, elpastas=email, komentaras=kontentas)
        atsakymas = "Dekojame, su jumis susisieks mūsų komanda el.paštu"
        return render(request, "contacts.html", {"atsakymas": atsakymas})
    return render(request, "contacts.html", {})


def register(request):
    uname = request.POST.get('uname')
    nickname = User.objects.filter(username=uname).exists()
    if request.method == 'POST':
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')
        nickname = User.objects.filter(username=uname).exists()

        if password == password2:
            if User.objects.filter(username=uname).exists():
                messages.error(request, f"Slapyvardis '{uname}' užimtas!")
                return redirect("register")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, f"El.paštas '{email}' užimtas!")
                    return redirect("register")
                else:
                    new_user = User.objects.create_user(uname, email, password)
                    new_user.save()

                    return redirect('login')
        else:
            messages.error(request, "Slaptažodžiai nesutampa!")
            return redirect("register")
    return render(request, "register.html", {"nickname": nickname})


def loginas(request):
    if request.method == "POST":
        name = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Vartotojas neegzistuoja arba neteisingi duomenys!")
            return redirect('login')

    return render(request, "login.html", {})


def logoutuser(request):
    logout(request)
    return redirect('index')


load_dotenv()

api_key = os.getenv("OPENAI_KEY", None)


def paklausk(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                kontentas = "You are Lithuanian named 'Essay.lt žinių meistras," \
                            "you only speak Lithuania language, if user tries to " \
                            "communicate in other language you don't understand" \
                            "created by Dovydas Skauminas and Ernestas Undzėnas" \
                            "try to provide information as accurately" \
                            "as possible in Lithuania language, you only can answer short questions," \
                            "you can't write essays, peoms, sonnets, or any other literature"

                openai.api_key = api_key
                user_input = request.POST.get("user_input")

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.5
                )
                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "paklausk.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def rasiniai(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                openai.api_key = api_key
                user_input = request.POST.get("user_input")
                kontentas = "You are Lithuanian writer named 'Essay.lt rašytojas' created by Dovydas Skauminas and" \
                            " Ernestas Undzėnas, " \
                            "try to provide information as accurately as possible in Lithuania language," \
                            " you dont answer other questions that are not related " \
                            "to anything else, only Lithuanian writing " \
                            "essays/letters/poems etc.. if someone asks you if you can " \
                            "do math or physics or English writings" \
                            "any other subject not related to Lithuanian " \
                            "literature and writing, you reply with a straight no! No other subject " \
                            "not related to Lithunian language writings! " \
                            "You dont answer other language messages"

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.2
                )
                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "rasiniai.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def anglu(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                openai.api_key = api_key
                user_input = request.POST.get("user_input")
                kontentas = "You are English writer named 'Essay.lt Writer' " \
                            "created by Dovydas Skauminas and Ernestas Undzėnas " \
                            "try to provide information as accurately as possible in English language," \
                            " you dont answer other questions that are not related to anything else," \
                            " only English writings " \
                            "essays/letters/poems etc.. if someone asks you if you can do math or physics or " \
                            "any other subject not related to english literature and writing," \
                            " you reply with a straight no!"

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.3
                )
                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "anglu.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def motyvacinis(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                if request.POST.get("user_input") and request.POST.get("user_input2") and request.POST.get(
                        "user_input3"):
                    openai.api_key = api_key
                    user_input = "Parašyk darbo laišką darbdaviui, turiu " + request.POST.get(
                        "user_input") + " " + request.POST.get(
                        "user_input2") + " pretenduoju į " + request.POST.get("user_input3")
                    kontentas = "You are Essay.lt Lithuanian cover letter writer, " \
                                "created by Dovydas Skauminas and Ernestas Undzėnas" \
                                "you can only build cover letter for job application" \
                                "try to provide information as accurately as possible in Lithuania language," \
                                "you dont answer other questions that are" \
                                "not related to anything that is not cover letter" \
                                "if someone asks you if you can do math or physics, essays, sonnets or " \
                                "any other subject that is not cover letter, you reply with a straight no!"

                    response = openai.ChatCompletion.create(
                        model='gpt-3.5-turbo',
                        messages=[
                            {"role": "system",
                             "content": kontentas},
                            {"role": "user", "content": user_input}
                        ],

                        temperature=0.5
                    )
                    chatbot_response = response['choices'][0]['message']['content']
                else:
                    chatbot_response = "Prašau užpildyti visus langelius"

            return render(request, "motyvacinis.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def testas(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                openai.api_key = api_key
                answers = request.POST.get("user_inputA") + request.POST.get("user_inputB") + request.POST.get(
                    "user_inputC") + request.POST.get("user_inputD") + request.POST.get(
                    "user_inputE") + request.POST.get(
                    "user_inputF")
                user_input = f"The subject is {request.POST.get('dalykas')} the question is " \
                             f"{request.POST.get('user_input')}, posibble answers is {answers}"

                kontentas = "You are Lithuanian knowlage master, " \
                            "created by Dovydas Skauminas and Ernestas Undzėnas" \
                            "you can only answer a right answer by given possible answers" \
                            "try to provide information as accurately as possible in Lithuania language," \
                            "you dont answer other questions that are not related " \
                            "to anything that is not selected subject" \
                            "if someone asks you if you can write essays, sonnets or " \
                            "any other poetry, you reply with a straight no, and " \
                            "if you dont understand the questions say that you dont understand the question"

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.2
                )
                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "testas.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def perfrazuok(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                kontentas = "You are Lithuanian paraphraser named 'Essay.lt perfrazuotojas'," \
                            "created by Dovydas Skauminas and Ernestas Undzėnas" \
                            "you can only to paraphrase a user entered text," \
                            "paraphrase text only in Lithuania language," \
                            "you dont answer other questions that are not related to " \
                            "anything that is not to paraphrase text" \
                            "if someone asks you if you can do math or physics or " \
                            "any other subject that is not related to literature and writing," \
                            " you reply with a straight no!" \
                            "you only can paraphrase the given text"

                openai.api_key = api_key
                user_input = request.POST.get("user_input")

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.7
                )
                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "perfrazuok.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def cv(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            chatbot_response = None
            if request.method == "POST":
                kontentas = "You are Lithuanian cv writer named 'Essay.lt CV specialistas'," \
                            "created by Dovydas Skauminas and Ernestas Undzėnas" \
                            "you can only write cv by given information a user a user has entered," \
                            "write CV only in Lithuania language," \
                            "you dont answer other questions that are not related to anything that is not related to CV" \
                            "if someone asks you if you can do math or physics or " \
                            "any other subject that is not related to CV writing, you reply with a straight no!"

                openai.api_key = api_key
                user_input = request.POST.get("user_input")

                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system",
                         "content": kontentas},
                        {"role": "user", "content": user_input}
                    ],

                    temperature=0.7
                )

                chatbot_response = response['choices'][0]['message']['content']

            return render(request, "cv.html", {"response": chatbot_response})
        except UserMembership.DoesNotExist:
            return redirect('planai')
    else:
        return loginas(request)


def klaidos(request):
    if request.user.is_authenticated:
        chatbot_response = None
        if request.method == "POST":
            kontentas = "You are Lithuanian writer named 'Essay.lt Klaidų taisytojas'," \
                        "you can only correct given text a user a user has entered," \
                        "correct text only in Lithuania language," \
                        "you dont answer other questions that are not related to anything that is not related to " \
                        "grammar and punctuation" \
                        "if someone asks you if you can do math or physics or " \
                        "any other subject or question that " \
                        "is not related to correcting a text, you reply with a straight no!"

            openai.api_key = api_key
            user_input = request.POST.get("user_input")

            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system",
                     "content": kontentas},
                    {"role": "user", "content": user_input}
                ],

                temperature=0.7
            )

            chatbot_response = response['choices'][0]['message']['content']

        return render(request, "klaidos.html", {"response": chatbot_response})
    else:
        return loginas(request)


def paskyra(request):
    if request.user.is_authenticated:
        try:
            user_membership = UserMembership.objects.get(user=request.user)
            subscriptions = Subscription.objects.get(user_membership=user_membership)
            return render(request, "paskyra.html", {'sub': subscriptions})
        except UserMembership.DoesNotExist:
            subscriptions = "Neturite jokio plano"
            return render(request, "paskyra.html", {'sub': "Neturite jokio plano"})

    else:
        return loginas(request)


def subscription(request):
    return render(request, "planai_tikrasis.html", {})


YOUR_DOMAIN = "http://127.0.0.1:9000/"


class ProductLandingPageViewBasic(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        product = Membership.objects.get(membership_type="Basic")
        prices = Price.objects.filter(product=product)
        context = super(ProductLandingPageViewBasic,
                        self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "prices": prices
        })
        return context


class ProductLandingPageViewPremium(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        product = Membership.objects.get(membership_type="Premium")
        prices = Price.objects.filter(product=product)
        context = super(ProductLandingPageViewPremium,
                        self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "prices": prices
        })
        return context


class ProductLandingPageViewUltra(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        product = Membership.objects.get(membership_type="Ultra")
        prices = Price.objects.filter(product=product)
        context = super(ProductLandingPageViewUltra,
                        self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "prices": prices
        })
        return context


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            price = Price.objects.get(id=self.kwargs["pk"])
            domain = "http://127.0.0.1:9000"
            if settings.DEBUG:
                domain = "http://127.0.0.1:9000"
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price.stripe_price_id,
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id": price.id
                },
                mode='subscription',
                success_url=domain + '/success/',
                cancel_url=domain + '/cancel/',
            )
            return redirect(checkout_session.url)
        else:
            return redirect('login')


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]

        send_mail(
            subject="Essay.lt",
            message=f"Sveikiname įsigijus Essay.lt prenumeratą",
            recipient_list=[customer_email],
            from_email="your@email.com"
        )
        product_id = event['data']['object']['metadata']['product_id']
        user = User.objects.get(email=customer_email)

        if product_id == "4":
            stripe_id = "prod_Nh9mwHtUcJsbvq"
            membership = Membership.objects.get(stripe_product_id=stripe_id)
            UserMembership.objects.create(user=user, membership=membership)

        if product_id == "2":
            stripe_id = "prod_Nh1IV67AvAo8cm"
            membership = Membership.objects.get(stripe_product_id=stripe_id)
            UserMembership.objects.create(user=user, membership=membership)

        if product_id == "1":
            stripe_id = "prod_NgpRWY2fwCPAvo"
            membership = Membership.objects.get(stripe_product_id=stripe_id)
            UserMembership.objects.create(user=user, membership=membership)

    return HttpResponse(status=200)
