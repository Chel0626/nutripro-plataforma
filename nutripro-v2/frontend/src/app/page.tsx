'use client';

import { useState } from 'react';

export default function HomePage() {
  const [formData, setFormData] = useState({
    peso: '',
    altura: '',
    idade: '',
    sexo: 'masculino',
    nivel_atividade: 'moderado'
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/api/v1/calculos/calorias', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          peso: parseFloat(formData.peso),
          altura: parseFloat(formData.altura),
          idade: parseInt(formData.idade),
          sexo: formData.sexo,
          nivel_atividade: formData.nivel_atividade
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        console.error('Erro na API');
      }
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', padding: '1rem 0' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '32px', height: '32px', backgroundColor: '#10b981', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.125rem' }}>N</span>
            </div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: 0 }}>NutriPro V2</h1>
          </div>
          <nav style={{ display: 'flex', gap: '1.5rem' }}>
            <a href="#" style={{ color: '#6b7280', textDecoration: 'none' }}>Dashboard</a>
            <a href="#" style={{ color: '#6b7280', textDecoration: 'none' }}>Pacientes</a>
            <a href="#" style={{ color: '#6b7280', textDecoration: 'none' }}>Planos</a>
            <a href="#" style={{ color: '#6b7280', textDecoration: 'none' }}>Relatórios</a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
          {/* Calculadora */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937', marginBottom: '1.5rem' }}>Calculadora de Calorias</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.25rem' }}>
                  Peso (kg)
                </label>
                <input
                  type="number"
                  value={formData.peso}
                  onChange={(e) => setFormData({...formData, peso: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
                  placeholder="70"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.25rem' }}>
                  Altura (cm)
                </label>
                <input
                  type="number"
                  value={formData.altura}
                  onChange={(e) => setFormData({...formData, altura: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
                  placeholder="175"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.25rem' }}>
                  Idade
                </label>
                <input
                  type="number"
                  value={formData.idade}
                  onChange={(e) => setFormData({...formData, idade: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
                  placeholder="30"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.25rem' }}>
                  Sexo
                </label>
                <select
                  value={formData.sexo}
                  onChange={(e) => setFormData({...formData, sexo: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
                >
                  <option value="masculino">Masculino</option>
                  <option value="feminino">Feminino</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', color: '#374151', marginBottom: '0.25rem' }}>
                  Nível de Atividade
                </label>
                <select
                  value={formData.nivel_atividade}
                  onChange={(e) => setFormData({...formData, nivel_atividade: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
                >
                  <option value="sedentario">Sedentário</option>
                  <option value="leve">Levemente ativo</option>
                  <option value="moderado">Moderadamente ativo</option>
                  <option value="intenso">Muito ativo</option>
                  <option value="extremo">Extremamente ativo</option>
                </select>
              </div>

              <button
                onClick={handleCalculate}
                disabled={loading}
                style={{ 
                  width: '100%', 
                  backgroundColor: '#10b981', 
                  color: 'white', 
                  fontWeight: '500', 
                  padding: '0.5rem 1rem', 
                  borderRadius: '0.375rem',
                  border: 'none',
                  cursor: 'pointer',
                  opacity: loading ? 0.5 : 1
                }}
              >
                {loading ? 'Calculando...' : 'Calcular Calorias'}
              </button>
            </div>
          </div>

          {/* Resultados */}
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937', marginBottom: '1.5rem' }}>Resultados</h2>
            
            {result ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ backgroundColor: '#dcfce7', border: '1px solid #bbf7d0', borderRadius: '0.5rem', padding: '1rem' }}>
                  <h3 style={{ fontWeight: '600', color: '#166534', marginBottom: '0.5rem' }}>Taxa Metabólica Basal (TMB)</h3>
                  <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#16a34a' }}>{result.tmb?.toFixed(0)} kcal/dia</p>
                </div>
                
                <div style={{ backgroundColor: '#dbeafe', border: '1px solid #bfdbfe', borderRadius: '0.5rem', padding: '1rem' }}>
                  <h3 style={{ fontWeight: '600', color: '#1e40af', marginBottom: '0.5rem' }}>Calorias para Objetivo</h3>
                  <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2563eb' }}>{result.calorias_objetivo?.toFixed(0)} kcal/dia</p>
                  <p style={{ fontSize: '0.875rem', color: '#2563eb', marginTop: '0.25rem' }}>
                    Nível: {result.nivel_atividade} (Fator: {result.fator_atividade})
                  </p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginTop: '1rem' }}>
                  <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
                    <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>Carboidratos</p>
                    <p style={{ fontWeight: '600', color: '#1f2937' }}>50%</p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
                    <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>Proteínas</p>
                    <p style={{ fontWeight: '600', color: '#1f2937' }}>25%</p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '0.75rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
                    <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>Gorduras</p>
                    <p style={{ fontWeight: '600', color: '#1f2937' }}>25%</p>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#6b7280', padding: '2rem 0' }}>
                <p>Preencha os dados e clique em "Calcular" para ver os resultados</p>
              </div>
            )}
          </div>
        </div>

        {/* Status da API */}
        <div style={{ marginTop: '2rem', backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#1f2937', marginBottom: '1rem' }}>Status do Sistema</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '50%' }}></div>
              <span style={{ fontSize: '0.875rem' }}>API FastAPI - Online</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '50%' }}></div>
              <span style={{ fontSize: '0.875rem' }}>Frontend React - Online</span>
            </div>
          </div>
          <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
            NutriPro V2 - Plataforma modernizada com FastAPI + React
          </p>
        </div>
      </main>
    </div>
  );
}