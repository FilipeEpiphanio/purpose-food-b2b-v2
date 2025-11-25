@echo off
echo 🔧 Corrigindo arquivos do projeto B2B limpo...
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN"

REM Corrigir notificationTypes.ts
echo import { useState, useEffect } from 'react'; > src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo export interface Notification { >> src\services\notificationTypes.ts
echo   id: string; >> src\services\notificationTypes.ts
echo   title: string; >> src\services\notificationTypes.ts
echo   message: string; >> src\services\notificationTypes.ts
echo   type: 'info' ^| 'success' ^| 'warning' ^| 'error' ^| 'product_out_of_stock' ^| 'product_low_stock' ^| 'production_needed' ^| 'delivery_scheduled' ^| 'payment_confirmed' ^| 'product_updated' ^| 'order_status_changed'; >> src\services\notificationTypes.ts
echo   read: boolean; >> src\services\notificationTypes.ts
echo   is_read?: boolean; >> src\services\notificationTypes.ts
echo   created_at: string; >> src\services\notificationTypes.ts
echo } >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo export function useNotifications(userId?: string, customerId?: string) { >> src\services\notificationTypes.ts
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
echo         is_read: false, >> src\services\notificationTypes.ts
echo         created_at: new Date().toISOString() >> src\services\notificationTypes.ts
echo       } >> src\services\notificationTypes.ts
echo     ]); >> src\services\notificationTypes.ts
echo   }, []); >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   const unreadCount = notifications.filter(n =^> !n.read).length; >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   const markAsRead = (id: string) =^> { >> src\services\notificationTypes.ts
echo     setNotifications(prev =^> >> src\services\notificationTypes.ts
echo       prev.map(n =^> n.id === id ? { ...n, read: true, is_read: true } : n) >> src\services\notificationTypes.ts
echo     ); >> src\services\notificationTypes.ts
echo   }; >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   const markAllAsRead = () =^> { >> src\services\notificationTypes.ts
echo     setNotifications(prev =^> >> src\services\notificationTypes.ts
echo       prev.map(n =^> ({ ...n, read: true, is_read: true })) >> src\services\notificationTypes.ts
echo     ); >> src\services\notificationTypes.ts
echo   }; >> src\services\notificationTypes.ts
echo. >> src\services\notificationTypes.ts
echo   return { notifications, setNotifications, unreadCount, markAsRead, markAllAsRead }; >> src\services\notificationTypes.ts
echo } >> src\services\notificationTypes.ts

REM Corrigir customerStore.ts
echo import { create } from 'zustand' > src\store\customerStore.ts
echo import { persist } from 'zustand/middleware' >> src\store\customerStore.ts
echo. >> src\store\customerStore.ts
echo interface Customer { >> src\store\customerStore.ts
echo   id: string; >> src\store\customerStore.ts
echo   name: string; >> src\store\customerStore.ts
echo   email: string; >> src\store\customerStore.ts
echo } >> src\store\customerStore.ts
echo. >> src\store\customerStore.ts
echo interface CustomerStore { >> src\store\customerStore.ts
echo   customer: Customer ^| null; >> src\store\customerStore.ts
echo   cart: any[]; >> src\store\customerStore.ts
echo   cartItems: any[]; >> src\store\customerStore.ts
echo   addToCart: (product: any) =^> void; >> src\store\customerStore.ts
echo   removeFromCart: (productId: string) =^> void; >> src\store\customerStore.ts
echo   clearCart: () =^> void; >> src\store\customerStore.ts
echo   getCartTotal: () =^> number; >> src\store\customerStore.ts
echo   setCustomer: (customer: Customer ^| null) =^> void; >> src\store\customerStore.ts
echo } >> src\store\customerStore.ts
echo. >> src\store\customerStore.ts
echo export const useCustomerStore = create( >> src\store\customerStore.ts
echo   persist^<CustomerStore^>( >> src\store\customerStore.ts
echo     (set, get) =^> ({ >> src\store\customerStore.ts
echo       customer: null, >> src\store\customerStore.ts
echo       cart: [], >> src\store\customerStore.ts
echo       cartItems: [], >> src\store\customerStore.ts
echo       addToCart: (product) =^> set((state) =^> ({ >> src\store\customerStore.ts
echo         cart: [...state.cart, product], >> src\store\customerStore.ts
echo         cartItems: [...state.cartItems, product] >> src\store\customerStore.ts
echo       })), >> src\store\customerStore.ts
echo       removeFromCart: (productId) =^> set((state) =^> ({ >> src\store\customerStore.ts
echo         cart: state.cart.filter((item) =^> item.id !== productId), >> src\store\customerStore.ts
echo         cartItems: state.cartItems.filter((item) =^> item.id !== productId) >> src\store\customerStore.ts
echo       })), >> src\store\customerStore.ts
echo       clearCart: () =^> set({ cart: [], cartItems: [] }), >> src\store\customerStore.ts
echo       getCartTotal: () =^> { >> src\store\customerStore.ts
echo         const state = get(); >> src\store\customerStore.ts
echo         return state.cart.reduce((total, item) =^> total + (item.price || 0), 0); >> src\store\customerStore.ts
echo       }, >> src\store\customerStore.ts
echo       setCustomer: (customer) =^> set({ customer }), >> src\store\customerStore.ts
echo     }), >> src\store\customerStore.ts
echo     { >> src\store\customerStore.ts
echo       name: 'customer-store', >> src\store\customerStore.ts
echo     } >> src\store\customerStore.ts
echo   ) >> src\store\customerStore.ts
echo ); >> src\store\customerStore.ts

REM Corrigir realTimeSync.ts
echo export const realTimeSyncService = { > src\services\realTimeSync.ts
echo   subscribe: (callback: Function) =^> { >> src\services\realTimeSync.ts
echo     // Mock implementation >> src\services\realTimeSync.ts
echo     return () =^> {}; >> src\services\realTimeSync.ts
echo   }, >> src\services\realTimeSync.ts
echo   emit: (event: string, data: any) =^> { >> src\services\realTimeSync.ts
echo     // Mock implementation >> src\services\realTimeSync.ts
echo   }, >> src\services\realTimeSync.ts
echo   onProductChange: (callback: Function) =^> { >> src\services\realTimeSync.ts
echo     // Mock implementation >> src\services\realTimeSync.ts
echo     return () =^> {}; >> src\services\realTimeSync.ts
echo   } >> src\services\realTimeSync.ts
echo }; >> src\services\realTimeSync.ts

REM Corrigir notificationService.ts
echo export const notificationService = { > src\services\notificationService.ts
echo   notify: (message: string, type: string = 'info') =^> { >> src\services\notificationService.ts
echo     console.log(`[${type}] ${message}`); >> src\services\notificationService.ts
echo   }, >> src\services\notificationService.ts
echo   requestPermission: async () =^> { >> src\services\notificationService.ts
echo     return 'granted'; >> src\services\notificationService.ts
echo   }, >> src\services\notificationService.ts
echo   createAvailabilityNotification: (product: any) =^> { >> src\services\notificationService.ts
echo     console.log(`Notificação de disponibilidade: ${product?.name}`); >> src\services\notificationService.ts
echo   } >> src\services\notificationService.ts
echo }; >> src\services\notificationService.ts

echo ✅ Arquivos corrigidos!
echo 📊 Total de arquivos no projeto B2B limpo:
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN"
dir /s /b | find /c ".\"
pause