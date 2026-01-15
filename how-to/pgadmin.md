---
title: pgAdmin Database Management
nav_order: 8
parent: How to...
domain: public
permalink: /how-to-pgadmin
last_reviewed_on: 2026-01-09
review_in: 6 months
---
# pgAdmin Database Management

## Introduction

pgAdmin is a web-based administration tool for PostgreSQL databases. IDP provides pgAdmin so you can inspect and manage your Aurora PostgreSQL databases directly from the browser.

## Access

pgAdmin is available at the following URL (replace `<cluster>` with your cluster name):

```
https://pgadmin.<cluster>.idp.jppol.dk
```

Examples:

- `https://pgadmin.idp-test.idp.jppol.dk`
- `https://pgadmin.koa-dev.idp.jppol.dk`

## Login

pgAdmin uses JP/Pol Entra (Azure AD) for authentication. Click the **"Login with JPPol"** button and sign in with your JP/Pol account.

Your user is created automatically on first login.

## Add Database Server

After login, you need to add a server connection to connect to your database.

### 1. Get Credentials

Follow the [PostgreSQL guide](/how-to-postgresql#connect-via-local-database-viewer) to retrieve your database endpoint and credentials.

### 2. Create Server in pgAdmin

1. Right-click **Servers** in the left panel
2. Select **Register → Server**
3. Fill in the **General** tab:
   - **Name**: Any name you prefer (e.g., `idp-dev-my-db`)
4. Fill in the **Connection** tab:
   - **Host name/address**: Endpoint from secret
   - **Port**: `5432`
   - **Maintenance database**: `<namespace>-<database>` (e.g., `idp-dev-my-db`)
   - **Username**: Username from secret
   - **Password**: Password from secret
   - **Save password**: Check this to save the password (see below)
5. Click **Save**

### Saving Passwords

If you check **Save password**, pgAdmin will prompt you to create a **Master Password** the first time. This master password encrypts all saved database passwords locally.

**First time saving a password:**
1. Check "Save password" when adding a server
2. You'll be prompted to create a master password
3. Enter and confirm your new master password
4. The database password is now saved

**If you see "Enter your master password"** but haven't set one before, click **Reset Master Password**. This happens if you're an existing user from before this feature was enabled. Note: resetting will clear any previously saved passwords (though you likely don't have any).

## Features

With pgAdmin you can:

- **Browse data**: View and edit table contents
- **Run SQL queries**: Use Query Tool to execute SQL
- **View schema**: Inspect tables, views, functions etc.
- **Manage users**: Handle database roles and permissions
- **Export data**: Export query results to CSV

## Tips

### Query Tool

Right-click on a database and select **Query Tool** to open a SQL editor.

### Saved Connections

pgAdmin saves your server connections, so you don't need to enter credentials every time.

### Multiple Databases

You can add multiple server connections to different databases in the same pgAdmin session.

## Troubleshooting

### Cannot Connect to Database

- Verify that endpoint, username and password are correct
- Check that your database exists and is accessible

### Login Fails

- Make sure to use your JP/Pol Entra account
- Contact the IDP team if you experience persistent login issues
