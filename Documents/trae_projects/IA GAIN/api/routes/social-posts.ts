import { Router } from 'express';
import { supabase } from '../server.js';

const router = Router();

// List all social posts
router.get('/', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('social_posts')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching social posts:', error);
      return res.status(500).json({ error: 'Failed to fetch social posts' });
    }

    // Transform data to match frontend interface
    const transformedPosts = data.map(post => ({
      id: post.id,
      platform: post.platform,
      content: post.content,
      image: post.image_url,
      scheduledDate: post.scheduled_date,
      status: post.status,
      likes: post.likes_count || 0,
      comments: post.comments_count || 0,
      shares: post.shares_count || 0,
      reach: post.reach_count || 0,
      publishedAt: post.published_at
    }));

    res.json(transformedPosts);
  } catch (error) {
    console.error('Error in social-posts route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new social post
router.post('/', async (req, res) => {
  try {
    const { platform, content, image, scheduledDate, status } = req.body;

    if (!platform || !content) {
      return res.status(400).json({ error: 'Platform and content are required' });
    }

    const postData = {
      platform,
      content,
      image_url: image || null,
      scheduled_date: scheduledDate || null,
      status: status || 'draft',
      likes_count: 0,
      comments_count: 0,
      shares_count: 0,
      reach_count: 0,
      published_at: status === 'published' ? new Date().toISOString() : null
    };

    const { data, error } = await supabase
      .from('social_posts')
      .insert([postData])
      .select()
      .single();

    if (error) {
      console.error('Error creating social post:', error);
      return res.status(500).json({ error: 'Failed to create social post' });
    }

    // Transform data to match frontend interface
    const transformedPost = {
      id: data.id,
      platform: data.platform,
      content: data.content,
      image: data.image_url,
      scheduledDate: data.scheduled_date,
      status: data.status,
      likes: data.likes_count || 0,
      comments: data.comments_count || 0,
      shares: data.shares_count || 0,
      reach: data.reach_count || 0,
      publishedAt: data.published_at
    };

    res.status(201).json(transformedPost);
  } catch (error) {
    console.error('Error in social-posts route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a social post
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { platform, content, image, scheduledDate, status } = req.body;

    const updateData = {
      platform,
      content,
      image_url: image || null,
      scheduled_date: scheduledDate || null,
      status,
      published_at: status === 'published' ? new Date().toISOString() : null
    };

    const { data, error } = await supabase
      .from('social_posts')
      .update(updateData)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating social post:', error);
      return res.status(500).json({ error: 'Failed to update social post' });
    }

    if (!data) {
      return res.status(404).json({ error: 'Social post not found' });
    }

    // Transform data to match frontend interface
    const transformedPost = {
      id: data.id,
      platform: data.platform,
      content: data.content,
      image: data.image_url,
      scheduledDate: data.scheduled_date,
      status: data.status,
      likes: data.likes_count || 0,
      comments: data.comments_count || 0,
      shares: data.shares_count || 0,
      reach: data.reach_count || 0,
      publishedAt: data.published_at
    };

    res.json(transformedPost);
  } catch (error) {
    console.error('Error in social-posts route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a social post
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { error } = await supabase
      .from('social_posts')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting social post:', error);
      return res.status(500).json({ error: 'Failed to delete social post' });
    }

    res.status(204).send();
  } catch (error) {
    console.error('Error in social-posts route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;