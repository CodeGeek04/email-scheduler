# Elysium Email Scheduler

Elysium Email Scheduler is an innovative solution designed to provide seamless integration between frontend email registration and backend email scheduling. The project is currently tailored for local development but can be adapted for deployment with minor changes. Currently, it focuses on 1:1 interactions between a single owner and client. 

## Description

The primary function of this software is to automate the email process. Once set up, the system allows automated reception and sending of emails. At its core, the scheduler ensures that emails are exchanged only with addresses containing "elysiuminnovations". 

## Setup and Running

Follow these steps to get started:

### Frontend and Backend Servers:

1. Navigate to the project directory.
2. Install the required node packages:
   ```bash
   npm install
3. Run frontend
   ```bash
   npm start

### Backend Python Scripts:
1. Install the required Python packages:
   ```bash
    pip install -r requirements.txt
2. Start the backend server:
   ```bash
    python app.py

### Email Routing:
1. Execute routes:
   ```bash
    python routes.py

2. Authenticate the assistant email as prompted.
3. Keep routes.py running. It will start receiving and sending emails based on the criteria.

### Deployment
When deploying, be sure to update the routing for the "register" button on the frontend, as it currently is set up for local hosting.

### Future Directions
Reply Functionality: The bot currently initiates a new message for every email. The goal is to enhance it to reply within threads.

Scalability: The vision is to adapt the bot for multiple owner-client interactions, rather than the current 1:1 configuration.
