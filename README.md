# README.md for Google Calendar Assistant

This project provides a personal executive assistant that helps users manage their Google Calendar. With functionalities like fetching, creating, and deleting events, it becomes easier to manage appointments and avoid double-booking.

## Pre-requisites

Before using the project, you must set up Google Calendar API access and grant the necessary permissions. Here are the steps:

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project.
3. Search for the 'Google Calendar API' in the library and enable it for your project.
4. Create credentials:
   1. Go to the `Credentials` tab.
   2. Click on `Create Credentials` and select `OAuth 2.0 Client IDs`.
   3. Choose `Desktop App` as the application type.
   4. Name your credentials and save.
5. Download the generated `credentials.json` file.
6. Place the `credentials.json` in the parent directory of this project.

## How to use

1. Make sure you have installed the necessary Python packages:
   ```
   pip install openai gcsa dateutil pytz
   ```
2. Run the `main.py` script (or whatever you've named the provided code).
3. Follow the on-screen prompts to interact with your Google Calendar.

## Features

1. Fetch events from Google Calendar.
2. Create events in Google Calendar.
3. Delete events from Google Calendar.
4. Interactive conversation with the assistant to manage the calendar.

## Important

- Make sure to grant the Google App access to your Google Calendar.
- Always keep your `credentials.json` confidential. Avoid uploading it to public repositories.
