import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://kctecmuwsnshbdzrxfxy.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtjdGVjbXV3c25zaGJkenJ4Znh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwODIxNTUsImV4cCI6MjA4NTY1ODE1NX0.DfKciVgkZs4JjCz6rpiCny0QVxf4tVeqBNfb54KPzag';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
