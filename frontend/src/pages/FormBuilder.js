import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { schemaAPI } from '../services/api';

const FIELD_TYPES = [
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'dropdown', label: 'Dropdown' },
  { value: 'checkbox', label: 'Checkbox' },
];

function FormBuilder({ user, onLogout }) {
  const [schemas, setSchemas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBuilder, setShowBuilder] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    fields: []
  });
  const [newField, setNewField] = useState({
    field_name: '',
    field_label: '',
    field_type: 'text',
    is_required: false,
    display_order: 0
  });

  useEffect(() => {
    loadSchemas();
  }, []);

  const loadSchemas = async () => {
    try {
      const response = await schemaAPI.list();
      setSchemas(response.data);
    } catch (error) {
      console.error('Error loading schemas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddField = () => {
    if (!newField.field_name || !newField.field_label) {
      alert('Please fill field name and label');
      return;
    }
    setFormData({
      ...formData,
      fields: [...formData.fields, { ...newField, display_order: formData.fields.length }]
    });
    setNewField({
      field_name: '',
      field_label: '',
      field_type: 'text',
      is_required: false,
      display_order: 0
    });
  };

  const handleRemoveField = (index) => {
    const updatedFields = formData.fields.filter((_, i) => i !== index);
    setFormData({ ...formData, fields: updatedFields });
  };

  const handleSaveForm = async () => {
    if (!formData.name) {
      alert('Please enter form name');
      return;
    }
    if (formData.fields.length === 0) {
      alert('Please add at least one field');
      return;
    }

    try {
      await schemaAPI.create(formData);
      alert('Form created successfully!');
      setShowBuilder(false);
      setFormData({ name: '', description: '', fields: [] });
      loadSchemas();
    } catch (error) {
      console.error('Error creating form:', error);
      alert('Failed to create form');
    }
  };

  const handleViewSchema = (schema) => {
    setSelectedSchema(schema);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={onLogout} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Form Builder</h1>
            <p className="mt-2 text-gray-600">Create custom forms to extract structured data from documents</p>
          </div>
          <button
            onClick={() => setShowBuilder(!showBuilder)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
            data-testid="create-form-btn"
          >
            {showBuilder ? 'Cancel' : 'Create New Form'}
          </button>
        </div>

        {showBuilder ? (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Build Your Form</h2>
            
            {/* Form Info */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Form Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Invoice Form, ID Card Form"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  data-testid="form-name-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe what this form is used for"
                  rows="2"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  data-testid="form-description-input"
                />
              </div>
            </div>

            {/* Add Field Section */}
            <div className="border-t border-gray-200 pt-6 mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add Fields</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Field Name *</label>
                  <input
                    type="text"
                    value={newField.field_name}
                    onChange={(e) => setNewField({ ...newField, field_name: e.target.value })}
                    placeholder="e.g., invoice_number, customer_name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                    data-testid="field-name-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Field Label *</label>
                  <input
                    type="text"
                    value={newField.field_label}
                    onChange={(e) => setNewField({ ...newField, field_label: e.target.value })}
                    placeholder="e.g., Invoice Number, Customer Name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                    data-testid="field-label-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Field Type</label>
                  <select
                    value={newField.field_type}
                    onChange={(e) => setNewField({ ...newField, field_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                    data-testid="field-type-select"
                  >
                    {FIELD_TYPES.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newField.is_required}
                      onChange={(e) => setNewField({ ...newField, is_required: e.target.checked })}
                      className="mr-2 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      data-testid="field-required-checkbox"
                    />
                    <span className="text-sm font-medium text-gray-700">Required Field</span>
                  </label>
                </div>
              </div>
              <button
                onClick={handleAddField}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                data-testid="add-field-btn"
              >
                + Add Field
              </button>
            </div>

            {/* Fields List */}
            {formData.fields.length > 0 && (
              <div className="border-t border-gray-200 pt-6 mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Form Fields ({formData.fields.length})</h3>
                <div className="space-y-2">
                  {formData.fields.map((field, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                        <div>
                          <p className="font-medium text-gray-900">{field.field_label}</p>
                          <p className="text-sm text-gray-500">
                            {field.field_name} • {field.field_type} {field.is_required && '• Required'}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveField(index)}
                        className="text-red-600 hover:text-red-800"
                        data-testid={`remove-field-${index}`}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="flex space-x-3">
              <button
                onClick={handleSaveForm}
                className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                data-testid="save-form-btn"
              >
                Save Form
              </button>
              <button
                onClick={() => {
                  setShowBuilder(false);
                  setFormData({ name: '', description: '', fields: [] });
                }}
                className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : null}

        {/* Existing Forms */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : schemas.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 mb-4">No forms created yet</p>
            <button
              onClick={() => setShowBuilder(true)}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Create your first form
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schemas.map((schema) => (
              <div key={schema.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{schema.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{schema.description || 'No description'}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">{schema.fields?.length || 0} fields</span>
                  <button
                    onClick={() => handleViewSchema(schema)}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Schema Detail Modal */}
        {selectedSchema && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedSchema(null)}>
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6" onClick={(e) => e.stopPropagation()}>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">{selectedSchema.name}</h2>
              <p className="text-gray-600 mb-6">{selectedSchema.description}</p>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Fields:</h3>
              <div className="space-y-3">
                {selectedSchema.fields?.map((field, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <p className="font-medium text-gray-900">{field.field_label}</p>
                    <p className="text-sm text-gray-500">
                      Name: {field.field_name} • Type: {field.field_type}
                      {field.is_required && ' • Required'}
                    </p>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setSelectedSchema(null)}
                className="mt-6 w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FormBuilder;
