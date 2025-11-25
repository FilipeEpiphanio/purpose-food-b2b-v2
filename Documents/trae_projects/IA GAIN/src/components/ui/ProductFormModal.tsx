import React, { useState, useEffect } from 'react';
import { X, Save, Plus, Upload, Image as ImageIcon } from 'lucide-react';

export interface ProductFormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'textarea' | 'currency' | 'file' | 'toggle' | 'ingredients';
  required?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
}

interface ProductFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any, action: 'save-exit' | 'save-new') => void;
  title: string;
  fields: ProductFormField[];
  initialData?: any;
}

export default function ProductFormModal({
  isOpen,
  onClose,
  onSubmit,
  title,
  fields,
  initialData
}: ProductFormModalProps) {
  const [formData, setFormData] = useState<any>({});
  const [imagePreview, setImagePreview] = useState<string>('');
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [newIngredient, setNewIngredient] = useState('');

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
      setImagePreview(initialData.image_url || '');
      
      // Garantir que ingredients seja sempre um array
      let ingredientsArray = [];
      if (initialData.ingredients) {
        if (Array.isArray(initialData.ingredients)) {
          ingredientsArray = initialData.ingredients;
        } else if (typeof initialData.ingredients === 'string') {
          try {
            ingredientsArray = JSON.parse(initialData.ingredients);
          } catch (e) {
            console.warn('Erro ao fazer parse dos ingredients:', e);
            ingredientsArray = [];
          }
        }
      }
      setIngredients(ingredientsArray);
    } else {
      const initialFormData: any = {};
      fields.forEach(field => {
        if (field.type === 'toggle') {
          initialFormData[field.name] = true;
        } else if (field.type === 'ingredients') {
          initialFormData[field.name] = [];
        } else {
          initialFormData[field.name] = '';
        }
      });
      setFormData(initialFormData);
      setIngredients([]);
      setImagePreview('');
    }
  }, [initialData, fields, isOpen]);

  const handleInputChange = (name: string, value: any) => {
    setFormData((prev: any) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageUrl = e.target?.result as string;
        setImagePreview(imageUrl);
        handleInputChange('image_url', imageUrl);
      };
      reader.readAsDataURL(file);
    }
  };

  const addIngredient = () => {
    if (newIngredient.trim()) {
      setIngredients([...ingredients, newIngredient.trim()]);
      setNewIngredient('');
    }
  };

  const removeIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleSubmit = (action: 'save-exit' | 'save-new') => {
    const dataToSubmit = {
      ...formData,
      ingredients: ingredients,
      status: formData.status || (formData.is_active ? 'active' : 'inactive')
    };
    
    onSubmit(dataToSubmit, action);
    
    if (action === 'save-exit') {
      onClose();
    } else {
      // Reset form for new product
      const resetFormData: any = {};
      fields.forEach(field => {
        if (field.type === 'toggle') {
          resetFormData[field.name] = true;
        } else if (field.type === 'ingredients') {
          resetFormData[field.name] = [];
        } else {
          resetFormData[field.name] = '';
        }
      });
      setFormData(resetFormData);
      setIngredients([]);
      setImagePreview('');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={(e) => {
          e.preventDefault();
          handleSubmit('save-exit');
        }} className="p-6">
          {/* Image Upload Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Imagem do Produto
            </label>
            <div className="flex items-center space-x-4">
              <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                {imagePreview ? (
                  <img src={imagePreview} alt="Preview" className="w-full h-full object-cover rounded-lg" />
                ) : (
                  <ImageIcon className="w-12 h-12 text-gray-400" />
                )}
              </div>
              <div>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="product-image-upload"
                />
                <label
                  htmlFor="product-image-upload"
                  className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 cursor-pointer"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Escolher Imagem
                </label>
              </div>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {fields.map((field) => {
              if (field.type === 'ingredients') {
                return (
                  <div key={field.name} className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    <div className="space-y-2">
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={newIngredient}
                          onChange={(e) => setNewIngredient(e.target.value)}
                          placeholder={field.placeholder || "Digite um ingrediente"}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                          onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addIngredient())}
                        />
                        <button
                          type="button"
                          onClick={addIngredient}
                          className="px-3 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {ingredients.map((ingredient, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800"
                          >
                            {ingredient}
                            <button
                              type="button"
                              onClick={() => removeIngredient(index)}
                              className="ml-2 text-orange-600 hover:text-orange-800"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              }

              if (field.type === 'toggle') {
                return (
                  <div key={field.name} className="md:col-span-2">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          {field.label}
                        </label>
                        <p className="text-sm text-gray-500">Produto disponível para venda</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleInputChange(field.name, !formData[field.name])}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          formData[field.name] ? 'bg-orange-500' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            formData[field.name] ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                );
              }

              return (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  
                  {field.type === 'select' && (
                    <select
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      required={field.required}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                    >
                      <option value="">Selecione...</option>
                      {field.options?.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  )}

                  {field.type === 'textarea' && (
                    <textarea
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      required={field.required}
                      placeholder={field.placeholder}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                    />
                  )}

                  {field.type === 'currency' && (
                    <input
                      type="number"
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleInputChange(field.name, parseFloat(e.target.value))}
                      required={field.required}
                      placeholder={field.placeholder}
                      step="0.01"
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                    />
                  )}

                  {(field.type === 'text' || field.type === 'number' || field.type === 'file') && (
                    <input
                      type={field.type}
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      required={field.required}
                      placeholder={field.placeholder}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => handleSubmit('save-new')}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              <Save className="h-4 w-4 mr-2" />
              Salvar e Novo
            </button>
            <button
              type="button"
              onClick={() => handleSubmit('save-exit')}
              className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <Save className="h-4 w-4 mr-2" />
              Salvar e Sair
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}