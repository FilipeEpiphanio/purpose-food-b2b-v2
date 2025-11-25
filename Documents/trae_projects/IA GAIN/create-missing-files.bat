@echo off
echo 🔧 Criando arquivos ausentes no projeto B2B limpo...
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN"

REM Criar diretório lib
mkdir src\lib

REM Criar utils.ts
echo import { type ClassValue, clsx } from "clsx" > src\lib\utils.ts
echo import { twMerge } from "tailwind-merge" >> src\lib\utils.ts
echo. >> src\lib\utils.ts
echo export function cn(^...inputs: ClassValue[]) { >> src\lib\utils.ts
echo   return twMerge(clsx(inputs)) >> src\lib\utils.ts
echo } >> src\lib\utils.ts

REM Criar supabase.ts
echo import { createClient } from '@supabase/supabase-js' > src\lib\supabase.ts
echo. >> src\lib\supabase.ts
echo const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co' >> src\lib\supabase.ts
echo const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA3OTY5NTMsImV4cCI6MjA0NjM3Mjk1M30.zR8i7qRD3zCXgrC6h8c4pITK4oF3wLgtIaE8jX4TaVk' >> src\lib\supabase.ts
echo. >> src\lib\supabase.ts
echo export const supabase = createClient(supabaseUrl, supabaseKey) >> src\lib\supabase.ts

REM Criar notificationTypes.ts
mkdir src\services
echo import { useState, useEffect } from 'react'; > src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo export interface Notification { >> src\services\notificationTypes.ts
echo   id: string; >> src\services\notificationTypes.ts
echo   title: string; >> src\services\notificationTypes.ts
echo   message: string; >> src\services\notificationTypes.ts
echo   type: 'info' ^| 'success' ^| 'warning' ^| 'error'; >> src\services\notificationTypes.ts
echo   read: boolean; >> src\services\notificationTypes.ts
echo   created_at: string; >> src\services\notificationTypes.ts
echo } >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo export function useNotifications() { >> src\services\notificationTypes.ts
echo   const [notifications, setNotifications] = useState^<Notification[]^>([]); >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   useEffect(() =^> { >> src\services\notificationTypes.ts
echo     // Mock notifications for now >> src\services\notificationTypes.ts
echo     setNotifications([ >> src\services\notificationTypes.ts
echo       { >> src\services\notificationTypes.ts
echo         id: '1', >> src\services\notificationTypes.ts
echo         title: 'Bem-vindo', >> src\services\notificationTypes.ts
echo         message: 'Sistema Purpose Food B2B', >> src\services\notificationTypes.ts
echo         type: 'info', >> src\services\notificationTypes.ts
echo         read: false, >> src\services\notificationTypes.ts
echo         created_at: new Date().toISOString() >> src\services\notificationTypes.ts
echo       } >> src\services\notificationTypes.ts
echo     ]); >> src\services\notificationTypes.ts
echo   }, []); >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   return { notifications, setNotifications }; >> src\services\notificationTypes.ts
echo } >> src\services\notificationTypes.ts

REM Criar realTimeSync.ts
echo export const realTimeSyncService = { >> src\services\realTimeSync.ts
echo   subscribe: (callback: Function) =^> { >> src\services\realTimeSync.ts
echo     // Mock implementation >> src\services\realTimeSync.ts
echo     return () =^> {}; >> src\services\realTimeSync.ts
echo   }, >> src\services\realTimeSync.ts
echo   emit: (event: string, data: any) =^> { >> src\services\realTimeSync.ts
echo     // Mock implementation >> src\services\realTimeSync.ts
echo   } >> src\services\realTimeSync.ts
echo }; >> src\services\realTimeSync.ts

REM Criar notificationService.ts
echo export const notificationService = { >> src\services\notificationService.ts
echo   notify: (message: string, type: string = 'info') =^> { >> src\services\notificationService.ts
echo     console.log(`[${type}] ${message}`); >> src\services\notificationService.ts
echo   }, >> src\services\notificationService.ts
echo   requestPermission: async () =^> { >> src\services\notificationService.ts
echo     return 'granted'; >> src\services\notificationService.ts
echo   } >> src\services\notificationService.ts
echo }; >> src\services\notificationService.ts

