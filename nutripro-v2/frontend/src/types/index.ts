export interface Paciente {
  id: number;
  nome_completo: string;
  email: string;
  telefone?: string;
  data_nascimento?: string;
  peso?: number;
  altura_cm?: number;
  sexo?: 'masculino' | 'feminino';
  observacoes?: string;
  data_cadastro: string;
}

export interface PacienteCreate {
  nome_completo: string;
  email: string;
  telefone?: string;
  data_nascimento?: string;
  peso?: number;
  altura_cm?: number;
  sexo?: 'masculino' | 'feminino';
  observacoes?: string;
}

export interface Alimento {
  id: number;
  nome: string;
  marca?: string;
  kcal_100g: number;
  carboidratos_100g: number;
  proteinas_100g: number;
  gorduras_100g: number;
  origem?: string;
  data_criacao: string;
}

export interface AlimentoCreate {
  nome: string;
  marca?: string;
  kcal_100g: number;
  carboidratos_100g: number;
  proteinas_100g: number;
  gorduras_100g: number;
  origem?: string;
}

export interface CalculoCaloriasRequest {
  peso: number;
  altura: number;
  idade: number;
  sexo: 'masculino' | 'feminino';
  nivel_atividade: 'sedentario' | 'leve' | 'moderado' | 'ativo' | 'extremo';
}

export interface CalculoCaloriasResponse {
  tmb: number;
  calorias_objetivo: number;
  nivel_atividade: string;
  fator_atividade: number;
}

export interface DistribuicaoMacrosRequest {
  total_kcal: number;
  perc_carb: number;
  perc_prot: number;
  perc_gord: number;
  num_refeicoes_grandes: number;
  num_refeicoes_pequenas: number;
}

export interface MacroRefeicao {
  nome: string;
  tipo: 'grande' | 'pequena';
  kcal: number;
  carboidratos_g: number;
  proteinas_g: number;
  gorduras_g: number;
}

export interface DistribuicaoMacrosResponse {
  total_kcal: number;
  total_carboidratos_g: number;
  total_proteinas_g: number;
  total_gorduras_g: number;
  refeicoes: MacroRefeicao[];
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
}