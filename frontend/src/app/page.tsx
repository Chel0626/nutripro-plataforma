import React from "react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-green-100 to-blue-100 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8 flex flex-col items-center">
        <h1 className="text-3xl font-bold mb-4 text-center text-green-700">
          NutriPro Plataforma
        </h1>
        <p className="text-gray-600 text-center mb-6">
          Bem-vindo! Faça login para acessar seu painel nutricional.
        </p>
        <a
          href="/login"
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded transition text-center"
        >
          Entrar
        </a>
      </div>
    </main>
  );
}
