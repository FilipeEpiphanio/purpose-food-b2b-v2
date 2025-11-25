import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/pt-br';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { 
  ChevronLeft, 
  Plus, 
  RefreshCw, 
  Settings,
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Users,
  DollarSign
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { supabase } from '../lib/supabase';
import { toast } from 'sonner';

moment.locale('pt-br');
const localizer = momentLocalizer(moment);

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  type: 'feira' | 'evento' | 'compromisso' | 'entrega' | 'reuniao';
  description?: string;
  location?: string;
  google_event_id?: string;
  synced: boolean;
  color?: string;
}

const eventTypeColors = {
  feira: '#10B981', // green
  evento: '#3B82F6', // blue
  compromisso: '#F59E0B', // amber
  entrega: '#EF4444', // red
  reuniao: '#8B5CF6' // purple
};

const eventTypeLabels = {
  feira: 'Feira',
  evento: 'Evento',
  compromisso: 'Compromisso',
  entrega: 'Entrega',
  reuniao: 'Reunião'
};

export default function CalendarPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/calendar/events', {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      });

      if (!response.ok) {
        throw new Error('Erro ao carregar eventos');
      }

      const data = await response.json();
      const events = data.events || data; // Handle both formats
      const formattedEvents = events.map((event: any) => ({
        id: event.id,
        title: event.title,
        start: new Date(event.start_date),
        end: new Date(event.end_date),
        type: event.event_type || event.type,
        description: event.description,
        location: event.location,
        google_event_id: event.google_event_id,
        synced: event.sync_status === 'synced',
        color: eventTypeColors[(event.event_type || event.type) as keyof typeof eventTypeColors]
      }));

      setEvents(formattedEvents);
    } catch (error) {
      console.error('Erro ao carregar eventos:', error);
      toast.error('Erro ao carregar eventos');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncWithGoogle = async () => {
    try {
      setSyncing(true);
      
      // First, try to authenticate with Google
      const authResponse = await fetch('/api/calendar/auth', {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      });

      if (!authResponse.ok) {
        const authData = await authResponse.json();
        if (authData.authUrl) {
          // Redirect to Google OAuth
          window.location.href = authData.authUrl;
          return;
        }
      }

      // If already authenticated, sync events
      const syncResponse = await fetch('/api/calendar/sync/from-google', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      });

      if (!syncResponse.ok) {
        throw new Error('Erro ao sincronizar com Google Calendar');
      }

      await loadEvents(); // Reload events after sync
      toast.success('Eventos sincronizados com Google Calendar');
    } catch (error) {
      console.error('Erro na sincronização:', error);
      toast.error('Erro ao sincronizar com Google Calendar');
    } finally {
      setSyncing(false);
    }
  };

  const handleSelectEvent = (event: CalendarEvent) => {
    setSelectedEvent(event);
    setShowEventModal(true);
  };

  const handleNavigate = (date: Date) => {
    setCurrentDate(date);
  };

  const CustomEvent = ({ event }: { event: CalendarEvent }) => (
    <div className="text-xs p-1 rounded text-white" style={{ backgroundColor: event.color }}>
      <div className="font-semibold">{event.title}</div>
      <div className="text-xs opacity-90">
        {moment(event.start).format('HH:mm')} - {moment(event.end).format('HH:mm')}
      </div>
    </div>
  );

  const CustomToolbar = () => (
    <div className="flex items-center justify-between mb-4 p-4 bg-white rounded-lg shadow-sm">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => handleNavigate(moment(currentDate).subtract(1, 'month').toDate())}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <h2 className="text-xl font-bold text-gray-800">
          {moment(currentDate).format('MMMM YYYY')}
        </h2>
        <button
          onClick={() => handleNavigate(moment(currentDate).add(1, 'month').toDate())}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="h-5 w-5 rotate-180" />
        </button>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setCurrentDate(new Date())}
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Hoje
        </button>
        <button
          onClick={handleSyncWithGoogle}
          disabled={syncing}
          className="flex items-center space-x-2 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Sincronizando...' : 'Sincronizar'}</span>
        </button>
        <button
          onClick={() => navigate('/calendario/novo')}
          className="flex items-center space-x-2 px-4 py-2 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>Novo Evento</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <div className="flex items-center space-x-3">
                <CalendarIcon className="h-6 w-6 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">Calendário</h1>
              </div>
            </div>
            <button
              onClick={() => navigate('/settings')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Legend */}
        <div className="mb-6 p-4 bg-white rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Tipos de Eventos</h3>
          <div className="flex flex-wrap gap-4">
            {Object.entries(eventTypeLabels).map(([type, label]) => (
              <div key={type} className="flex items-center space-x-2">
                <div 
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: eventTypeColors[type as keyof typeof eventTypeColors] }}
                />
                <span className="text-sm text-gray-600">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Calendar */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <CustomToolbar />
          
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="p-4">
              <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                style={{ height: 600 }}
                onSelectEvent={handleSelectEvent}
                onNavigate={handleNavigate}
                date={currentDate}
                components={{
                  event: CustomEvent
                }}
                messages={{
                  previous: 'Anterior',
                  next: 'Próximo',
                  today: 'Hoje',
                  month: 'Mês',
                  week: 'Semana',
                  day: 'Dia',
                  agenda: 'Agenda',
                  date: 'Data',
                  time: 'Hora',
                  event: 'Evento',
                  noEventsInRange: 'Nenhum evento neste período',
                  showMore: (total) => `+ Ver mais (${total})`
                }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Event Modal */}
      {showEventModal && selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{selectedEvent.title}</h3>
              <button
                onClick={() => setShowEventModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div 
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: selectedEvent.color }}
                />
                <span className="text-sm font-medium">
                  {eventTypeLabels[selectedEvent.type as keyof typeof eventTypeLabels]}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  {moment(selectedEvent.start).format('DD/MM/YYYY HH:mm')} - 
                  {moment(selectedEvent.end).format('HH:mm')}
                </span>
              </div>
              
              {selectedEvent.location && (
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{selectedEvent.location}</span>
                </div>
              )}
              
              {selectedEvent.description && (
                <div className="text-sm text-gray-600">
                  {selectedEvent.description}
                </div>
              )}
              
              <div className="flex items-center space-x-2">
                <RefreshCw className={`h-4 w-4 ${selectedEvent.synced ? 'text-green-500' : 'text-gray-400'}`} />
                <span className="text-xs text-gray-500">
                  {selectedEvent.synced ? 'Sincronizado com Google' : 'Não sincronizado'}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowEventModal(false);
                  navigate(`/calendario/editar/${selectedEvent.id}`);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Editar
              </button>
              <button
                onClick={() => setShowEventModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}