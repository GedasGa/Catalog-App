# Catalog Application

**by Gedas Gardauskas**

In this project, I have develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.

## What it is and it does

It is a RESTful web application using the Python framework Flask along with  third-party OAuth authentication. More over, project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.

## Required Libraries and Dependencies

- Python 2.x is required to run this project. The Python executable should be in your default path, which the Python installer should have set.
- SQLAlchemy 0.8.4 or higher (a Python SQL toolkit)
- Flask 0.10.1 or higher (a web development microframework)
- Vagrant
- VirtualBox that is compatible with Vagrant.

You can run the project in a Vagrant managed virtual machine (VM) which includes all the required dependencies (see below for how to run the VM). For this you will need Vagrant and VirtualBox software installed on your system.

## Getting started

### Setup Project:

- Install Vagrant and VirtualBox
Take a look [here](https://drupalize.me/videos/installing-vagrant-and-virtualbox?p=1526) to find more information.
- Download the project .zip file to you computer and unzip the file or clone this repository to your desktop.
- You can download or clone [this](https://github.com/udacity/fullstack-nanodegree-vm) repository with vagrant files.
- Now make sure you place `this repository` into vagrant folder.

### This project consists for the following files:
- `project.py` - The main Python script that serves the website
- `newsdata.sql` - database file with all records
- `client_secrets.json` - Client secrets for Google OAuth 2.0 login.
- `/static` - Directory containing CSS and Javascript for the website.
- `/templates` - Directory containing the HTML templates for the website, using the [Jinja 2](http://jinja.pocoo.org/docs/dev/) templating language for Python.
- `database_setup.py` - Defines the database classes and creates an empty database.
- `populate_database.py` - Inserts a selection of animals into the database.

#### Templates:

The `/templates` directory contains the following files, written in HTML and the [Jinja 2](http://jinja.pocoo.org/docs/dev/) templating language:

- `catalog.html` - The default page, which lists all the categories and the latest items that were added for logged in users.
- `catalogitem.html` - A page that displays all the category item for logged in users.
- `catalogitempublic.html` - A page that displays all the category item.
- `catalogpublic.html` - The default page, which lists all the categories and the latest items that were added.
- `deletecatalogitem.html` - A form to delete an item.
- `editcatalogitem.html` - A form to edit details of an item item.
- `header.html` - Navigation Bar template.
- `itemdetails.html` - A page that displays item detailed information for logged in users.
- `itemdetailspublic.html` - A page that displays item detailed information.
- `login.html` - A login page featuring OAuth Goolge+ login button.
- `main.html` - Main Page structure template.
- `newcatalogitem.html` - A form for creating a new item.

### Launching the Virtual Machine:

- Launch the Vagrant VM inside Vagrant sub-directory in the downloaded fullstack-nanodegree-vm repository using command:
  `$ vagrant up`
- Then Log into this using command:
  `$ vagrant ssh`
- Change directory to /vagrant and look around with ls.





How will I complete this project?
This project is connected to the Full Stack Foundations and Authentication and Authorization courses, but depending on your background knowledge you may not need the entirety of both courses to complete this project. Here's what you should do:

Install Vagrant and VirtualBox
Clone the fullstack-nanodegree-vm
Launch the Vagrant VM (vagrant up)
Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
Run your application within the VM (python /vagrant/catalog/application.py)
Access and test your application by visiting http://localhost:8000 locally
Get started with this helpful guide.
You can find the link to the fullstack-nanodegree-vm here.
