# Project

## Setup

### Requirements

This projects requires python 3.6.
Python 3 can be installed with [pyenv](https://github.com/pyenv/pyenv).

1. Use [pyenv-installer](https://github.com/pyenv/pyenv-installer) for installing pyenv
1. See which python versions are available: `pyenv install --list`
1. Install python 3. Example: `pyenv install 3.6.3` (3.6.3 or higher)


Also [nodejs](https://nodejs.org/en/) is required for using `eslint` and `jscpd`.

1. Install `nodejs`, this could be archived by using [nvm](https://github.com/creationix/nvm).
1. Install `nodejs` version `7`
1. Use `npm` for installing dependencies: `npm install`


Optionally Docker and Docker Compose can be installed for development.

### Setting's

This project adopts [The 12 factor methodology](https://12factor.net/).
This means the configuration si made by environment variables [(Factor III)](https://12factor.net/config).

## Local setUp

1. Create a new virtualenv with a meaningful name: `pyenv virtualenv 3.6.3 my_virtualenv`
1. Create a `.python-version` file: `echo "my_virtualenv" > .python-version`
1. Install the requirements: `pip install -r requirements/local.txt`

### Development with Docker
1. Build image: `docker-compose build`
1. Start services: `docker-compose up`
1. Migrate database: `docker-compose run django /app/venv/bin/python manage.py migrate`
1. Create a super user: `docker-compose run django /app/venv/bin/python manage.py createsuperuser`

## Git hooks

* Install [git-hooks](https://github.com/git-hooks/git-hooks/).
* Install git hooks: `git hooks install`


## Tips:

## Run server

* `./manage.py runserver`

## Run shell

* `./manage.py shell`

## Run tests

* `python manage.py test`

## Run Lint/Style/CPD

Some linters require [nodejs](https://nodejs.org/en/).
Please install nodejs and then run `npm install`.


* [Flake8](http://flake8.pycqa.org/en/latest/index.html): `scripts/flake8.sh`
* [Pylint](https://pylint.readthedocs.io/en/latest/): `scripts/pylint.sh`
* [Jscpd](https://github.com/kucherenko/jscpd): `scripts/jscpd.sh`
* [Eslint](https://eslint.org/): `scripts/eslint.sh`

## Pycharm IDE

* Config virtualenv created before as the virtualenv of the project (settings -> python interpreter)
* enable django support: settings -> django 
  * django project root: /home/diego/dev/projects/python/project_name
  * settings: conf/settings/local.py
  * manage script: manage.py
* mark directory Templates as "Templates folder" (right-click over directory in the "Project view")


## Setup slack integration

You can set up a WebHook notification for your project.
You only need two things:

1. A channel for your project
1. Ensure yourself you haven't reached the WebHook limit of Slack.

### Slack settings

First, go to the [App Directory](). You will have multiple integrations supported by default.
If Gitlab is not present (It's not at this moment!), go to **Custom Integration** at the left panel.

Then click in the item "Incoming WebHooks" and then in the **Add configuration** button.

Select a channel where you like to receive notifications (Please do not spam us!).
After selecting the channel, configure the integration (Username, icon, etc) and copy the `Webhook URL` you will needed in the next step.

###  Gilab settings

In your project settings, there a section called "Integrations".
One of them is called "Slack notifications", click on it.

Check the **active** checkbox and configure the integration according to your needs.
Fill the input called `Webhook` with the previously copied `Webhook URL` from slack.

Save the form and test your integration with the button **Test settings and save changes**.

## [Sentry](https://sentry.io/welcome/) integration

> Open-source error tracking that helps developers monitor and fix crashes in real time. Iterate continuously. Boost efficiency. Improve user experience.

### Integration

Based in [official integration](https://docs.sentry.io/clients/python/integrations/django/) with Django.

The project's settings `conf/settings/production.py` already adds `'raven.contrib.django.raven_compat',` to the `INSTALLED_APPS`.
Also it adds these lines:

```python
RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', default=""),
}
```

So you only have to add the `RAVEN_DNS` to the environment of your application.

### Nginx & Sentry

If a request takes too much time Nginx might end it, but It still could be running in the Gunicorn worker process.
Then, the user will see an error, but Sentry is never notified.
A solution for this is configuring [sentrylogs](https://github.com/mdgart/sentrylogs) application.
It reads nginx logs and reports to Sentry on errors.

Install it with `pip`:

    pip install sentrylogs

Run it with `daemonize` option:

    sentrylogs --daemonize --sentrydsn $RAVEN_DNS

Options:

If your nginx logs are not being saved in the default place (`/var/log/nginx/error.log`), you can specify where they are with `--nginxerrorpath` option.
See [the documentation](https://github.com/mdgart/sentrylogs#how-it-works) for more information
