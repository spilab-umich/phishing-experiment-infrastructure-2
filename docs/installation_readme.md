# Installation and Software Requirements

This repo uses `Python 3.10`. This document will walk through the steps to install and run this repo on your machine's `localhost`. These steps include:

- creating a Python virtual environment
- installing package dependencies
- assembling the Django project
- importing emails as .eml files
- initializing users
- starting the sever

For instructions on how to adjust or disable phishing warnings, please see the Customization document.

We do not include instructions for pushing this project to a remote server, which will depend on the server's operating system.

These instructions define specific package versions used to build this repo. You are free to install the latest versions  (e.g. Python, Django) but we cannot guarantee this project will work as expected in anything except the listed versions.

## Creating a Virtual Environment

The first step is to install Python onto your device (https://www.python.org/downloads/). 

The next step is to create a Python virtual environment in which to run this project. You can see Python's documention for venv here: https://docs.python.org/3/library/venv.html.

Once you have created your new virtual environment, `activate` it.
- In Windows OS, this is done through the command `. venv_name/Scripts/activate`
- In Linux-based OS, the command is `. venv_name/bin/activate`

## Software Requirements

Next install `Django 4.1.1` (https://docs.djangoproject.com/en/4.1/) and its dependencies within your virtual environment. You can install the most recent version of Django through your virtual environment's command line using the pip command `pip install django`. You can also install Django 4.1.1 with the command `pip install django==4.1.1`. Verify the installation with `pip show django`.

Note: Django notes that 4.1.1 is listed as "not secure" by Django's documentation. We recommend using the most recent version of Django for security reasons, however this may require additional debugging.

This repo also uses two packages that may be optional depending on your use case. 

We use `BeautifulSoup4 0.0.1` (https://beautiful-soup-4.readthedocs.io/en/latest/) in `config/init_db.py` to interact with and edit our HTML emails within Python. However you can revise this file to use your HTML parser of choice. 

We also use `django-cors-headers 3.13.0` (https://pypi.org/project/django-cors-headers/) to safely display phishing URLs while redirecting users so legitimate/safe URLs when they are clicked. However this package is not necessary if you do not intend to show participants phishing links.

## Assembling the Django Project

After installing the required packages, we will assemble the Django project. This will entail `Creating a New Django Project`, `Cloning the Repo`, `Overwriting the Initial Django Project Files` and `Initialize the Django Project`. 

### Creating a New Django Project
Create a new directory (e.g., `root_folder`) to contain this project. Navigate to the root directory and create a new Django project using the command `django-admin startproject email_client`. This will create a new Django project folder called `email_client` and, most importantly, will initialize your `settings.py` file. 

Next, we're going to create a `mail` app with the command `python email_client/manage.py startapp mail`.

Your Django Project should have the following hierarchy

- `<root folder>/`
    - `email_client/`
        - `email_client/`
        - `mail/`

For more details about how to create a Django project, you can follow the instructions here https://docs.djangoproject.com/en/4.1/intro/tutorial01/.

### Clone the Repo
Next we want to add the files from the repo to our Django project. You can accomplish this pulling the repo into a new directory and running the command `git clone https://github.com/spilab-umich/phishing-experiment-infrastructure-2`. 

### Overwrite the new Django project with the repo files
Now we want to overwrite some of the files in the Django project folder with the files in the repo. Copy the repo starting with the `email_client` folder inside the `root_folder` and paste it into the Django `root_folder`. **Make sure to copy and paste the contents of the repo's \<root_folder> into the Django project's \<root_folder> so the repo files overwrite the correct Django project files**.

### Adjusting `settings.py`
Now we need to make some changes to `email_client/settings.py`. First, we want to add the following line (a good place to add this line is underneath `ALLOWED_HOSTS`, since it follows the alphabetical pattern of the `settings.py` file:

`AUTH_USER_MODEL = 'mail.User'`

Next we need to add the following to the top of the `INSTALLED_APPS` settings:

- `'corsheaders',`
- `'mail.apps.MailConfig',`

### Initializing the Django Project's Database
Now we are going to initialize the Django project's database. We accomplish this with three commands:

- `python email_client/manage.py makemigrations mail`
- `python email_client/manage.py sqlmigrate mail 0001`
- `python email_client/manage.py migrate`

### Testing localhost
Finally, we want to make sure everything is working correctly. We can run the project on localhost with the command `python email_client/manage.py runserver`. If everything is correct, this should display the login screen but it should not be possible to login. This is because we do not have any users or emails initialized!

In the next step, we will import emails and initialize users.

## Importing Emails as .eml Files

Next we want to select some emails to display in the email client. Select some number of emails (in .eml format) and paste them into `config/raw_eml` directory. The script in `config/import_db.py` will parse these .eml files and translate them into objects in Django's database.

In addition to adding the .eml files, you will also want to create an email JSON object **for each email** in `config/emails.json`. This makes it easier to set particular object values in Django's data base. Each JSON email object should contain:

- `sender`: the name of the email sender
- `preview`: the text that you want to appear in the preview pane of the main inbox view
- `email_id`: the unique ID number of an email (integer)
- `num_links`: the number of links present in an email (we deleted some email links for our study)
- `link_id`: the unique link_id (integer) for which email link will display a warning (each email shows a warning over one link)
- `is_phish`: whether the email contains a phising link or not. 

## Running `init_db.py`
With the eml files in the `raw_eml` directory, we will want to configure the `init_db.py` file.

You can run this script by running `python -m config/init_db.py` in your virtual environment.

This file does the following:

- creates some number of users (which you can specify)
- saves EML files as HTML files in `config/raw_html`
- assigns unique ID numbers to email hyperlinks
- assigns a specific phishing URL to phishing emails (using the `link_id` value from `emails.json`)
- instantiates and saves User and Mail objects to Django's data base

This file can be adjusted to fit your needs, but here are some important things to note:

Each user is assigned a unique password through the `assign_credentials()` function in `email_client/mail/views.py`. This prevents developers from having direct access to participant passwords unless they use the `django-admin` view.

`init_db.py` also creates an adjustable number of "test users". These users have the pre-set username `tempuser<NUMBER>` and password `TestPassword`. We used these accounts to help check that the inbox was working as expected for specific groups/accounts.

The variable `list_of_p_domains` contains our chosen list of phishing URLs. For our study, we needed a 3 x 3 dictionary object. Adjust this variable to include your own phishing URLs if needed. 

### Copy the HTML emails to `email_client/mail/templates/mail/emails`
In addition to saving User and Mail objects to Django's database, `config_db.py` also transforms EML files into HTML files in the `config/raw_html` directory.

Depending on the source of EML files, you may want to edit these HTML files, including:
- Deleting personal or sensitive information such as names or email addresses
- Breaking or removing links that are tied to accounts, such as Unsubscribe links
- Remove tracking pixels to protect participant privacy and security
    
Once you have done this, copy the edited HTML files into the `email_client/mail/templates/mail/emails` directory.    

## Verify this Installation by Logging In

Once these steps are complete, it should be possible to login to the inbox using one of the `TempUser` credentials. 

To customize the display of anti-phishing warnings, please see the Customization document.


```python

```
