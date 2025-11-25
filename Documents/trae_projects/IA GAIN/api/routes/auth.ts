/**
 * This is a user authentication API route demo.
 * Handle user registration, login, token management, etc.
 */
import { Router, type Request, type Response } from 'express'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase with static config for production
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw';

const supabase = createClient(supabaseUrl, supabaseKey);

const router = Router()

/**
 * User Registration
 * POST /api/auth/register
 */
router.post('/register', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password, name } = req.body;
    
    if (!email || !password) {
      res.status(400).json({ 
        success: false, 
        error: 'Email and password are required' 
      });
      return;
    }

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name }
      }
    });

    if (error) {
      res.status(400).json({ 
        success: false, 
        error: error.message 
      });
      return;
    }

    res.json({ 
      success: true, 
      message: 'User registered successfully',
      user: data.user
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Registration failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
})

/**
 * User Login
 * POST /api/auth/login
 */
router.post('/login', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password } = req.body;
    
    if (!email || !password) {
      res.status(400).json({ 
        success: false, 
        error: 'Email and password are required' 
      });
      return;
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      res.status(401).json({ 
        success: false, 
        error: error.message 
      });
      return;
    }

    res.json({ 
      success: true, 
      message: 'Login successful',
      user: data.user,
      session: data.session
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Login failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
})

/**
 * User Logout
 * POST /api/auth/logout
 */
router.post('/logout', async (req: Request, res: Response): Promise<void> => {
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      res.status(400).json({ 
        success: false, 
        error: error.message 
      });
      return;
    }

    res.json({ 
      success: true, 
      message: 'Logout successful'
    });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Logout failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
})

/**
 * Get Current User
 * GET /api/auth/me
 */
router.get('/me', async (req: Request, res: Response): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader) {
      res.status(401).json({ 
        success: false, 
        error: 'No authorization header' 
      });
      return;
    }

    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);

    if (error) {
      res.status(401).json({ 
        success: false, 
        error: error.message 
      });
      return;
    }

    res.json({ 
      success: true, 
      user 
    });
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to get user',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
})

export default router
