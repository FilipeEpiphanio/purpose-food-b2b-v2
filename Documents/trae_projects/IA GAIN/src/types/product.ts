export interface Product {
  id: string;
  name: string;
  category: string;
  price: number;
  cost: number;
  stock: number;
  min_stock: number;
  unit: string;
  status: 'active' | 'inactive';
  description: string;
  image_url?: string;
  ingredients?: string[];
  preparation_time?: number;
  is_active?: boolean;
  created_at: string;
  updated_at: string;
}