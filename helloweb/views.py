from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("""
    <h1>Hello, World!</h1>
    <p>Welcome to my first Django web application.</p>
    <p>This is a simple view that returns an HTML response.</p>
    <p>Enjoy exploring Django!</p>
    <p><a href="/datetime/">Current Date and Time (Function-Based View)</a></p>
    <p><a href="/datetime_class/">Current Date and Time (Class-Based View)</a></p>
    <p><a href="/random_qoute/">Random Quote</a></p>
    
    """)


def current_datetime(request):
    import datetime
    now = datetime.datetime.now()
    html = f"""
    <h1>Current Date and Time</h1>
    <p id="timer"></p>
    <script>
      function updateTimer() {{
        const now = new Date();
        document.getElementById('timer').textContent = now.toLocaleString();
      }}
      setInterval(updateTimer, 1000);
      updateTimer();
    </script>
    <p><a href="/">Back to Home</a></p>
    """
    return HttpResponse(html)


class CurrentDateTimeView:
    from django.views import View

    class CurrentDateTimeView(View):
        def get(self, request):
            import datetime
            now = datetime.datetime.now()
            html = f"""
            <h1>Current Date and Time (Class-Based View)</h1>
            <p id="timer"></p>
            <script>
              function updateTimer() {{
                const now = new Date();
                document.getElementById('timer').textContent = now.toLocaleString();
              }}
              setInterval(updateTimer, 1000);
              updateTimer();
            </script>
            <p><a href="/">Back to Home</a></p>
            """
            return HttpResponse(html)

    @classmethod
    def as_view(cls):
        return cls.CurrentDateTimeView.as_view()

def random_quote(request):
    import random
    quotes = [
        "The best way to predict the future is to invent it. - Alan Kay",
        "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
        "The only way to do great work is to love what you do. - Steve Jobs",
        "If you can dream it, you can achieve it. - Zig Ziglar",
        "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer"
    ]
    quote = random.choice(quotes)
    html = f"""
    <h1>Random Quote</h1>
    <blockquote>{quote}</blockquote>
    <p><a href="/">Back to Home</a></p>
    """
    return HttpResponse(html)
