### How to create web service for protecting branches in an GitHub organization

## What is this repo?
This repo creates a local webserver to automatically:
- protect the master branch
- Create a `README.md` file
- And create an alert for a target user via mention in an issue

## Prerequisites
- Git clone this repository to a local pc or server
- Install ngrok
  - https://ngrok.com/download

- Install dockercompose and docker
  - https://docs.docker.com/compose/install/
- Create api key and create `auth-vals.json` file in the same directory  as  `docker-compose.yml`
  - Ensure the permissions for adding repos, modifying branches, and creating issues are checked
  - contents should look something like :
     ```json
     {
      "api_token"="ghp_XXXXXXXXXXXXXXXXXXXXX"
      "target_user"="<github_username>"
      }

    ```

- Create a github organization
  - https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/about-organizations
## Creating server and web hook

### On you pc

- Create `ngrok` endpoint
  - `ngrok http 4567`
  - Copy the resulting url and save for later
- Navigate to the dir where the `docker-compose.yml` file is located
- Run the command `docker-compose up -d`
  - Now your webhook server is running

### On github.com

- Navigate to your organization
- Go to webhooks
- Click `Add a webhook`
- Copy and paste the ngrok url into the `Payload URL` field with the added `/payload` path
  - E.g. `http://XXX-XX-XXX-XX-XXX.ngrok.io/payload`
- Check the radial for `Let me select individual items`
  - Check the box for repositories
- Create webhook

