# URLShortener

    A URL shortener web application using Python with the Django framework.

### Setup

1. **Clone Repositroy**

    ```bash
    git clone https://github.com/sachinbudhamagar/URLShortener.git
    cd URLShortener
    ```

2. **Create a virtual environment**

    ```bash
    python -m venv venv
    venv\Scripts\activate       # window
    source venv\bin\activate    # mac
    ```
    
3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply database migrations**

    ```bash
    python manage.py makemigrations accounts
    python manage.py makemigrations shortener

    python manage.py migrate
    ```

5. **Run the development server**

    ```bash
    python manage.py runserver
    ```
    Open **http://127.0.0.1:8000** in your browser.

---
