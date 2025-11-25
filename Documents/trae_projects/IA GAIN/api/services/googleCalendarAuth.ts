import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import dotenv from 'dotenv';

dotenv.config();

export class GoogleCalendarAuth {
  private oauth2Client: OAuth2Client;
  private scopes = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly'
  ];

  constructor() {
    // Initialize OAuth2 client with environment variables
    this.oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3001/api/calendar/auth/callback'
    );
  }

  /**
   * Generate Google OAuth2 authentication URL
   */
  generateAuthUrl(): string {
    const authUrl = this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: this.scopes,
      include_granted_scopes: true,
      prompt: 'consent'
    });

    return authUrl;
  }

  /**
   * Exchange authorization code for tokens
   */
  async exchangeCodeForTokens(code: string) {
    try {
      const { tokens } = await this.oauth2Client.getToken(code);
      
      // Set credentials on the OAuth2 client
      this.oauth2Client.setCredentials(tokens);
      
      return {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        expiry_date: tokens.expiry_date,
        scope: tokens.scope,
        token_type: tokens.token_type
      };
    } catch (error) {
      console.error('Error exchanging code for tokens:', error);
      throw new Error('Failed to exchange authorization code for tokens');
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(refreshToken: string) {
    try {
      this.oauth2Client.setCredentials({
        refresh_token: refreshToken
      });

      const { credentials } = await this.oauth2Client.refreshAccessToken();
      
      return {
        access_token: credentials.access_token,
        expiry_date: credentials.expiry_date,
        scope: credentials.scope,
        token_type: credentials.token_type
      };
    } catch (error) {
      console.error('Error refreshing access token:', error);
      throw new Error('Failed to refresh access token');
    }
  }

  /**
   * Get OAuth2 client with valid credentials
   */
  async getAuthenticatedClient(tokens: {
    access_token?: string;
    refresh_token?: string;
    expiry_date?: number;
  }) {
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3001/api/calendar/auth/callback'
    );

    // Check if access token is expired
    if (tokens.expiry_date && tokens.expiry_date < Date.now()) {
      // Refresh the token
      if (tokens.refresh_token) {
        const newTokens = await this.refreshAccessToken(tokens.refresh_token);
        oauth2Client.setCredentials({
          access_token: newTokens.access_token,
          refresh_token: tokens.refresh_token,
          expiry_date: newTokens.expiry_date
        });
      } else {
        throw new Error('Access token expired and no refresh token available');
      }
    } else {
      oauth2Client.setCredentials(tokens);
    }

    return oauth2Client;
  }

  /**
   * Revoke access token
   */
  async revokeToken(token: string) {
    try {
      await this.oauth2Client.revokeToken(token);
      return true;
    } catch (error) {
      console.error('Error revoking token:', error);
      throw new Error('Failed to revoke token');
    }
  }

  /**
   * Verify and decode JWT token
   */
  async verifyToken(token: string) {
    try {
      const ticket = await this.oauth2Client.verifyIdToken({
        idToken: token,
        audience: process.env.GOOGLE_CLIENT_ID
      });

      return ticket.getPayload();
    } catch (error) {
      console.error('Error verifying token:', error);
      throw new Error('Failed to verify token');
    }
  }
}

export default GoogleCalendarAuth;