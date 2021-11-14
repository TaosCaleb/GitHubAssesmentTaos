# How to create web service for protecting branches in an GitHub organization

## What is this repo?
This repo creates a local webserver to automatically:

- Protect the master branch
- Create a `README.md` file
- And create an alert for a target user via mention in an issue

When a new repository is created

## Prerequisites
- Git clone this repository to a local pc or server

- Install ngrok (if external url is not avaialable otherwhise)
  - https://ngrok.com/download


- Install docker-compose and docker on to server or pc
  - https://docs.docker.com/compose/install/

- Create api token and create `auth-vals.json` file in the same directory  as  `docker-compose.yml`
  - Create new api token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
    - Ensure the permissions for adding repos, modifying branches, and creating issues are checked for the api token
  - Contents of the `auth-vals.json` should look something like :
     ```json
     {
      "api_token"="ghp_XXXXXXXXXXXXXXXXXXXXX"
      "target_user"="<github_username>"
      }

    ```

- Create a github organization
  - https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/about-organizations

## Creating server and web hook

### On your pc

- Create `ngrok` endpoint
  - `ngrok http 4567`
  - Copy the resulting url and save for later
    - E.g. `https://XXX-XX-XXX-XX-XXX.ngrok.io (<< save this for later (https and not http for security)) -> http://localhost:4567`

- Navigate to the dir where the `docker-compose.yml` file is located

- Run the command `docker-compose up -d`
  - Now your webhook server is running

### On github.com

- Navigate to your organization

- Go to webhooks

- Click `Add a webhook`

- Copy and paste the ngrok url into the `Payload URL` field with the added `/payload` path
  - E.g. `https://XXX-XX-XXX-XX-XXX.ngrok.io/payload`

- Check the radial for `Let me select individual items`
  - Check the box for `Repositories`

- Create webhook

### Trouble-shooting
- If the newly created repo is not public your account will require a paid subscription to protect the branches

- The code is written to sequentially succeed so if one action fails (e.g. creating a readme file) the rest of the actions will fail (e.g protecting a branch). This is partially a code structure issue and partially how git works (can't protect a branch that doesn't exist)

- If the `auth-vals.json` file does not exist before starting docker compose will attempt to create a directory `auth-vals.json/` and you will see an error like this

```shell
Error response from daemon: mkdir <some_path>/0fec61c6a000e527c1fd9b37dc0d95720ed26edbac40f4807879d6e41b383499: mkdir <some_path>/0fec61c6a000e527c1fd9b37dc0d95720ed26edbac40f4807879d6e41b383499: not a directory
```
be sure that the directory `auth-vals.json` and the file `auth-vals.json` is created before starting docker-compose

- If you happen to see `404` errors in the logs, this may be a permissions issue caused by a few possible reasons
  1. The api token was not granted enough permissions
  1. There is an empty `auth-vals.json` file in the `python_code` directory, remove it and restart docker compose
    - This is a result of the the mounting process by docker, if you restart the docker-compose (`docker-compose down` then `docker-compose up`) the empty `auth-vals.json` file will be read instead of the proper `auth-vals.json` file in the parent directory 
  1. The `auth-vals.json` file is misconfigured, see example above for proper form
  1. There is a bad url that cannot be found 
