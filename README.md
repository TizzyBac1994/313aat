# Team A - Automated Assessment Tool

## Installation

- Clone the repo to your computer and `cd` into the folder that is created
- Set up a virtual environment
  - Run `python -m venv venv`
  - **Activate the venv!!**
- Install pip/flask dependencies from requirements
  - Run `pip install -r requirements.txt`
- Copy `.env.example` to a file called `.env` in the root directory
- In `.env`, change `DATABASE_URI` to match your database

## Updating Requirements (after pulling down master)

- **Activate the venv!!**
- Run `pip install -r requirements.txt`

### Database Setup

- In your command line terminal, **make sure your venv is activated.**
- Run `flask shell`
- In the python REPL that has opened, run `from AAT import db`
- Then run `db.create_all()` to create the tables in your development database

#### If you need to reset your database (**WARNING, this will delete all data you have added to your database**)

- Run `flask shell`
- In the python REPL that has opened, run `from AAT import db`
- Then run `db.drop_all()` to clear your database of tables (and data).
- Then run `db.create_all()` to create the tables again, using the current model structure.

### Test Data!

We have test data seeds in this project!

- Run `flask seed run` to populate your database with a bunch of randomly generated dummy data
- You can edit the seeder files (located in ./seeds) to increase or decrease the number of records created
  - If you're using a remote database (e.g. on the university server) seeding may take some time. Feel free to reduce the number of records seeded!
- **WARNING: Running the seeder will delete all data you have manually added to the database!**

*For almost everything we do with this project, you probably want to just have your venv activated at all times*
