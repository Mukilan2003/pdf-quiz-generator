# Setting Up Google OAuth for PDF Quiz Generator

This guide will walk you through the process of setting up Google OAuth for the PDF Quiz Generator application.

## Prerequisites

1. A Google account
2. Access to the [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click on "New Project"
4. Enter a name for your project (e.g., "PDF Quiz Generator")
5. Click "Create"

## Step 2: Enable the Google OAuth API

1. Select your project from the project dropdown
2. Go to "APIs & Services" > "Library"
3. Search for "Google OAuth2 API" or "Google Identity"
4. Click on "Google Identity Services" and enable it

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type (unless you have a Google Workspace organization)
3. Click "Create"
4. Fill in the required information:
   - App name: "PDF Quiz Generator"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Add the following scopes:
   - `email`
   - `profile`
   - `openid`
7. Click "Save and Continue"
8. Add test users if you're in testing mode
9. Click "Save and Continue"
10. Review your settings and click "Back to Dashboard"

## Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Name: "PDF Quiz Generator Web Client"
5. Add the following Authorized JavaScript origins:
   - `http://localhost:5000`
   - Your production URL (if applicable)
6. Add the following Authorized redirect URIs:
   - `http://localhost:5000/auth/google-callback`
   - Your production redirect URI (if applicable)
7. Click "Create"
8. Note down the Client ID and Client Secret

## Step 5: Update Your .env File

Add the following to your `.env` file:

```
# Google OAuth configuration
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

Replace `your-client-id-here` and `your-client-secret-here` with the values from step 4.

## Step 6: Configure Firebase (if using Firebase)

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select your existing project
3. Go to "Authentication" > "Sign-in method"
4. Enable "Google" as a sign-in provider
5. Use the same OAuth Client ID and Client Secret from step 4
6. Save the changes

## Step 7: Update Firebase Configuration in .env

Make sure your `.env` file has the following Firebase configuration:

```
# Firebase configuration
FIREBASE_API_KEY=your-firebase-api-key-here
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
FIREBASE_APP_ID=your-app-id
FIREBASE_MEASUREMENT_ID=your-measurement-id
```

You can find these values in your Firebase project settings.

## Step 8: Test the Authentication

1. Start your application
2. Navigate to the login page
3. Click on "Sign in with Google"
4. You should be redirected to Google's authentication page
5. After authenticating, you should be redirected back to your application

## Troubleshooting

### Error 401: invalid_client

This error occurs when:
- The client ID or client secret is incorrect
- The redirect URI doesn't match what's configured in the Google Cloud Console
- The OAuth consent screen is not properly configured

### Error: redirect_uri_mismatch

This error occurs when the redirect URI in your application doesn't match any of the authorized redirect URIs in the Google Cloud Console.

### Error: access_denied

This error occurs when the user denies permission to your application or when the OAuth consent screen is not properly configured.

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
