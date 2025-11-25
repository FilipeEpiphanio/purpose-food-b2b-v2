import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ChevronLeft, 
  Save, 
  Calendar,
  Clock,
  MapPin,
  FileText,
  Tag,
  DollarSign,
  Users,
  RefreshCw
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { toast } from 'sonner';
import moment from 'moment';

interface EventFormData {
  title: string;
  type: 'feira' | 'evento' | 'compromisso' | 'entrega' | 'reuniao';
  description: string;
  start_date: string;
  end_date: string;
  location: string;
  notes: string;
  budget?: number;
  attendees?: string;
  sync_to_google: boolean;
}

const eventTypes = [
  { value: 'feira', label: 'Feira', icon: '🏪' },
  { value: 'evento', label: 'Evento', icon: '🎉' },
  { value: 'compromisso', label: 'Compromisso', icon: '📅' },
  { value: 'entrega', label: 'Entrega', icon: '📦' },
  { value: 'reuniao', label: 'Reunião', icon: '👥' }
];

export default function EventForm() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { id } = useParams<{ id?: string }>();
  const isEditing = !!id;
  
  const [formData, setFormData] = useState<EventFormData>({
    title: '',
    type: 'feira',
    description: '',
    start_date: moment().format('YYYY-MM-DDTHH:mm'),
    end_date: moment().add(1, 'hour').format('YYYY-MM-DDTHH:mm'),
    location: '',
    notes: '',
    budget: undefined,
    attendees: '',
    sync_to_google: true
  });
  
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    if (isEditing) {
      loadEvent();
    }
  }, [id]);

  const loadEvent = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/calendar/events/${id}`, {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      });

      if (!response.ok) {
        throw new Error('Erro ao carregar evento');
      }

      const event = await response.json();
      setFormData({
        title: event.title,
        type: event.type,
        description: event.description || '',
        start_date: moment(event.start_date).format('YYYY-MM-DDTHH:mm'),
        end_date: moment(event.end_date).format('YYYY-MM-DDTHH:mm'),
        location: event.location || '',
        notes: event.notes || '',
        budget: event.budget || undefined,
        attendees: event.attendees || '',
        sync_to_google: event.sync_status !== 'not_synced'
      });
    } catch (error) {
      console.error('Erro ao carregar evento:', error);
      toast.error('Erro ao carregar evento');
      navigate('/calendar');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Validate dates
      if (moment(formData.start_date).isAfter(formData.end_date)) {
        toast.error('A data de início deve ser anterior à data de término');
        return;
      }

      const url = isEditing ? `/api/calendar/events/${id}` : '/api/calendar/events';
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`
        },
        body: JSON.stringify({
          ...formData,
          user_id: user?.id
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Erro desconhecido' }));
        throw new Error(`Erro ao ${isEditing ? 'atualizar' : 'criar'} evento: ${errorData.error || errorData.message || 'Erro desconhecido'}`);
      }

      const result = await response.json();
      
      // Sync with Google if requested
      if (formData.sync_to_google && result.id) {
        await syncWithGoogle(result.id);
      }

      toast.success(`Evento ${isEditing ? 'atualizado' : 'criado'} com sucesso!`);
      navigate('/calendar');
    } catch (error) {
      console.error('Erro ao salvar evento:', error);
      toast.error(`Erro ao ${isEditing ? 'atualizar' : 'criar'} evento`);
    } finally {
      setLoading(false);
    }
  };

  const syncWithGoogle = async (eventId: string) => {
    try {
      setSyncing(true);
      
      const response = await fetch(`/api/calendar/sync/to-google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`
        },
        body: JSON.stringify({ eventIds: [eventId] })
      });

      if (!response.ok) {
        throw new Error('Erro ao sincronizar com Google Calendar');
      }

      toast.success('Evento sincronizado com Google Calendar');
    } catch (error) {
      console.error('Erro na sincronização:', error);
      toast.error('Erro ao sincronizar com Google Calendar');
    } finally {
      setSyncing(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else if (name === 'budget') {
      setFormData(prev => ({ ...prev, [name]: value ? parseFloat(value) : undefined }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const setDuration = (hours: number) => {
    const start = moment(formData.start_date);
    const end = start.clone().add(hours, 'hours');
    setFormData(prev => ({
      ...prev,
      end_date: end.format('YYYY-MM-DDTHH:mm')
    }));
  };

  if (loading && isEditing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <h1 className="text-xl font-bold text-gray-900">
                {isEditing ? 'Editar Evento' : 'Novo Evento'}
              </h1>
            </div>
            <button
              onClick={handleSubmit}
              disabled={loading || syncing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{loading ? 'Salvando...' : 'Salvar'}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(e);
        }} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Informações Básicas</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Event Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Tag className="inline h-4 w-4 mr-1" />
                  Tipo de Evento
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  {eventTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Título do Evento
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Feira da Praça Central"
                  required
                />
              </div>
            </div>

            {/* Description */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <FileText className="inline h-4 w-4 mr-1" />
                Descrição
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Descreva os detalhes do evento..."
              />
            </div>
          </div>

          {/* Date and Time */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Data e Hora</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Data de Início
                </label>
                <input
                  type="datetime-local"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              {/* End Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="inline h-4 w-4 mr-1" />
                  Data de Término
                </label>
                <input
                  type="datetime-local"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            {/* Quick Duration Buttons */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duração Rápida
              </label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 6, 8].map(hours => (
                  <button
                    key={hours}
                    type="button"
                    onClick={() => setDuration(hours)}
                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    {hours}h
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Location and Details */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Localização e Detalhes</h2>
            
            <div className="space-y-4">
              {/* Location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="inline h-4 w-4 mr-1" />
                  Localização
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Praça Central, Rua das Flores, 123"
                />
              </div>

              {/* Budget */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <DollarSign className="inline h-4 w-4 mr-1" />
                  Orçamento Estimado (R$)
                </label>
                <input
                  type="number"
                  name="budget"
                  value={formData.budget?.toString() || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                />
              </div>

              {/* Attendees */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Users className="inline h-4 w-4 mr-1" />
                  Participantes
                </label>
                <input
                  type="text"
                  name="attendees"
                  value={formData.attendees}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Nome dos participantes, separados por vírgula"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observações
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Observações adicionais..."
                />
              </div>
            </div>
          </div>

          {/* Google Calendar Sync */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Sincronização</h2>
            
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="sync_to_google"
                name="sync_to_google"
                checked={formData.sync_to_google}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="sync_to_google" className="text-sm font-medium text-gray-700">
                <RefreshCw className="inline h-4 w-4 mr-1" />
                Sincronizar com Google Calendar
              </label>
            </div>
            
            <p className="text-xs text-gray-500 mt-2">
              Ao marcar esta opção, o evento será sincronizado com seu Google Calendar
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || syncing}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{loading ? 'Salvando...' : 'Salvar Evento'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}