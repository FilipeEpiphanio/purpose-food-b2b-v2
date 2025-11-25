import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, MapPin, Plus, ChevronRight } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import moment from 'moment';

interface UpcomingEvent {
  id: string;
  title: string;
  type: 'feira' | 'evento' | 'compromisso' | 'entrega' | 'reuniao';
  start_date: string;
  location?: string;
  color?: string;
}

const eventTypeColors = {
  feira: 'bg-green-100 text-green-800',
  evento: 'bg-blue-100 text-blue-800',
  compromisso: 'bg-amber-100 text-amber-800',
  entrega: 'bg-red-100 text-red-800',
  reuniao: 'bg-purple-100 text-purple-800'
};

const eventTypeLabels = {
  feira: 'Feira',
  evento: 'Evento',
  compromisso: 'Compromisso',
  entrega: 'Entrega',
  reuniao: 'Reunião'
};

export default function UpcomingEventsWidget() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [events, setEvents] = useState<UpcomingEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUpcomingEvents();
  }, []);

  const loadUpcomingEvents = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/calendar/events/upcoming?limit=5', {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.details?.includes('Could not find the table')) {
          console.log('Tabela calendar_events ainda não criada, mostrando eventos vazios');
          setEvents([]);
          return;
        }
        throw new Error('Erro ao carregar eventos');
      }

      const data = await response.json();
      setEvents(data.events || data); // Handle both response formats
    } catch (error) {
      console.error('Erro ao carregar próximos eventos:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const formatEventDate = (dateString: string) => {
    const date = moment(dateString);
    const today = moment();
    const tomorrow = moment().add(1, 'day');
    
    if (date.isSame(today, 'day')) {
      return `Hoje às ${date.format('HH:mm')}`;
    } else if (date.isSame(tomorrow, 'day')) {
      return `Amanhã às ${date.format('HH:mm')}`;
    } else {
      return date.format('DD/MM [às] HH:mm');
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Próximos Eventos</h3>
          <Calendar className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Próximos Eventos</h3>
          <Calendar className="h-5 w-5 text-gray-400" />
        </div>
        <div className="text-center py-8">
          <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 mb-4">Nenhum evento agendado</p>
          <button
            onClick={() => navigate('/calendario/novo')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            Agendar Evento
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Próximos Eventos</h3>
        <div className="flex items-center space-x-2">
          <Calendar className="h-5 w-5 text-gray-400" />
          <button
            onClick={() => navigate('/calendario')}
            className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            Ver todos
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {events.map(event => (
          <div
            key={event.id}
            className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => navigate(`/calendario/editar/${event.id}`)}
          >
            <div className="flex-shrink-0">
              <div className={`w-2 h-8 rounded-full ${eventTypeColors[event.type]}`} />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {event.title}
                </h4>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </div>
              
              <div className="flex items-center space-x-2 mt-1">
                <span className={`text-xs px-2 py-1 rounded-full ${eventTypeColors[event.type]}`}>
                  {eventTypeLabels[event.type as keyof typeof eventTypeLabels]}
                </span>
                <div className="flex items-center text-xs text-gray-500">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatEventDate(event.start_date)}
                </div>
              </div>
              
              {event.location && (
                <div className="flex items-center text-xs text-gray-500 mt-1">
                  <MapPin className="h-3 w-3 mr-1" />
                  <span className="truncate">{event.location}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={() => navigate('/calendario/novo')}
          className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Agendar Novo Evento
        </button>
      </div>
    </div>
  );
}