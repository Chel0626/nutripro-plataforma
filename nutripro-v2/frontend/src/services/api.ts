import { api } from '@/lib/api';
import {
  Paciente,
  PacienteCreate,
  Alimento,
  AlimentoCreate,
  CalculoCaloriasRequest,
  CalculoCaloriasResponse,
  DistribuicaoMacrosRequest,
  DistribuicaoMacrosResponse,
} from '@/types';

export const pacientesService = {
  async getAll(params?: { skip?: number; limit?: number; search?: string }) {
    const response = await api.get<Paciente[]>('/pacientes', { params });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get<Paciente>(`/pacientes/${id}`);
    return response.data;
  },

  async create(data: PacienteCreate) {
    const response = await api.post<Paciente>('/pacientes', data);
    return response.data;
  },

  async update(id: number, data: Partial<PacienteCreate>) {
    const response = await api.put<Paciente>(`/pacientes/${id}`, data);
    return response.data;
  },

  async delete(id: number) {
    const response = await api.delete(`/pacientes/${id}`);
    return response.data;
  },
};

export const alimentosService = {
  async getAll(params?: { skip?: number; limit?: number; search?: string; origem?: string }) {
    const response = await api.get<Alimento[]>('/alimentos', { params });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get<Alimento>(`/alimentos/${id}`);
    return response.data;
  },

  async autocomplete(q: string, limit = 10) {
    const response = await api.get<Alimento[]>('/alimentos/autocomplete', {
      params: { q, limit },
    });
    return response.data;
  },

  async create(data: AlimentoCreate) {
    const response = await api.post<Alimento>('/alimentos', data);
    return response.data;
  },

  async update(id: number, data: Partial<AlimentoCreate>) {
    const response = await api.put<Alimento>(`/alimentos/${id}`, data);
    return response.data;
  },

  async delete(id: number) {
    const response = await api.delete(`/alimentos/${id}`);
    return response.data;
  },
};

export const calculosService = {
  async calcularCalorias(data: CalculoCaloriasRequest) {
    const response = await api.post<CalculoCaloriasResponse>('/calculos/calorias', data);
    return response.data;
  },

  async distribuirMacros(data: DistribuicaoMacrosRequest) {
    const response = await api.post<DistribuicaoMacrosResponse>('/calculos/distribuicao-macros', data);
    return response.data;
  },

  async calcularTMB(peso: number, altura: number, idade: number, sexo: string) {
    const response = await api.get('/calculos/tmb', {
      params: { peso, altura, idade, sexo },
    });
    return response.data;
  },
};