-- Grant service role access to customers table
GRANT ALL ON public.customers TO service_role;

-- Grant service role access to other tables
GRANT ALL ON public.products TO service_role;
GRANT ALL ON public.orders TO service_role;
GRANT ALL ON public.order_items TO service_role;
GRANT ALL ON public.transactions TO service_role;
GRANT ALL ON public.financial_records TO service_role;
GRANT ALL ON public.financial_goals TO service_role;
GRANT ALL ON public.invoices TO service_role;
GRANT ALL ON public.calendar_events TO service_role;
GRANT ALL ON public.social_posts TO service_role;
GRANT ALL ON public.whatsapp_messages TO service_role;
GRANT ALL ON public.google_calendar_tokens TO service_role;
GRANT ALL ON public.profiles TO service_role;