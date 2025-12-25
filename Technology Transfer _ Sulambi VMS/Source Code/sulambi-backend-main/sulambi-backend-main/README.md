# Sulambi VOSA - Backend

This system is designed to streamline volunteer events by managing event proposals, approvals, and participation. Its key features include event proposal submission by Officers, approval by Admins, and participation by Members, each with specific roles and responsibilities."

This version clarifies the system's purpose and structure while making the flow smoother. Let me know if you'd like any further changes!

# Installation and Setup

Install the dependencies needed for the backend server:

```
pip install -r requirements.txt
```

To setup the server configuration, fill up the environment variables from `.env`. The file contains the following format:

```
DEBUG=True
DB_PATH="app/database/database.db"
AUTOMAILER_EMAIL=
AUTOMAILER_PASSW=
```

**Note:** Make sure to fill the `AUTOMAILER_EMAIL` and `AUTOMAILER_PASSW` variables for the automatic mailing to work.

### Initialization of Tables

By default, no database are present. To initialize a database, execute the following command:

```
python server.py --init
```

### Reseting tables

If you want a faster way to reset the entire database, you can execute the following commands:

```
python server.py --reset
python server.py --init
```

This will erase the old sequelize database and re-initialize the tables.

### Starting the backend server

To start the server, simply execute the following, and that's it!

```
python server.py
```