REM Criar customerStore.ts na raiz correta
mkdir src\store
echo import { create } from 'zustand' > src\store\customerStore.ts
echo import { persist } from 'zustand/middleware' >> src\store\customerStore.ts
echo. >> src\store\customerStore.ts
echo interface CustomerStore { >> src\store\customerStore.ts
echo   cart: any[]; >> src\store\customerStore.ts
echo   addToCart: (product: any) =^> void; >> src\store\customerStore.ts
echo   removeFromCart: (productId: string) =^> void; >> src\store\customerStore.ts
echo   clearCart: () =^> void; >> src\store\customerStore.ts
echo } >> src\store\customerStore.ts
echo. >> src\store\customerStore.ts
echo export const useCustomerStore = create( >> src\store\customerStore.ts
echo   persist^<CustomerStore^>( >> src\store\customerStore.ts
echo     (set) =^> ({ >> src\store\customerStore.ts
echo       cart: [], >> src\store\customerStore.ts
echo       addToCart: (product) =^> set((state) =^> ({ >> src\store\customerStore.ts
echo         cart: [...state.cart, product] >> src\store\customerStore.ts
echo       })), >> src\store\customerStore.ts
echo       removeFromCart: (productId) =^> set((state) =^> ({ >> src\store\customerStore.ts
echo         cart: state.cart.filter((item) =^> item.id !== productId) >> src\store\customerStore.ts
echo       })), >> src\store\customerStore.ts
echo       clearCart: () =^> set({ cart: [] }), >> src\store\customerStore.ts
echo     }), >> src\store\customerStore.ts
echo     { >> src\store\customerStore.ts
echo       name: 'customer-store', >> src\store\customerStore.ts
echo     } >> src\store\customerStore.ts
echo   ) >> src\store\customerStore.ts
echo ); >> src\store\customerStore.ts

REM Criar ShoppingCart.tsx
echo import React from 'react'; > src\pages\customer\ShoppingCart.tsx
echo import { useCustomerStore } from '../../store/customerStore'; >> src\pages\customer\ShoppingCart.tsx
echo. >> src\pages\customer\ShoppingCart.tsx
echo export default function ShoppingCart() { >> src\pages\customer\ShoppingCart.tsx
echo   const { cart } = useCustomerStore(); >> src\pages\customer\ShoppingCart.tsx
echo. >> src\pages\customer\ShoppingCart.tsx
echo   return ( >> src\pages\customer\ShoppingCart.tsx
echo     ^<div className="p-6"^> >> src\pages\customer\ShoppingCart.tsx
echo       ^<h1 className="text-2xl font-bold mb-4"^>Carrinho de Compras^</h1^> >> src\pages\customer\ShoppingCart.tsx
echo       ^<div className="bg-white rounded-lg shadow p-4"^> >> src\pages\customer\ShoppingCart.tsx
echo         {cart.length === 0 ? ( >> src\pages\customer\ShoppingCart.tsx
echo           ^<p className="text-gray-500"^>Seu carrinho está vazio^</p^> >> src\pages\customer\ShoppingCart.tsx
echo         ) : ( >> src\pages\customer\ShoppingCart.tsx
echo           ^<p className="text-green-600"^>Itens no carrinho: {cart.length}^</p^> >> src\pages\customer\ShoppingCart.tsx
echo         )} >> src\pages\customer\ShoppingCart.tsx
echo       ^</div^> >> src\pages\customer\ShoppingCart.tsx
echo     ^</div^> >> src\pages\customer\ShoppingCart.tsx
echo   ); >> src\pages\customer\ShoppingCart.tsx
echo } >> src\pages\customer\ShoppingCart.tsx

echo ✅ Arquivos ausentes criados!
echo 📁 Projeto B2B limpo está pronto!
echo 📊 Total de arquivos no projeto B2B limpo:
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN"
dir /s /b | find /c ".\"
pause","explanation":"Creating missing essential files for the clean B2B project"}